# api/models/general_dataset_response_model.py

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ResourceResponse(BaseModel):
    """
    Model for resource information in dataset responses.

    Represents a single resource that belongs to a dataset in responses.
    """

    id: str = Field(..., description="Unique identifier for the resource")
    url: str = Field(..., description="URL or path to the resource")
    name: str = Field(..., description="Name identifier for the resource")
    format: Optional[str] = Field(
        None, description="Format of the resource (CSV, JSON, etc.)"
    )
    description: Optional[str] = Field(None, description="Description of the resource")
    mimetype: Optional[str] = Field(None, description="MIME type of the resource")
    size: Optional[int] = Field(None, description="Size of the resource in bytes")
    created: Optional[str] = Field(None, description="Creation timestamp")
    last_modified: Optional[str] = Field(
        None, description="Last modification timestamp"
    )


class GeneralDatasetResponse(BaseModel):
    """
    Model for general dataset responses from CKAN.

    Represents a complete dataset with all its metadata and resources.
    """

    id: str = Field(..., description="Unique identifier for the dataset")
    name: str = Field(..., description="Unique name of the dataset")
    title: str = Field(..., description="Human-readable title of the dataset")
    owner_org: Optional[str] = Field(
        None, description="Organization ID that owns this dataset"
    )
    notes: Optional[str] = Field(
        None, description="Description or notes about the dataset"
    )
    tags: Optional[List[str]] = Field(
        None, description="List of tags for categorizing the dataset"
    )
    groups: Optional[List[str]] = Field(
        None, description="List of groups for the dataset"
    )
    extras: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata as key-value pairs"
    )
    resources: Optional[List[ResourceResponse]] = Field(
        None, description="List of resources associated with this dataset"
    )
    private: Optional[bool] = Field(
        None, description="Whether the dataset is private or public"
    )
    license_id: Optional[str] = Field(
        None, description="License identifier for the dataset"
    )
    version: Optional[str] = Field(None, description="Version of the dataset")
    created: Optional[str] = Field(None, description="Creation timestamp")
    last_modified: Optional[str] = Field(
        None, description="Last modification timestamp"
    )
    url: Optional[str] = Field(None, description="URL to view the dataset")
    state: Optional[str] = Field(
        None, description="State of the dataset (active, deleted, etc.)"
    )
