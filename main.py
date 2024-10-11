from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.recommender import recommender_router
from routers.position import position_router
from routers.portfolio import portfolio_router
from routers.stock import stock_router
from routers.user import user_router
import uvicorn


origins = [
    "*",
]

app = FastAPI(title="EmporIO", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommender_router)
app.include_router(position_router)
app.include_router(portfolio_router)
app.include_router(stock_router)
app.include_router(user_router)


@app.get("/")
async def root():
    return {"message": "Hello World!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=1)
