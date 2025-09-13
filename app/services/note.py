from datetime import datetime, timezone

from sqlmodel import Session, Sequence, select
from sqlmodel.main import SQLModel

from app.core.exceptions import NoteNotFoundError
from app.core.summarizer import get_summarizer
from app.db.session import engine
from app.models.note import Note
from app.schemas.note import NoteCreate


def get_note_owner(note_id: int, session: Session) -> int | None:
    note = get_note_by_id(note_id, session)
    if note is None:
        return note
    return note.user_id


def create_note(note_in: NoteCreate, user_id: int, session: Session) -> Note:
    note = Note(content=note_in.content, user_id=user_id)
    from app.core.queue import enqueue_job
    note.status = "queued"
    session.add(note)
    session.commit()
    session.refresh(note)
    enqueue_job(note.id)
    return note


def get_user_notes(user_id: int, skip: int, limit: int, session: Session) -> Sequence[Note]:
    return session.exec(select(Note).where(Note.user_id == user_id).offset(skip).limit(limit)).all()


def get_note_by_id(note_id: int, session: Session) -> Note | None:
    note = session.exec(select(Note).where(Note.id == note_id)).first()
    if note is None:
        raise NoteNotFoundError
    return note


def update_note(note_id: int, note_in: NoteCreate, session: Session):
    note = get_note_by_id(note_id, session)
    note.content = note_in.content
    note.updated_at = datetime.now(timezone.utc)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


def delete_note(note_id: int, session: Session):
    note = get_note_by_id(note_id, session)
    session.delete(note)
    session.commit()
    return note

def summarize_note(note_id: int):
    with Session(engine) as session:
        note = session.exec(select(Note).where(Note.id == note_id)).first()
        if not note:
            return

        note.status = "processing"
        session.commit()

        try:
            # DEMO: intentional fail trigger
            if "__FAIL__" in (note.content or ""):
                note.status = "processing"
                session.commit()
                raise RuntimeError("Intentional demo failure triggered by token __FAIL__")

            summarizer = get_summarizer()
            result = summarizer(note.content, max_length=130, min_length=30, do_sample=False)
            note.summary = result[0]["summary_text"]
            note.status = "done"
            session.commit()
        except Exception:
            note.status = "failed"
            session.commit()
