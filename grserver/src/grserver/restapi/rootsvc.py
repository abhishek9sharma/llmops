from fastapi import FastAPI
from src.grserver.restapi.routers import grrouterasync, grroutersync

app = FastAPI()


@app.get("/")
def start_svc():
    return {"Info": "GR Service is running"}


app.include_router(grrouterasync.router, prefix="/grserver_async")
app.include_router(grroutersync.router, prefix="/grserver_sync")
