from kubernetes import client
from .create_dspaces_resources import v1_api, apps_v1_api, networking_v1_api, rbac_v1_api  # Reuse initialized clients

def delete_dspaces_resources(user_id: str):
    """
    Delete all Kubernetes resources for a user's dspaces instance by removing the namespace.
    """
    namespace = f"dspaces-{user_id}"
    
    try:
        # Check if namespace exists
        v1_api.read_namespace(name=namespace)
    except client.ApiException as e:
        if e.status == 404:
            return {"detail": f"No dspaces instance found for user {user_id}"}
        raise e

    try:
        # Delete the namespace (this will cascade delete all resources within it)
        v1_api.delete_namespace(name=namespace)
        
        # Optionally, wait for deletion to complete (can be adjusted based on needs)
        while True:
            try:
                v1_api.read_namespace(name=namespace)
                import time
                time.sleep(1)  # Wait briefly before checking again
            except client.ApiException as e:
                if e.status == 404:
                    break  # Namespace is gone
                raise e

        return {"detail": f"Namespace {namespace} and all associated resources deleted"}
    except client.ApiException as e:
        raise Exception(f"Failed to delete namespace {namespace}: {str(e)}")