from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_current_active_user
from app.db.session import get_db
from app.models.label import Label
from app.models.task import Task
from app.models.user import User
from app.schemas.label import LabelCreate, LabelOut

router = APIRouter()
task_labels_router = APIRouter()


@router.post("", response_model=LabelOut, status_code=status.HTTP_201_CREATED)
def create_label(
    payload: LabelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if db.query(Label).filter(Label.name == payload.name).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Label already exists")
    label = Label(name=payload.name)
    db.add(label)
    db.commit()
    db.refresh(label)
    return label


@router.get("", response_model=List[LabelOut])
def list_labels(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return db.query(Label).order_by(Label.name).all()


@task_labels_router.post("/{task_id}/labels/{label_id}", response_model=List[LabelOut])
def add_label_to_task(
    task_id: int,
    label_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    label = db.query(Label).filter(Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")
    if label not in task.labels:
        task.labels.append(label)
        db.commit()
    return task.labels


@task_labels_router.delete("/{task_id}/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_label_from_task(
    task_id: int,
    label_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    label = db.query(Label).filter(Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")
    if label in task.labels:
        task.labels.remove(label)
        db.commit()


@task_labels_router.get("/{task_id}/labels", response_model=List[LabelOut])
def get_task_labels(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task.labels
