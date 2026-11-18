from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes import api
from app.views import assets, index

app = FastAPI(title="Radivela")


@app.exception_handler(RequestValidationError)
async def validation_error(_request: Request, error: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": [
            {"loc": item["loc"], "msg": item["msg"]} for item in error.errors()
        ]},
    )


@app.get("/api/v1/salud")
def salud():
    return {"estado": "disponible"}


app.include_router(api)

app.add_api_route("/", index, include_in_schema=False)
app.mount("/assets", assets, name="assets")
