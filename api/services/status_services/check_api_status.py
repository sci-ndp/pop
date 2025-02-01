# api/services/status_services/check_api_status.py

from api.config.ckan_settings import ckan_settings
from api.services import status_services
from api.services.keycloak_services.introspect_user_token import \
    get_client_token


def get_status():
    """
    Checks if local/global CKAN and Keycloak are active and reachable.

    Returns
    -------
    dict
        A dictionary with the following keys:
          - ckan_local_enabled (bool): Whether local CKAN is enabled in
          settings.
          - ckan_is_active_local (bool or None): Whether local CKAN is
          reachable (if enabled).
          - ckan_is_active_global (bool): Whether global CKAN is reachable.
          - keycloak_is_active (bool): Whether Keycloak is active.

    Note
    ----
    If local CKAN is disabled, 'ckan_is_active_local' will be None by default
    and no check will be performed for local CKAN.
    """
    status_dict = {
        "ckan_local_enabled": ckan_settings.ckan_local_enabled,
        "ckan_is_active_local": None,
        "ckan_is_active_global": False,
        "keycloak_is_active": False
    }

    # 1. Check local CKAN if enabled
    if ckan_settings.ckan_local_enabled:
        try:
            # Defaults to checking local CKAN if no arguments are passed
            status_dict["ckan_is_active_local"] = \
                status_services.check_ckan_status()
        except Exception:
            status_dict["ckan_is_active_local"] = False

    # 2. Check global CKAN
    try:
        status_dict["ckan_is_active_global"] = \
            status_services.check_ckan_status(local=False)
    except Exception:
        status_dict["ckan_is_active_global"] = False

    # 3. Check Keycloak status
    try:
        get_client_token()
        status_dict["keycloak_is_active"] = True
    except Exception:
        status_dict["keycloak_is_active"] = False

    return status_dict
