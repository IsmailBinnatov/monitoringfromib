from fastapi import FastAPI, Request
from app.logs.logger import logger
import time


async def modify_request_response_middleware(request: Request, call_next):
    if request.url.path in ["/docs", "/openapi.json", "/favicon.ico"]:
        return await call_next(request)

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    operation_name = f"{request.method} {request.url.path}"
    logger.info(
        f"Request time of {operation_name}: {process_time:.4f} seconds")

    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response
