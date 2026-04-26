from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

task_labels = Table(
    "task_labels",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("label_id", Integer, ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True),
)


class Label(Base):
    __tablename__ = "labels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)

    tasks = relationship("Task", secondary=task_labels, back_populates="labels")
