from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

import app.services.note as service
from app.core.auth import authorize_user_or_admin, get_current_user
from app.db.session import get_session
from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteOut

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/", response_model=NoteOut)
async def create_new_note(
    note_in: NoteCreate,
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
):
    return service.create_note(note_in, user.id, session)


@router.get("/me", response_model=List[NoteOut])
async def get_my_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session), user=Depends(get_current_user)
):
    return service.get_user_notes(user.id, skip, limit, session=session)


@router.get("/{resource_id}", response_model=NoteOut)
async def get_note(
    resource_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(authorize_user_or_admin("notes:read", service.get_note_owner)),
):
    return service.get_note_by_id(resource_id, session)


@router.patch("/{resource_id}", response_model=NoteOut)
async def update_note(
    resource_id: int,
    note_in: NoteCreate,
    session: Session = Depends(get_session),
    user: User = Depends(authorize_user_or_admin(
        "notes:update", service.get_note_owner
    )),
):
    return service.update_note(resource_id, note_in, session=session)


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    resource_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(authorize_user_or_admin(
        "notes:delete", service.get_note_owner
    ),
)):
    service.delete_note(resource_id, session=session)
    return
