# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import copy
# Configuration file for JupyterHub
import os
from secrets import token_hex
from urllib.error import HTTPError
from oauthenticator.generic import GenericOAuthenticator
import requests
import logging
from dockerspawner import DockerSpawner

os.environ['JUPYTERHUB_CRYPT_KEY'] = token_hex(32)
c = get_config()  # noqa: F821

# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.

# Spawn single-user servers as Docker containers
# c.JupyterHub.spawner_class = DockerSpawner

# Spawn containers from this image
# c.DockerSpawner.image = os.environ["DOCKER_NOTEBOOK_IMAGE"]

# Connect containers to this Docker network
network_name = os.environ["DOCKER_NETWORK_NAME"]
c.Authenticator.enable_auth_state = True
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = network_name
c.DockerSpawner.allowed_images = ["quay.io/jupyter/minimal-notebook:latest", "quay.io/jupyter/r-notebook:latest"]

# Force the proxy to only listen to connections to 127.0.0.1 (on port proxy_port)
proxy_port = os.environ["JUPYTERHUB_PROXY_PORT"]
# c.JupyterHub.bind_url = f'http://127.0.0.1:{proxy_port}'
c.JupyterHub.bind_url = f"http://:{proxy_port}"

# Explicitly set notebook directory because we'll be mounting a volume to it.
# Most `jupyter/docker-stacks` *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
notebook_dir = os.environ.get("DOCKER_NOTEBOOK_DIR", "/home/jovyan/work")
c.DockerSpawner.notebook_dir = notebook_dir

# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
c.DockerSpawner.volumes = {"jupyterhub-user-{username}": notebook_dir}

# Remove containers once they are stopped
c.DockerSpawner.remove = True

# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = "jupyterhub"
c.JupyterHub.hub_port = int(os.environ.get("JUPYTERHUB_PORT", 8080))

# Persist hub data on volume mounted inside container
c.JupyterHub.cookie_secret_file = "/data/jupyterhub_cookie_secret"
c.JupyterHub.db_url = "sqlite:////data/jupyterhub.sqlite"

# Authenticate users with Native Authenticator
c.GenericOAuthenticator.client_id = os.environ.get("JUPYTERHUB_KEYCLOAK_CLIENT_ID")
c.GenericOAuthenticator.client_secret = os.environ.get("JUPYTERHUB_KEYCLOAK_CLIENT_SECRET")
c.GenericOAuthenticator.authorize_url = os.environ.get("JUPYTERHUB_AUTHORIZE_URL")
c.GenericOAuthenticator.token_url = os.environ.get("JUPYTERHUB_TOKEN_URL")
c.GenericOAuthenticator.userdata_url = os.environ.get("JUPYTERHUB_USERDATA_URL")
c.GenericOAuthenticator.oauth_callback_url = os.environ.get("JUPYTERHUB_OAUTH_CALLBACK_URL")
c.GenericOAuthenticator.logout_redirect_url = os.environ.get("JUPYTERHUB_LOGOUT_REDIRECT_URL")

c.GenericOAuthenticator.userdata_params = {'state': 'state'}
c.GenericOAuthenticator.username_key = 'preferred_username'
c.GenericOAuthenticator.login_service = 'Keycloak'
c.GenericOAuthenticator.scope = ['openid', 'profile']
c.GenericOAuthenticator.allow_all = True
c.GenericOAuthenticator.enable_auth_state = True
c.Authenticator.auto_login = True

# Allowed admins
admin = os.environ.get("JUPYTERHUB_ADMIN")
if admin:
    c.GenericOAuthenticator.admin_users = [admin]

c.JupyterHub.template_paths = ["/etc/jupyterhub/custom"]


