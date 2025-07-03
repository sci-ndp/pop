from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CKANResource(BaseModel):
    resource_url: str
    format: Optional[str] = Field(default="URL")
    name: Optional[str]
    description: Optional[str]


class DatasetUpdateRequest(BaseModel):
    title: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    groups: Optional[List[str]] = None
    extras: Optional[Dict[str, str]] = None
    resources: Optional[List[CKANResource]] = None
