from fastapi import FastAPI
from grserver.restapi.routers import grrouterasync

app = FastAPI()


@app.get("/")
def start_svc():
    return {"Info": "GR Service is running"}


app.include_router(grrouterasync.router, prefix="/guarded")


# import uvicorn
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8004)