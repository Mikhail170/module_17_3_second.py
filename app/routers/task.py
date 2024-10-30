
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models.task import Task
from app.models.user import User
from app.schemas import CreateTask, UpdateTask
from sqlalchemy import select, insert, update, delete


router_task = APIRouter(prefix='/task', tags=['task'])


@router_task.get('/')
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task)).all()
    return tasks


@router_task.get('/{task_id}')
async def task_by_id(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not found")
    return task


@router_task.post('/create')
async def create_task(
        db: Annotated[Session, Depends(get_db)],
        task_create_model: CreateTask,
        user_id: int  # Добавляем user_id для связи с пользователем
):
    # Проверяем, существует ли пользователь
    existing_user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if existing_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    # Создаём запись задачи
    db.execute(insert(Task).values(
        title=task_create_model.title,
        content=task_create_model.content,
        priority=task_create_model.priority,
        user_id=user_id
        ))
    db.commit()

    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router_task.put('/update/{task_id}')
async def update_task(
        task_id: int,
        task_update_model: UpdateTask,
        db: Annotated[Session, Depends(get_db)],
):
    existing_task = db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()

    if existing_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not found")

    db.execute(
        update(Task).where(Task.id == task_id).values(
            title=task_update_model.title,
            content=task_update_model.content,
            priority=task_update_model.priority,
            )
    )

    db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task update is successful!'
    }


@router_task.delete('/delete/{task_id}')
async def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    del_user = delete(Task).where(Task.id == task_id)
    result = db.execute(del_user)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not found")
    return {'status_code': status.HTTP_200_OK, 'transaction': 'Task successfully deleted!'}



