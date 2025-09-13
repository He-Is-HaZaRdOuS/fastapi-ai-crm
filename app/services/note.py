from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models.note import Note
from app.schemas.note import NoteCreate

def get_note_owner(note_id: int, session: Session) -> int | None:
    note = get_note_by_id(note_id, session)
    if note is None:
        return note
    return note.user_id


def create_note(note_in: NoteCreate, user_id: int, session: Session) -> Note:
    note = Note(content=note_in.content, user_id=user_id)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


def get_user_notes(user_id: int, session: Session):
    return session.exec(select(Note).where(Note.user_id == user_id)).all()


def get_note_by_id(note_id: int, session: Session):
    return session.exec(
        select(Note).where(Note.id == note_id)
    ).first()


def update_note(note: Note, content: str, session: Session):
    note.content = content
    note.updated_at = datetime.now(timezone.utc)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


def delete_note(note: Note, session: Session):
    session.delete(note)
    session.commit()
