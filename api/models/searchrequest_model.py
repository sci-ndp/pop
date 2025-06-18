# api/models/searchrequest_model.py

from typing import Literal, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """
    Represents the input data for the POST /search endpoint.
    """

    dataset_name: str = Field(None, description="The name of the dataset.")
    dataset_title: str = Field(None, description="The title of the dataset.")
    owner_org: str = Field(None, description="The name of the organization.")
    resource_url: str = Field(None, description="The URL of the dataset resource.")
    resource_name: str = Field(None, description="The name of the dataset resource.")
    dataset_description: str = Field(
        None, description="The description of the dataset."
    )
    resource_description: str = Field(
        None, description="The description of the dataset resource."
    )
    resource_format: str = Field(
        None, description="The format of the dataset resource."
    )
    search_term: str = Field(
        None, description="A comma-separated list of search terms."
    )
    filter_list: list[str] = Field(
        None, description="A list of field filters (key:value)."
    )
    timestamp: str = Field(None, description="A timestamp or time range for filtering.")
    server: Optional[Literal["local", "global", "pre_ckan"]] = Field(
        "global",
        description=(
            "Specify the server to search on: 'local', 'global', "
            "or 'pre_ckan'. Defaults to 'global'."
        ),
    )
