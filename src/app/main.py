from fastapi import FastAPI

from app.config import get_settings

settings = get_settings()

app = FastAPI(title="LearnLoop Agent")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
