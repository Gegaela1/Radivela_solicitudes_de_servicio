from fastapi import APIRouter, FastAPI

app = FastAPI(title="Radivela")
api = APIRouter(prefix="/api/v1")


@api.get("/salud")
def salud():
    return {"estado": "disponible"}


app.include_router(api)
