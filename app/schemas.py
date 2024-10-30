from pydantic import BaseModel


class CreateUser(BaseModel):
    username: str
    firstname: str
    lastname: str
    age: int
    id: int


class UpdateUser(BaseModel):
    username: str
    firstname: str
    lastname: str
    age: int


class CreateTask(BaseModel):
    title: str
    content: str
    priority: int



class UpdateTask(BaseModel):
    title: str
    content: str
    priority: int

