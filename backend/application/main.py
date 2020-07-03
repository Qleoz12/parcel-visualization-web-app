import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from application.routes import map, orders, compare, autonomous, settings

app = FastAPI()

# This makes it possible to access the api at /map/...
app.include_router(map.router, prefix='/map')
app.include_router(orders.router, prefix='/orders')
app.include_router(compare.router, prefix='/compare')
app.include_router(settings.router, prefix='/settings')
app.include_router(autonomous.router, prefix='/autonomous')

origins = ["http://localhost:8080", "http://127.0.0.1:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)