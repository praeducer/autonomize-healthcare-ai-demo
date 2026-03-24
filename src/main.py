"""FastAPI application entry point."""

from fastapi import FastAPI

app = FastAPI(
    title="AI-Driven Prior Authorization Demo",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
