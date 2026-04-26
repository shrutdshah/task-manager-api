from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, func
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    due_date = Column(DateTime(timezone=True))
    is_archived = Column(Boolean, default=False)

    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="tasks", foreign_keys=[owner_id])

    # Assignee (nullable — task may be unassigned)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assignee = relationship("User", foreign_keys=[assignee_id])

    # Jira integration
    jira_ticket_id = Column(String(50), index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
