import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class QuestionType(str, enum.Enum):
    single = "single"
    multi = "multi"
    scale = "scale"
    text = "text"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    surveys = relationship("Survey", back_populates="owner", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="user")


class Survey(Base):
    __tablename__ = "surveys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    is_published = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    settings = Column(JSONB, nullable=True)

    owner = relationship("User", back_populates="surveys")
    questions = relationship("Question", back_populates="survey", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="survey", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    survey_id = Column(UUID(as_uuid=True), ForeignKey("surveys.id"), nullable=False, index=True)
    text = Column(String, nullable=False)
    type = Column(Enum(QuestionType), nullable=False)
    required = Column(Boolean, nullable=False, default=True)
    order = Column(Integer, nullable=False, default=0)
    meta = Column(JSONB, nullable=True)

    survey = relationship("Survey", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    answer_values = relationship("AnswerValue", back_populates="question", cascade="all, delete-orphan")


class Option(Base):
    __tablename__ = "options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False, index=True)
    text = Column(String, nullable=False)
    order = Column(Integer, nullable=False, default=0)

    question = relationship("Question", back_populates="options")
    answer_options = relationship("AnswerOption", back_populates="option", cascade="all, delete-orphan")


class Response(Base):
    __tablename__ = "responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    survey_id = Column(UUID(as_uuid=True), ForeignKey("surveys.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String, nullable=True, index=True)  # Для неавторизованных пользователей (cookie-based)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    meta = Column(JSONB, nullable=True)

    survey = relationship("Survey", back_populates="responses")
    user = relationship("User", back_populates="responses")
    answer_values = relationship("AnswerValue", back_populates="response", cascade="all, delete-orphan")


class AnswerValue(Base):
    __tablename__ = "answer_values"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    response_id = Column(UUID(as_uuid=True), ForeignKey("responses.id"), nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False, index=True)
    value_text = Column(Text, nullable=True)
    value_number = Column(Float, nullable=True)

    response = relationship("Response", back_populates="answer_values")
    question = relationship("Question", back_populates="answer_values")
    answer_options = relationship("AnswerOption", back_populates="answer_value", cascade="all, delete-orphan")


class AnswerOption(Base):
    __tablename__ = "answer_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    answer_value_id = Column(UUID(as_uuid=True), ForeignKey("answer_values.id"), nullable=False, index=True)
    option_id = Column(UUID(as_uuid=True), ForeignKey("options.id"), nullable=False, index=True)

    answer_value = relationship("AnswerValue", back_populates="answer_options")
    option = relationship("Option", back_populates="answer_options")


