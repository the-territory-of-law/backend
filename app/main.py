from fastapi import FastAPI


app = FastAPI(title="Backend service")


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
