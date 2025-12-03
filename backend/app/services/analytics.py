from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AnswerOption, AnswerValue, Option, Question, QuestionType, Response
from app.schemas import OptionStats, QuestionAnalytics, SurveyAnalytics


async def get_survey_analytics(session: AsyncSession, survey_id: UUID) -> SurveyAnalytics:
    total_stmt = select(func.count(Response.id)).where(Response.survey_id == survey_id)
    total_responses = (await session.execute(total_stmt)).scalar_one()

    questions = (
        await session.execute(select(Question).where(Question.survey_id == survey_id).order_by(Question.order))
    ).scalars().all()

    question_analytics: list[QuestionAnalytics] = []

    for q in questions:
        if q.type in (QuestionType.single, QuestionType.multi):
            stmt = (
                select(
                    Option.id,
                    Option.text,
                    func.count(AnswerOption.id),
                )
                .join(AnswerOption, AnswerOption.option_id == Option.id, isouter=True)
                .where(Option.question_id == q.id)
                .group_by(Option.id, Option.text)
            )
            rows = (await session.execute(stmt)).all()
            option_stats: list[OptionStats] = []
            total_for_question = sum(r[2] for r in rows) or 1
            for opt_id, text, count in rows:
                option_stats.append(
                    OptionStats(
                        option_id=opt_id,
                        text=text,
                        count=count,
                        percentage=(count / total_for_question) * 100.0 if total_for_question else 0.0,
                    )
                )
            question_analytics.append(
                QuestionAnalytics(
                    question_id=q.id,
                    type=q.type,
                    total_responses=total_for_question,
                    options=option_stats,
                )
            )
        elif q.type == QuestionType.scale:
            values_stmt = select(AnswerValue.value_number).where(AnswerValue.question_id == q.id)
            values = [v[0] for v in (await session.execute(values_stmt)).all() if v[0] is not None]
            total_for_question = len(values)
            histogram: dict[float, int] = {}
            avg = None
            if values:
                for v in values:
                    histogram[v] = histogram.get(v, 0) + 1
                avg = sum(values) / len(values)
            question_analytics.append(
                QuestionAnalytics(
                    question_id=q.id,
                    type=q.type,
                    total_responses=total_for_question,
                    histogram=histogram,
                    avg=avg,
                )
            )
        else:
            text_stmt = (
                select(
                    AnswerValue.response_id,
                    AnswerValue.value_text,
                    Response.submitted_at,
                )
                .join(Response, AnswerValue.response_id == Response.id)
                .where(AnswerValue.question_id == q.id)
                .where(AnswerValue.value_text.isnot(None))
                .order_by(Response.submitted_at.desc())
            )
            text_rows = (await session.execute(text_stmt)).all()
            total_for_question = len(text_rows)
            from app.schemas import TextResponse
            text_responses = [
                TextResponse(
                    response_id=row[0],
                    text=row[1] or "",
                    created_at=row[2],
                )
                for row in text_rows
            ]
            question_analytics.append(
                QuestionAnalytics(
                    question_id=q.id,
                    type=q.type,
                    total_responses=total_for_question,
                    text_responses=text_responses,
                )
            )

    return SurveyAnalytics(
        survey_id=survey_id,
        total_responses=total_responses,
        questions=question_analytics,
    )


async def get_question_analytics(
    session: AsyncSession,
    survey_id: UUID,
    question_id: UUID,
) -> QuestionAnalytics:
    survey_analytics = await get_survey_analytics(session, survey_id)
    for q in survey_analytics.questions:
        if q.question_id == question_id:
            return q
    raise ValueError("Question not found in analytics")


