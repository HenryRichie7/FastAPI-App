from pydantic import BaseModel

class SingleResponseModel(BaseModel):
    success: bool
    results : str

class ListResponseModel(BaseModel):
    success: bool
    results : list

class DictResponseModel(BaseModel):
    success: bool
    results: dict