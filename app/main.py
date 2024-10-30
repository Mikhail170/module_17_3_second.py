from fastapi import FastAPI
from app.routers import router_user, router_task


app = FastAPI()


@app.get('/')
async def welcome():
    return {"message": "Welcome to Taskmanager"}

app.include_router(router_user)
app.include_router(router_task)

