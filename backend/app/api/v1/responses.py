from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response as FastAPIResponse, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_active_user, get_current_user_optional
from app.crud import submit_response
from app.db import get_session
from app.models import Response, Survey
from app.schemas import ResponseRead, SubmitResponsePayload, UserRead


router = APIRouter()


def get_or_create_session_id(request: Request, response: FastAPIResponse) -> str:
    session_id = request.cookies.get("survey_session_id")
    if not session_id:
        session_id = str(uuid4())
        response.set_cookie(
            key="survey_session_id",
            value=session_id,
            max_age=31536000,
            httponly=True,
            samesite="lax",
            secure=False,
        )
    return session_id


@router.post("/surveys/{survey_id}/responses", response_model=ResponseRead, status_code=status.HTTP_201_CREATED)
async def submit_survey_response(
    survey_id: UUID,
    payload: SubmitResponsePayload,
    request: Request,
    response: FastAPIResponse,
    session: AsyncSession = Depends(get_session),
    current_user: Optional[UserRead] = Depends(get_current_user_optional),
):
    survey = await session.get(Survey, survey_id)
    if not survey or not survey.is_published:
        raise HTTPException(status_code=404, detail="Survey not available")

    user_id = current_user.id if current_user is not None else payload.user_id

    if current_user is not None:
        existing_response = await session.execute(
            select(Response).where(
                Response.survey_id == survey_id,
                Response.user_id == current_user.id
            )
        )
        if existing_response.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already submitted a response to this survey"
            )
        session_id = None
    else:
        session_id = get_or_create_session_id(request, response)
        
        existing_response = await session.execute(
            select(Response).where(
                Response.survey_id == survey_id,
                Response.session_id == session_id
            )
        )
        if existing_response.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already submitted a response to this survey"
            )

    meta = {
        "ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }
    response_obj = await submit_response(
        session=session,
        survey_id=survey_id,
        user_id=user_id,
        answers=payload.answers,
        meta=meta,
        session_id=session_id,
    )
    return ResponseRead.model_validate(response_obj)


@router.get("/surveys/{survey_id}/responses/check", response_model=dict)
async def check_user_response(
    survey_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: Optional[UserRead] = Depends(get_current_user_optional),
):
    if current_user is not None:
        existing_response = await session.execute(
            select(Response).where(
                Response.survey_id == survey_id,
                Response.user_id == current_user.id
            )
        )
        has_responded = existing_response.scalar_one_or_none() is not None
    else:
        session_id = request.cookies.get("survey_session_id")
        if not session_id:
            has_responded = False
        else:
            existing_response = await session.execute(
                select(Response).where(
                    Response.survey_id == survey_id,
                    Response.session_id == session_id
                )
            )
            has_responded = existing_response.scalar_one_or_none() is not None
    
    return {"has_responded": has_responded}


@router.get("/surveys/{survey_id}/responses", response_model=List[ResponseRead])
async def list_survey_responses(
    survey_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_active_user),
):
    survey = await session.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    if survey.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    result = await session.execute(select(Response).where(Response.survey_id == survey_id))
    responses = list(result.scalars().unique())
    return [ResponseRead.model_validate(r) for r in responses]


@router.get("/responses/{response_id}", response_model=ResponseRead)
async def get_response_detail(
    response_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_active_user),
):
    response = await session.get(Response, response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")

    survey = await session.get(Survey, response.survey_id)
    if not survey or survey.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return ResponseRead.model_validate(response)


