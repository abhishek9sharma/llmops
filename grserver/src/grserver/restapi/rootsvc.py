from fastapi import FastAPI

from grserver.core.guards import guard_map
from grserver.restapi.routers import grroutersync

app = FastAPI()


@app.get("/")
def start_svc():
    return {"Info": "GR Service is running"}


@app.get("/available_guards")
def available_guards():
    return guard_map


# app.include_router(grrouterasync.router, prefix="/guarded_async")
app.include_router(grroutersync.router, prefix="/guarded_sync")
print("HI")
