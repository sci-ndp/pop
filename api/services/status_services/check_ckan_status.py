from ckanapi import NotFound
from api.config.ckan_settings import ckan_settings


def check_ckan_status(local=True) -> bool:
    """
    Check if CKAN is active and reachable.

    Parameters
    ----------
    local : bool, optional
        If True, check the local CKAN instance. If False, check the global CKAN
        instance. The default is True.

    Returns
    -------
    bool
        True if CKAN is active, False otherwise.

    Raises
    ------
    Exception
        If there is an error connecting to CKAN.
    """
    if local:
        ckan = ckan_settings.ckan
    else:
        ckan = ckan_settings.ckan_global

    try:
        # Make a request to the status endpoint of CKAN
        status = ckan.action.status_show()
        return True if status else False
    except NotFound:
        return False
    except Exception as e:
        raise Exception(f"Error checking CKAN status: {str(e)}")
