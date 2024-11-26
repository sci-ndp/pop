import requests
from fastapi import HTTPException

def run_jupyterhub():
    """
    Sends a request to the running JupyterHub instance to validate it is active.
    :return: Success message.
    """
    try:
        # Ping the JupyterHub server running in Docker
        response = requests.get("http://jupyterhub:8002/hub/spawn")
        if response.status_code == 200:
            return {"message": "JupyterHub is running and accessible."}
        else:
            raise HTTPException(status_code=500, detail="Failed to connect to JupyterHub.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to JupyterHub: {str(e)}")
