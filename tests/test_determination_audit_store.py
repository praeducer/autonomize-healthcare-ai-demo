"""Unit tests for the SQLite audit store.

Validates append-only audit trail for PA determinations.
All tests use a temp file — no external services needed.
"""

import pytest

pytestmark = pytest.mark.unit


class TestAuditStoreInit:
    async def test_init_creates_database_file(self, tmp_path) -> None:
        """Calling init_db should create a SQLite file and determinations table."""
        from prior_auth_demo.determination_audit_store import DeterminationAuditStore

        db_path = tmp_path / "test_audit.db"
        store = DeterminationAuditStore(db_path=str(db_path))
        await store.init_db()
        assert db_path.exists()
        await store.close()


class TestStoreDetermination:
    async def test_store_and_retrieve_by_id(self, tmp_path) -> None:
        """Stored determination should be retrievable by its UUID."""
        from prior_auth_demo.determination_audit_store import DeterminationAuditStore

        store = DeterminationAuditStore(db_path=str(tmp_path / "test.db"))
        await store.init_db()
        det_id = await store.store_determination(
            case_name="01_lumbar_mri_clear_approval.json",
            determination="APPROVED",
            confidence_score=0.92,
            clinical_rationale="Meets medical necessity.",
            guideline_citations=["CMS LCD L35028"],
            processing_time_seconds=12.5,
            full_request_json='{"resourceType": "Bundle"}',
            full_response_json='{"determination": "APPROVED"}',
        )
        assert det_id is not None
        result = await store.get_determination(det_id)
        assert result is not None
        assert result["determination"] == "APPROVED"
        assert result["confidence_score"] == 0.92
        assert result["case_name"] == "01_lumbar_mri_clear_approval.json"
        await store.close()


class TestListDeterminations:
    async def test_list_returns_stored_results(self, tmp_path) -> None:
        """list_determinations returns all stored determinations, newest first."""
        from prior_auth_demo.determination_audit_store import DeterminationAuditStore

        store = DeterminationAuditStore(db_path=str(tmp_path / "test.db"))
        await store.init_db()
        await store.store_determination(
            case_name="case_a.json",
            determination="APPROVED",
            confidence_score=0.9,
            clinical_rationale="Good",
            guideline_citations=["ref1"],
            processing_time_seconds=10.0,
            full_request_json="{}",
            full_response_json="{}",
        )
        await store.store_determination(
            case_name="case_b.json",
            determination="DENIED",
            confidence_score=0.95,
            clinical_rationale="Bad",
            guideline_citations=["ref2"],
            processing_time_seconds=11.0,
            full_request_json="{}",
            full_response_json="{}",
        )
        results = await store.list_determinations()
        assert len(results) == 2
        # Newest first
        assert results[0]["case_name"] == "case_b.json"
        await store.close()

    async def test_list_supports_pagination(self, tmp_path) -> None:
        """limit and offset parameters work correctly."""
        from prior_auth_demo.determination_audit_store import DeterminationAuditStore

        store = DeterminationAuditStore(db_path=str(tmp_path / "test.db"))
        await store.init_db()
        for i in range(5):
            await store.store_determination(
                case_name=f"case_{i}.json",
                determination="APPROVED",
                confidence_score=0.9,
                clinical_rationale="test",
                guideline_citations=[],
                processing_time_seconds=1.0,
                full_request_json="{}",
                full_response_json="{}",
            )
        page1 = await store.list_determinations(limit=2, offset=0)
        page2 = await store.list_determinations(limit=2, offset=2)
        assert len(page1) == 2
        assert len(page2) == 2
        assert page1[0]["case_name"] != page2[0]["case_name"]
        await store.close()


class TestAppendOnly:
    def test_no_update_or_delete_methods(self) -> None:
        """DeterminationAuditStore must NOT have update or delete methods."""
        from prior_auth_demo.determination_audit_store import DeterminationAuditStore

        assert not hasattr(DeterminationAuditStore, "update_determination")
        assert not hasattr(DeterminationAuditStore, "delete_determination")
        assert not hasattr(DeterminationAuditStore, "update")
        assert not hasattr(DeterminationAuditStore, "delete")
