from pydantic import BaseModel, Field


class LabelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class LabelOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
