from fastapi import APIRouter
from app.api.v1.endpoints import auth, tasks, users, comments, labels

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(comments.router, prefix="/tasks", tags=["comments"])
api_router.include_router(labels.router, prefix="/labels", tags=["labels"])
api_router.include_router(labels.task_labels_router, prefix="/tasks", tags=["task-labels"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
