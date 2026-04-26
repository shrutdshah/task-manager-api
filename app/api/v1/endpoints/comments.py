from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_current_active_user
from app.db.session import get_db
from app.models.comment import Comment
from app.models.task import Task
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentOut, CommentUpdate

router = APIRouter()


def _get_task_or_404(task_id: int, db: Session, current_user: User) -> Task:
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("/{task_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(
    task_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _get_task_or_404(task_id, db, current_user)
    comment = Comment(body=payload.body, task_id=task_id, author_id=current_user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/{task_id}/comments", response_model=List[CommentOut])
def list_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _get_task_or_404(task_id, db, current_user)
    return db.query(Comment).filter(Comment.task_id == task_id).order_by(Comment.created_at).all()


@router.patch("/{task_id}/comments/{comment_id}", response_model=CommentOut)
def update_comment(
    task_id: int,
    comment_id: int,
    payload: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _get_task_or_404(task_id, db, current_user)
    comment = db.query(Comment).filter(
        Comment.id == comment_id, Comment.task_id == task_id
    ).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")
    comment.body = payload.body
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{task_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    task_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _get_task_or_404(task_id, db, current_user)
    comment = db.query(Comment).filter(
        Comment.id == comment_id, Comment.task_id == task_id
    ).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")
    db.delete(comment)
    db.commit()
