# api/models/general_dataset_request_model.py

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ResourceRequest(BaseModel):
    """
    Model for resource definition within a general dataset request.

    Represents a single resource (file, URL, etc.) that belongs to a dataset.
    """

    url: str = Field(..., description="URL or path to the resource")
    name: str = Field(..., description="Name identifier for the resource")
    format: Optional[str] = Field(
        None, description="Format of the resource (CSV, JSON, etc.)"
    )
    description: Optional[str] = Field(None, description="Description of the resource")
    mimetype: Optional[str] = Field(None, description="MIME type of the resource")
    size: Optional[int] = Field(None, description="Size of the resource in bytes")


class GeneralDatasetRequest(BaseModel):
    """
    Model for creating a general dataset in CKAN.

    This model provides a flexible interface for creating datasets without
    being tied to specific resource types like S3, Kafka, or URL.
    """

    name: str = Field(
        ..., description="Unique name for the dataset (lowercase, no spaces)"
    )
    title: str = Field(..., description="Human-readable title of the dataset")
    owner_org: str = Field(..., description="Organization ID that owns this dataset")
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
    resources: Optional[List[ResourceRequest]] = Field(
        None, description="List of resources associated with this dataset"
    )
    private: Optional[bool] = Field(
        False, description="Whether the dataset is private or public"
    )
    license_id: Optional[str] = Field(
        None, description="License identifier for the dataset"
    )
    version: Optional[str] = Field(None, description="Version of the dataset")


class GeneralDatasetUpdateRequest(BaseModel):
    """
    Model for updating an existing general dataset in CKAN.

    All fields are optional to allow partial updates (PATCH operations).
    """

    name: Optional[str] = Field(
        None, description="Unique name for the dataset (lowercase, no spaces)"
    )
    title: Optional[str] = Field(
        None, description="Human-readable title of the dataset"
    )
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
    resources: Optional[List[ResourceRequest]] = Field(
        None, description="List of resources associated with this dataset"
    )
    private: Optional[bool] = Field(
        None, description="Whether the dataset is private or public"
    )
    license_id: Optional[str] = Field(
        None, description="License identifier for the dataset"
    )
    version: Optional[str] = Field(None, description="Version of the dataset")
