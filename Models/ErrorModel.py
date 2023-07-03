from pydantic import BaseModel

class ErrorModel(BaseModel):
    success : bool
    msg:str

class CustomErrorResponse(BaseModel):
    error_code: int
    error_message: str