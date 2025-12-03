from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column(
            "role",
            sa.Enum("user", "admin", name="userrole"),
            nullable=False,
            server_default="user",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "surveys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.create_index("ix_surveys_owner_id", "surveys", ["owner_id"])

    op.create_table(
        "questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "survey_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("surveys.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column(
            "type",
            sa.Enum("single", "multi", "scale", "text", name="questiontype"),
            nullable=False,
        ),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.create_index("ix_questions_survey_id", "questions", ["survey_id"])

    op.create_table(
        "options",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "question_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("questions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_options_question_id", "options", ["question_id"])

    op.create_table(
        "responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "survey_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("surveys.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.create_index("ix_responses_survey_id", "responses", ["survey_id"])
    op.create_index("ix_responses_user_id", "responses", ["user_id"])

    op.create_table(
        "answer_values",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "response_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("responses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "question_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("questions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("value_text", sa.Text(), nullable=True),
        sa.Column("value_number", sa.Float(), nullable=True),
    )
    op.create_index("ix_answer_values_response_id", "answer_values", ["response_id"])
    op.create_index("ix_answer_values_question_id", "answer_values", ["question_id"])

    op.create_table(
        "answer_options",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "answer_value_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("answer_values.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "option_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("options.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    op.create_index("ix_answer_options_answer_value_id", "answer_options", ["answer_value_id"])
    op.create_index("ix_answer_options_option_id", "answer_options", ["option_id"])


def downgrade() -> None:
    op.drop_index("ix_answer_options_option_id", table_name="answer_options")
    op.drop_index("ix_answer_options_answer_value_id", table_name="answer_options")
    op.drop_table("answer_options")

    op.drop_index("ix_answer_values_question_id", table_name="answer_values")
    op.drop_index("ix_answer_values_response_id", table_name="answer_values")
    op.drop_table("answer_values")

    op.drop_index("ix_responses_user_id", table_name="responses")
    op.drop_index("ix_responses_survey_id", table_name="responses")
    op.drop_table("responses")

    op.drop_index("ix_options_question_id", table_name="options")
    op.drop_table("options")

    op.drop_index("ix_questions_survey_id", table_name="questions")
    op.drop_table("questions")

    op.drop_index("ix_surveys_owner_id", table_name="surveys")
    op.drop_table("surveys")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.execute('DROP TYPE IF EXISTS "userrole"')
    op.execute('DROP TYPE IF EXISTS "questiontype"')


