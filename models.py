from pydantic import BaseModel


class SearchResult(BaseModel):
    title: str
    url: str
    summary: str