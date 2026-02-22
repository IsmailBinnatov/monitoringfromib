from fastapi import FastAPI

from app.routers.product import router as product_router


app = FastAPI(
    title="API Price Monitoring",
    description="API for tracking prices of Apple devices",
    version="0.1.0"
)


app.include_router(product_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Apple Price Monitor API! Go to /docs for Swagger"}
