from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

import app.services.note as service
from app.core.auth import get_current_user, authorize
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
    session: Session = Depends(get_session), user=Depends(get_current_user)
):
    return service.get_user_notes(user.id, session)


@router.get("/{resource_id}", response_model=NoteOut)
async def get_note(
    resource_id: int,
    session: Session = Depends(get_session),
    user: User = authorize("notes:read", service.get_note_owner),
):
    note = service.get_note_by_id(resource_id, session)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    return note


@router.patch("/{resource_id}", response_model=NoteOut)
async def update_note(
    resource_id: int,
    note_in: NoteCreate,
    session: Session = Depends(get_session),
    user: User = authorize("notes:update", service.get_note_owner),
):
    note = service.get_note_by_id(resource_id, session)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    return service.update_note(note, note_in.content, session)


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    resource_id: int,
    session: Session = Depends(get_session),
    user: User = authorize("notes:delete", service.get_note_owner),
):
    note = service.get_note_by_id(resource_id, session)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    service.delete_note(note, session)
    return
