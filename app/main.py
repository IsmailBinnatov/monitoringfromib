from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.pages.routers import router as product_router
from app.api.routers.product import router as api_router


app = FastAPI(
    title="API Price Monitoring",
    description="API for tracking prices of Apple devices",
    version="0.1.0"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.include_router(product_router)
app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Apple Price Monitor API! Go to /docs for Swagger"}
