# api/config/ckan_settings.py

from pydantic_settings import BaseSettings
from ckanapi import RemoteCKAN


class Settings(BaseSettings):
    ckan_local_enabled: bool = False
    ckan_url: str = "http://localhost:5000"
    ckan_api_key: str = "your-api-key"
    ckan_global_url: str = "http://localhost:5000"
    pre_ckan_enabled: bool = False
    pre_ckan_url: str = ""
    pre_ckan_api_key: str = ""

    @property
    def ckan(self):
        return RemoteCKAN(self.ckan_url, apikey=self.ckan_api_key)

    @property
    def ckan_no_api_key(self):
        return RemoteCKAN(self.ckan_url)

    @property
    def ckan_global(self):
        return RemoteCKAN(self.ckan_global_url)

    @property
    def pre_ckan(self):
        # If pre_ckan_url does not start with http:// or https://,
        # prepend http:// by default to avoid "No scheme supplied" errors.
        if self.pre_ckan_url and not (
            self.pre_ckan_url.startswith("http://")
            or self.pre_ckan_url.startswith("https://")
        ):
            valid_url = f"http://{self.pre_ckan_url}"
            return RemoteCKAN(valid_url, apikey=self.pre_ckan_api_key)

        return RemoteCKAN(self.pre_ckan_url, apikey=self.pre_ckan_api_key)

    @property
    def pre_ckan_no_api_key(self):
        if self.pre_ckan_url and not (
            self.pre_ckan_url.startswith("http://")
            or self.pre_ckan_url.startswith("https://")
        ):
            valid_url = f"http://{self.pre_ckan_url}"
            return RemoteCKAN(valid_url)
        return RemoteCKAN(self.pre_ckan_url)

    model_config = {
        "env_file": ".env",
        "extra": "allow",
    }


ckan_settings = Settings()
