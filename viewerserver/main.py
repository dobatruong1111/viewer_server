import uvicorn
import os
import time

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .module.coupons import router as coupon_router
from .module.client import router as client_router
from .module.wado import router as wado_router
from .config.settings import settings

from .config.session import engine
from .db.model.base_model import Base

import asyncio

import os
from dotenv import load_dotenv
load_dotenv(verbose=True)

os.environ["TZ"] = settings.TIMEZONE
# time.tzset()


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.TITLE,
        description=settings.DESCRIPTION,
        debug=settings.DEBUG,
        # docs_url=None,
        # redoc_url=None,
        # openapi_url=None,
    )
    application.include_router(coupon_router, prefix=settings.API_V1_STR)
    application.include_router(client_router, prefix=settings.API_V1_STR)
    application.include_router(wado_router)
    application.mount("/viewer", StaticFiles(directory="saola-dicom-viewer/build"), name="viewer")
    return application


async def periodic():
    while True:
        # code to run periodically starts here
        print(os.getpid())
        # code to run periodically ends here
        # sleep for 3 seconds after running above code
        await asyncio.sleep(3)

app = get_application()

@app.on_event("startup")
async def schedule_periodic():
    print("APP Starting up....")
    # Auto-create Database Schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Run loop event periodically
    # loop = asyncio.get_event_loop()
    # loop.create_task(periodic())


@app.get("/")
def main():
    return {"status": "ok"}

# if __name__ == "__main__":
#     """Launched with `poetry run start` at root level"""
#     port_2dserver = os.getenv('PORT_2DSERVER', 8000)
#     uvicorn.run("viewerserver.main:app", host='0.0.0.0', port=port_2dserver, reload=True)