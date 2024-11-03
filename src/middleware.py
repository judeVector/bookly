import time
import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse


logger = logging.getLogger("uvicorn.access")
logger.disabled = True  # Turn to False to see FastAPI server logs


def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)
        processing_time = time.time() - start_time

        message = f"{request.client.host}:{request.client.host} - {request.method} - {request.url.path} - completed after {round(processing_time, 5)}"
        print(message)

        return response

    # @app.middleware("http")
    # async def authorization(request: Request, call_next):
    #     if not "Authorization" in request.headers:
    #         return JSONResponse(
    #             content={
    #                 "message": "Not Authenticated",
    #                 "resolution": "Please provide the right credentials to proceed",
    #             },
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #         )

    #     response = await call_next(request)
    #     return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])
