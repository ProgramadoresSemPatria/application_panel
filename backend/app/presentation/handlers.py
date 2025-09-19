from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core import exceptions


async def _resource_not_found_handler(
        request: Request, exc: exceptions.ResourceNotFound):
    return JSONResponse(status_code=404, content={"detail": exc.message})


async def _resource_conflict_handler(
        request: Request, exc: exceptions.ResourceNotFound):
    return JSONResponse(status_code=409, content={"detail": exc.message})


def register_handlers(app: FastAPI):
    """Register all errors handlers for the app"""
    app.add_exception_handler(
        exceptions.ResourceNotFound, _resource_not_found_handler)
    app.add_exception_handler(
        exceptions.ResourceConflict, _resource_conflict_handler)
