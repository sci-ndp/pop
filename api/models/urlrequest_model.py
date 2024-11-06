from pydantic import BaseModel, Field, ValidationError, model_validator
from enum import Enum
from typing import Any, Dict, Optional


# Define an enumeration for file types
class FileTypeEnum(str, Enum):
    stream = "stream"
    CSV = "CSV"
    TXT = "TXT"
    JSON = "JSON"
    NetCDF = "NetCDF"


# Define the main request model
class URLRequest(BaseModel):
    resource_name: str = Field(
        ...,
        description="The unique name of the resource to be created.",
        json_schema_extra={"example": "example_resource_name"},
    )
    resource_title: str = Field(
        ...,
        description="The title of the resource to be created.",
        json_schema_extra={"example": "Example Resource Title"},
    )
    owner_org: str = Field(
        ...,
        description=(
            "The ID of the organization to which the resource belongs."),
        json_schema_extra={"example": "example_org_id"},
    )
    resource_url: str = Field(
        ...,
        description="The URL of the resource to be added.",
        json_schema_extra={"example": "http://example.com/resource"},
    )
    file_type: Optional[FileTypeEnum] = Field(
        None,
        description=(
            "The type of the file. "
            "Valid options are: stream, CSV, TXT, JSON, NetCDF."
        ),
        json_schema_extra={"example": "CSV"},
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes about the resource.",
        json_schema_extra={
            "example": "Some additional notes about the resource."},
    )
    extras: Optional[Dict[str, str]] = Field(
        None,
        description=(
            "Additional metadata to be added to the resource package "
            "as extras."
        ),
        json_schema_extra={"example": {"key1": "value1", "key2": "value2"}},
    )
