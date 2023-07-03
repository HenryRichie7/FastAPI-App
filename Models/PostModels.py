from pydantic import BaseModel

class QueryExecuteModel(BaseModel):
    query: str