class MyAuthenticator(GenericOAuthenticator):
    """
    Extending GenericOAuthenticator class to be able to check validity of tokens for NDP extension, before spawning
    """
    async def refresh_user(self, user, handler):
        """
        Will allow to a=start spawning, if access_token/refresh_token are updated, or redirect to logout otherwise
        :param user:
        :param handler:
        :return:
        """
        print(f"Refreshing Authenticator refresh_user for {user.name}")
        auth_state = await user.get_auth_state()
        if auth_state:
            if not await self.check_and_refresh_tokens(user, auth_state):
                if handler:
                    raise HTTPError(401, "Your session has expired. Please log out and log in again.")

                return False
        return True

    async def check_and_refresh_tokens(self, user, auth_state):
        """
        Will set new access_token and refresh_token into auth_state and return True, if refresh is possible,
        or will return False otherwise
        :param user:
        :param auth_state:
        :return:
        """
        refresh_token_valid = self.check_refresh_token_keycloak(auth_state)
        if refresh_token_valid:
            # here we need to refresh access_token
            print('Trying to refresh access_token')
            auth_state['access_token'], auth_state['refresh_token']  = refresh_token_valid
            await user.save_auth_state(auth_state)
            print(f"Updated auth_state saved for {user.name}")
            return True
        else:
            return False


    def check_refresh_token_keycloak(self, auth_state):
        """
        Will return tuple of access_token and refresh_token if refresh is possible, or False otherwise
        :param auth_state:
        :return:
        """
        _access_token = auth_state.get('access_token')
        _refresh_token = auth_state.get('refresh_token')
        print(f"Checking refresh_token")
        response = requests.post(c.GenericOAuthenticator.token_url,
                                 data={
                                     'grant_type': 'refresh_token',
                                     'refresh_token': _refresh_token,
                                     'client_id': c.GenericOAuthenticator.client_id,
                                     'client_secret': c.GenericOAuthenticator.client_secret
                                 })

        if response.status_code == 200:
            print(f"Refresh token is still good!")
            new_access_token = response.json().get('access_token')
            new_refresh_token = response.json().get('refresh_token')
            return new_access_token, new_refresh_token
        else:
            return False

# pass access_token and refresh_token for communicating with NDP APIs
async def auth_state_hook(spawner, auth_state):
    auth_state = await spawner.user.get_auth_state()
    logging.error("debugging")
    logging.error(auth_state)
    spawner.access_token = auth_state['access_token']
    spawner.refresh_token = auth_state['refresh_token']
    spawner.environment.update({'ACCESS_TOKEN': spawner.access_token})
    spawner.environment.update({'REFRESH_TOKEN': spawner.refresh_token})

def pre_spawn_hook(spawner):
    # env variables for extension
    spawner.environment.update({"CKAN_API_URL": os.environ["CKAN_API_URL"]})
    spawner.environment.update({"WORKSPACE_API_URL": os.environ["WORKSPACE_API_URL"]})
    spawner.environment.update({"REFRESH_EVERY_SECONDS": os.environ["REFRESH_EVERY_SECONDS"]})

    # install extension directly on image (in case user brings his image)
    pip_install_command0 = ("pip uninstall jupyterlab-git -y")
    pip_install_command1 = ("pip install --upgrade jupyterlab==4.2.4 jupyter-archive==3.4.0 jupyterlab-launchpad==1.0.1")
    pip_install_command2 = ("pip install jupyterlab-git==0.50.1 --index-url https://gitlab.nrp-nautilus.io/api/v4/projects/3930/packages/pypi/simple --user")
    pip_install_command3 = (f"pip install ndp-jupyterlab-extension=={ os.environ['NDP_EXT_VERSION'] } --index-url https://gitlab.nrp-nautilus.io/api/v4/projects/3930/packages/pypi/simple --user")

    # Modify the spawner's start command to include the pip install
    original_cmd = spawner.cmd or ["jupyterhub-singleuser"]
    spawner.cmd = [
        "bash",
        "-c",
        f"{pip_install_command0} || true "
        f"&& {pip_install_command1} || true "
        f"&& {pip_install_command2} || true "
        f"&& {pip_install_command3} || true "
        f"&& cd /home/jovyan/work || true "
        f"&& exec {' '.join(original_cmd)}"
    ]

    # make username available for MLflow library
    # username = spawner.user.name
    # spawner.environment.update({'MLFLOW_TRACKING_USERNAME': username})

c.JupyterHub.spawner_class = DockerSpawner
c.JupyterHub.authenticator_class = MyAuthenticator

# check only once per day not to block single-user
c.MyAuthenticator.auth_refresh_age = 86300
c.Authenticator.refresh_pre_spawn = True
c.DockerSpawner.pre_spawn_hook = pre_spawn_hook
c.MySpawner.http_timeout = 1200
c.DockerSpawner.auth_state_hook = auth_state_hook
