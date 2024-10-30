from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models.user import User
from app.models.task import Task
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify


router_user = APIRouter(prefix='/user', tags=['user'])


@router_user.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router_user.get('/{user_id}')
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")
    return user


@router_user.get('/{user_id}/tasks')  # Новый маршрут для получения задач пользователя по ID
async def tasks_by_user_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    tasks = db.scalars(select(Task).where(Task.user_id == user_id)).all()  # Получаем все задачи пользователя
    return tasks


@router_user.post('/create')
async def create_user(
        db: Annotated[Session, Depends(get_db)],
        user_create_model: CreateUser,
):
    db.execute(insert(User).values(username=user_create_model.username,
                                   firstname=user_create_model.firstname,
                                   lastname=user_create_model.lastname,
                                   age=user_create_model.age,
                                   slug=slugify(user_create_model.username)))
    db.commit()

    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router_user.put('/update/{user_id}')
async def update_user(
        user_id: int,
        user_update_model: UpdateUser,
        db: Annotated[Session, Depends(get_db)],
):
    existing_user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

    if existing_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    db.execute(
        update(User).where(User.id == user_id).values(
            username=user_update_model.username,
            firstname=user_update_model.firstname,
            lastname=user_update_model.lastname,
            age=user_update_model.age,
            slug=slugify(user_update_model.username)
        )
    )

    db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User update is successful!'
    }


@router_user.delete('/delete/{user_id}')
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    # Сначала удаляем все задачи, связанные с пользователем
    db.execute(delete(Task).where(Task.user_id == user_id))

    # Затем удаляем пользователя
    del_user = delete(User).where(User.id == user_id)
    result = db.execute(del_user)
    db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User successfully deleted!'
    }
