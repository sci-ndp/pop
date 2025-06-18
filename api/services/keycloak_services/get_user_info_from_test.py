from ...config.keycloak_settings import keycloak_settings


def get_user_info_from_test():
    """
    This function is used to get the details of a user from a token

    Parameters
    ----------
    token : str
        token of the user

    Returns
    -------
    user_info : dict
        details of the user
    """
    # If the response is successful
    # Extract the relevant information from the response
    user_info = {}
    user_info["id"] = "1234"
    user_info["username"] = keycloak_settings.test_username
    user_info["email"] = "test_email@email.com"
    user_info["first_name"] = keycloak_settings.test_username
    user_info["last_name"] = keycloak_settings.test_username
    return user_info
