"""Append-only SQLite audit store for PA determinations.

Every determination is recorded with full request/response data.
No update or delete operations exist by design.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import aiosqlite

logger = logging.getLogger(__name__)

_DEFAULT_DB_PATH = str(Path(__file__).resolve().parent.parent.parent / "data" / "audit_trail.db")


class DeterminationAuditStore:
    """Async SQLite audit store — append-only."""

    def __init__(self, db_path: str = _DEFAULT_DB_PATH) -> None:
        self._db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def init_db(self) -> None:
        """Create the database file and determinations table if they don't exist."""
        self._db = await aiosqlite.connect(self._db_path)
        self._db.row_factory = aiosqlite.Row
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS determinations (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                case_name TEXT,
                determination TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                clinical_rationale TEXT NOT NULL,
                guideline_citations TEXT NOT NULL,
                processing_time_seconds REAL NOT NULL,
                full_request_json TEXT NOT NULL,
                full_response_json TEXT NOT NULL
            )
        """)
        await self._db.commit()

    async def store_determination(
        self,
        case_name: str | None,
        determination: str,
        confidence_score: float,
        clinical_rationale: str,
        guideline_citations: list[str],
        processing_time_seconds: float,
        full_request_json: str,
        full_response_json: str,
    ) -> str:
        """Store a new determination record and return its UUID."""
        if self._db is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        det_id = str(uuid.uuid4())
        created_at = datetime.now(UTC).isoformat()
        await self._db.execute(
            """INSERT INTO determinations
               (id, created_at, case_name, determination, confidence_score,
                clinical_rationale, guideline_citations, processing_time_seconds,
                full_request_json, full_response_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                det_id,
                created_at,
                case_name,
                determination,
                confidence_score,
                clinical_rationale,
                json.dumps(guideline_citations),
                processing_time_seconds,
                full_request_json,
                full_response_json,
            ),
        )
        await self._db.commit()
        logger.info("Stored determination %s for case %s: %s", det_id, case_name, determination)
        return det_id

    async def get_determination(self, det_id: str) -> dict[str, Any] | None:
        """Retrieve a single determination by its UUID."""
        if self._db is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        cursor = await self._db.execute("SELECT * FROM determinations WHERE id = ?", (det_id,))
        row = await cursor.fetchone()
        if row is None:
            return None
        result = dict(row)
        result["guideline_citations"] = json.loads(result["guideline_citations"])
        return result

    async def list_determinations(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        """List determinations ordered newest first, with pagination."""
        if self._db is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        cursor = await self._db.execute(
            "SELECT * FROM determinations ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        rows = await cursor.fetchall()
        results = []
        for row in rows:
            d = dict(row)
            d["guideline_citations"] = json.loads(d["guideline_citations"])
            results.append(d)
        return results

    async def close(self) -> None:
        """Close the database connection."""
        if self._db:
            await self._db.close()
            self._db = None
