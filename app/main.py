from fastapi import FastAPI


app = FastAPI(title="API Price Monitoring")


@app.get("/")
async def root():
    return {"status": "ok", "message": "Сервер запущен, ждем базу данных!"}
