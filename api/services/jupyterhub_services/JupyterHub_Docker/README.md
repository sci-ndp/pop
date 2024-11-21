# NDP JupyterHub Docker
## Core Documentation
- JupyterHub Docker Deployment Guide and Examples: https://github.com/jupyterhub/jupyterhub-deploy-docker 

## Setup
1. Install Docker
2. Copy `.env.example` as `.env` file:
```
cp .env.example .env
```
And add missing Keycloak secret `JUPYTERHUB_KEYCLOAK_CLIENT_SECRET= !!! CHANGE ME !!!`

## Deploy:

```docker compose -f docker-compose.yaml up --build -d```
Go to http://localhost:8002/hub/spawn to use JupyterHub.

## Undeploy:
```docker compose -f docker-compose.yaml down```

   
### Important Notes
1. The hub is customized using these guides:
https://jupyterhub.readthedocs.io/en/stable/howto/templates.html#extending-templates
https://github.com/jupyterhub/jupyterhub/tree/886ce6cbdfc00b66b45ac769e5ab2270abca3ef1/share/jupyterhub/templates
`hub_docker_image` folder contains Dockerfile for hub image + templates and pics.

2. `jupyterhub_config.py` is the main JupyterHub configuration, it is mounted in docker compose file (`docker-compose.dev.yaml`). 
3. All needed customization changes and logic can be done in `jupyterhub_config.py`. Mainly, they will be applied to classes:
   - DockerSpawner (https://github.com/jupyterhub/dockerspawner/tree/main/examples/image_form, https://jupyterhub-dockerspawner.readthedocs.io/en/latest/api/index.html)
   - GenericOAuthenticator (https://oauthenticator.readthedocs.io/en/latest/reference/api/gen/oauthenticator.generic.html#)

4. There are few other Jupyter dependencies in the following GIT repos:
 - https://github.com/national-data-platform/ndp-jupyterlab-extension - NDP extension for JupyterLab. It is being installed on single-user server container.
 - https://github.com/national-data-platform/jupyterlab-git - Special version of JupyterLab GIT extension. It was created to allow passing GIT link into GIT Clone dialog for NDP needs. It is being installed on single-user server container.

5. A number of environment variables has to be set in `.env` file, passed to `docker-compose.yaml` file and processed in `jupyterhub_config.py` in order the overall deployment to work.
6. All NDP docker images and Python packages(PyPi) are stored in NRP Gitlab (https://gitlab.nrp-nautilus.io/).
- **Gitlab Container Registry (for Docker images)**. Enter your Gitlab username and personal access token:
``
docker login gitlab-registry.nrp-nautilus.io
``
Now, you should be able to push images to our Gitlab registry. For example: 
```
docker push gitlab-registry.nrp-nautilus.io/ndp/ndp-docker-images/jh:2.0.10
```
Our images are located at: https://gitlab.nrp-nautilus.io/ndp/ndp-docker-images/container_registry

- **GitLab Package Registry (for PyPi packages)**.
To be able to push or pull private Python packages, the local machine should be set up according to the instructions at https://gitlab.nrp-nautilus.io/help/user/packages/package_registry/index.
Add authentication (https://gitlab.nrp-nautilus.io/help/user/packages/pypi_repository/index.md#authenticate-with-a-deploy-token).

Create file: ~/.pypirc
```
[distutils]
index-servers =
    gitlab

[gitlab]
repository = https://gitlab.nrp-nautilus.io/api/v4/projects/ndp%2Fndp-docker-images/packages/pypi
username = <your_personal_access_token_name>
password = <your_personal_access_token>
```
After that, you'll be able to push PyPi packages, so they can be installed later by standard pip command:
```
pip install jupyterlab-git ndp-jupyterlab-extension --index-url https://gitlab.nrp-nautilus.io/api/v4/projects/3930/packages/pypi/simple
```
Our packages are located at: https://gitlab.nrp-nautilus.io/ndp/ndp-docker-images/-/packages  
