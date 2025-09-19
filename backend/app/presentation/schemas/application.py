from datetime import date
from typing import List
from typing_extensions import Literal
from pydantic import BaseModel, EmailStr

from app.presentation.schemas import BaseSchema, TimeSchema


class CreateApplication(BaseSchema):
    company: str
    role: str
    mode: Literal['active', 'passive']
    platform_id: int
    application_date: date
    observation: str | None = None
    expected_salary: float | None = None
    salary_range_min: float | None = None
    salary_range_max: float | None = None


class ApplicationLastStep(BaseModel):
    id: int
    name: str
    color: str
    date: date


class ApplicationFeedback(BaseModel):
    id: int
    name: str
    color: str
    date: date


class Application(BaseSchema, TimeSchema):
    id: int
    company: str
    role: str
    mode: Literal['active', 'passive']
    platform_id: int
    application_date: date
    observation: str | None = None
    expected_salary: float | None = None
    salary_range_min: float | None = None
    salary_range_max: float | None = None

    last_step: ApplicationLastStep | None = None
    feedback: ApplicationFeedback | None = None
