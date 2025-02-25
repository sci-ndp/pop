# api/config/ckan_settings.py

from pydantic_settings import BaseSettings
from ckanapi import RemoteCKAN


class Settings(BaseSettings):
    ckan_local_enabled: bool = True
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
        return RemoteCKAN(self.pre_ckan_url, apikey=self.pre_ckan_api_key)

    @property
    def pre_ckan_no_api_key(self):
        return RemoteCKAN(self.pre_ckan_url)

    model_config = {
        "env_file": "./env_variables/.env_ckan",
        "extra": "allow",
    }


ckan_settings = Settings()
