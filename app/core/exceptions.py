from fastapi import HTTPException

class NoteError(HTTPException):
    """Base exception for note-related errors"""
    pass

class NoteNotFoundError(NoteError):
    def __init__(self, note_id=None):
        message = "Note not found" if note_id is None else f"Note with id {note_id} not found"
        super().__init__(status_code=404, detail=message)

class NoteCreationError(NoteError):
    def __init__(self, error: str):
        super().__init__(status_code=500, detail=f"Failed to create note: {error}")

class UserError(HTTPException):
    """Base exception for user-related errors"""
    pass

class UserNotFoundError(UserError):
    def __init__(self, user_id=None):
        message = "User not found" if user_id is None else f"User with id {user_id} not found"
        super().__init__(status_code=404, detail=message)

class PasswordMismatchError(UserError):
    def __init__(self):
        super().__init__(status_code=400, detail="New passwords do not match")

class PaswordRequirementsNotMetError(UserError):
    def __init__(self):
        super().__init__(status_code=400, detail="New password does not meet security requirements")

class InvalidPasswordError(UserError):
    def __init__(self):
        super().__init__(status_code=401, detail="Current password is incorrect")

class AuthenticationError(HTTPException):
    def __init__(self, message: str = "Could not validate user"):
        super().__init__(status_code=401, detail=message)

class TokenError(HTTPException):
    def __init__(self, message: str = "Invalid Credentials"):
        super().__init__(status_code=401, detail=message)
