from fastapi import FastAPI

app = FastAPI(title="minilink")

@app.get("/health")
def health():
    return {"status": "ok"}