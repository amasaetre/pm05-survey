from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models import QuestionType, UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(UserBase):
    id: UUID
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int
    type: str


class OptionBase(BaseModel):
    text: str
    order: int = 0


class OptionCreate(OptionBase):
    pass


class OptionRead(OptionBase):
    id: UUID

    class Config:
        from_attributes = True


class QuestionBase(BaseModel):
    text: str
    type: QuestionType
    required: bool = True
    order: int = 0
    meta: Optional[dict] = None


class QuestionCreate(QuestionBase):
    options: Optional[List[OptionCreate]] = None


class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    type: Optional[QuestionType] = None
    required: Optional[bool] = None
    order: Optional[int] = None
    meta: Optional[dict] = None


class QuestionRead(QuestionBase):
    id: UUID
    options: List[OptionRead] = []

    class Config:
        from_attributes = True


class SurveyBase(BaseModel):
    title: str
    description: str
    settings: Optional[dict] = None


class SurveyCreate(SurveyBase):
    questions: Optional[List[QuestionCreate]] = None


class SurveyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[dict] = None
    is_published: Optional[bool] = None


class SurveyRead(SurveyBase):
    id: UUID
    owner_id: UUID
    is_published: bool
    created_at: datetime
    questions: List[QuestionRead] = []

    class Config:
        from_attributes = True


class AnswerValueSubmit(BaseModel):
    question_id: UUID
    value_text: Optional[str] = None
    value_number: Optional[float] = None
    option_ids: Optional[List[UUID]] = None


class SubmitResponsePayload(BaseModel):
    user_id: Optional[UUID] = None
    answers: List[AnswerValueSubmit]


class ResponseRead(BaseModel):
    id: UUID
    survey_id: UUID
    user_id: Optional[UUID]
    submitted_at: datetime
    meta: Optional[dict]

    class Config:
        from_attributes = True


class OptionStats(BaseModel):
    option_id: UUID
    text: str
    count: int
    percentage: float


class TextResponse(BaseModel):
    response_id: UUID
    text: str
    created_at: Optional[datetime] = None


class QuestionAnalytics(BaseModel):
    question_id: UUID
    type: QuestionType
    total_responses: int
    options: Optional[List[OptionStats]] = None
    histogram: Optional[dict] = None
    avg: Optional[float] = None
    text_responses: Optional[List[TextResponse]] = None


class SurveyAnalytics(BaseModel):
    survey_id: UUID
    total_responses: int
    questions: List[QuestionAnalytics]


