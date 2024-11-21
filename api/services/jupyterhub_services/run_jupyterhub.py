import os
import subprocess
from fastapi import HTTPException

def run_jupyterhub():
    """
    Runs JupyterHub using the existing configuration and Docker setup.
    :return: Success message.
    """
    try:
        # Ensure the JupyterHub configuration file and Dockerfile are present
        config_path = "JupyterHub_Docker/jupyterhub_config.py"
        docker_compose_path = "JupyterHub_Docker/docker-compose.yaml"
        
        if not os.path.exists(config_path):
            raise HTTPException(status_code=500, detail="JupyterHub configuration file is missing.")
        if not os.path.exists(docker_compose_path):
            raise HTTPException(status_code=500, detail="Docker Compose file is missing.")

        # Start the JupyterHub instance using docker-compose
        subprocess.run(
            ["docker-compose", "-f", docker_compose_path, "up", "-d"],
            check=True
        )

        return {"message": "JupyterHub instance started successfully."}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to start JupyterHub: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")