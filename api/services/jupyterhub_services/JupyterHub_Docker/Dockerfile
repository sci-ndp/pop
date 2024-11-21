# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
ARG JUPYTERHUB_VERSION
FROM quay.io/jupyterhub/jupyterhub:$JUPYTERHUB_VERSION

RUN apt-get update && apt-get install -y \
    git
# RUN git clone --single-branch --branch=main --depth=1 -- https://github.com/national-data-platform/jupyter-templates.git /etc/jupyterhub/custom

COPY hub_docker_image/403.html /etc/jupyterhub/custom/403.html
COPY hub_docker_image/page.html /etc/jupyterhub/custom/page.html
COPY hub_docker_image/spawn.html /etc/jupyterhub/custom/spawn.html

COPY hub_docker_image/pics/ndp_logo.png /usr/local/share/jupyterhub/static/images/ndp_logo.png
COPY hub_docker_image/pics/ndp-landing-image.png /usr/local/share/jupyterhub/static/images/ndp-landing-image.png
# Install dockerspawner, nativeauthenticator
# hadolint ignore=DL3013
RUN python3 -m pip install --no-cache-dir \
    dockerspawner \
    oauthenticator

CMD ["jupyterhub", "-f", "/srv/jupyterhub/jupyterhub_config.py"]
