import os
import time
import yaml
from pathlib import Path
from typing import Optional
from kubernetes import client, config


def get_kubeconfig_path() -> str:
    """
    Determine the path to the kubeconfig file, prioritizing environment variables and mounted paths.
    Falls back to a default location if not found.
    """
    # Check if KUBECONFIG environment variable is set
    kubeconfig_from_env = os.environ.get("KUBECONFIG")
    print(f"KUBECONFIG environment variable: {kubeconfig_from_env}")
    if kubeconfig_from_env and os.path.exists(kubeconfig_from_env):
        return kubeconfig_from_env

    # Default path inside the Docker container (mounted from env_variables)
    default_kubeconfig_path = "/code/env_variables/.kubeconfig"  # Adjust filename if necessary (e.g., "kubeconfig" or "config")

    if os.path.exists(default_kubeconfig_path):
        return default_kubeconfig_path

    # If not found, raise an exception or log a warning
    raise FileNotFoundError(
        f"Kubeconfig file not found at {default_kubeconfig_path}. "
        "Please ensure the file exists in the env_variables folder and is mounted correctly in the Docker container, "
        "or set the KUBECONFIG environment variable."
    )

# Load kubeconfig (assumes service runs with cluster access)
# Specify the custom kubeconfig path
kubeconfig_path = get_kubeconfig_path()
try:
    config.load_kube_config(config_file=kubeconfig_path)
    # config.load_kube_config() # Load default kubeconfig
except Exception as e:
    print(f"Attempting to load kubeconfig from: {kubeconfig_path}")
    raise Exception(f"Failed to load kubeconfig: {e}")

api_client = client.ApiClient()
v1_api = client.CoreV1Api(api_client)
apps_v1_api = client.AppsV1Api(api_client)
networking_v1_api = client.NetworkingV1Api(api_client)
rbac_v1_api = client.RbacAuthorizationV1Api(api_client)

def load_yaml_file(file_path):
    """
    Load a YAML file and return a list of its contents (supports multi-document YAML).
    """
    with open(file_path, 'r') as f:
        return list(yaml.safe_load_all(f))

def wait_for_namespace(api_instance, namespace, timeout=60):
    """
    Wait until the specified namespace is available.
    """
    print(f"Waiting for namespace '{namespace}' to be available...")
    start_time = time.time()
    while True:
        try:
            api_instance.read_namespace(name=namespace)
            print(f"Namespace '{namespace}' is ready")
            return True
        except client.ApiException as e:
            if e.status == 404:
                if time.time() - start_time > timeout:
                    raise Exception(f"Timeout waiting for namespace '{namespace}' to be created")
                time.sleep(1)
            else:
                raise e

def apply_manifest(api_client, manifest, namespace=None):
    """
    Apply a Kubernetes manifest using the appropriate API.
    """
    if manifest is None:
        return
    kind = manifest.get('kind')
    api_version = manifest.get('apiVersion')
    metadata = manifest.get('metadata', {})
    name = metadata.get('name')

    print(f"Applying {kind} '{name}'...")

    if kind == 'Namespace':
        v1_api = client.CoreV1Api(api_client)
        v1_api.create_namespace(body=manifest)
    elif kind == 'Deployment':
        apps_v1 = client.AppsV1Api(api_client)
        apps_v1.create_namespaced_deployment(namespace=namespace, body=manifest)
    elif kind == 'Service':
        v1 = client.CoreV1Api(api_client)
        v1.create_namespaced_service(namespace=namespace, body=manifest)
    elif kind == 'ConfigMap':
        v1 = client.CoreV1Api(api_client)
        v1.create_namespaced_config_map(namespace=namespace, body=manifest)
    elif kind == 'Role':
        rbac_v1 = client.RbacAuthorizationV1Api(api_client)
        rbac_v1.create_namespaced_role(namespace=namespace, body=manifest)
    elif kind == 'RoleBinding':
        rbac_v1 = client.RbacAuthorizationV1Api(api_client)
        rbac_v1.create_namespaced_role_binding(namespace=namespace, body=manifest)
    elif kind == 'Ingress':
        networking_v1 = client.NetworkingV1Api(api_client)
        networking_v1.create_namespaced_ingress(namespace=namespace, body=manifest)
    elif kind == 'NetworkPolicy':
        networking_v1 = client.NetworkingV1Api(api_client)
        networking_v1.create_namespaced_network_policy(namespace=namespace, body=manifest)
    else:
        print(f"Skipping unsupported kind: {kind}")
        return

    print(f"Successfully applied {kind} '{name}'")


def get_loadbalancer_url(networking_api_instance, api_instance, namespace, ingress_name, 
                         service_name="nginx-ingress-ingress-nginx-controller", 
                         ingress_namespace="ingress-nginx", timeout=300):
    
    # Try to retrieve the domain from the Ingress with retries
    domain = None
    retries = 5
    delay = 2
    print(f"Attempting to retrieve domain from Ingress '{ingress_name}' in namespace '{namespace}'...")
    for attempt in range(retries):
        try:
            ingress = networking_api_instance.read_namespaced_ingress(name=ingress_name, namespace=namespace)
            domain = ingress.spec.rules[0].host if ingress.spec.rules else None
            if domain:
                print(f"Retrieved domain '{domain}' from Ingress '{ingress_name}'")
                break
            print(f"No host found in Ingress '{ingress_name}' on attempt {attempt + 1}/{retries}")
        except client.ApiException as e:
            print(f"Attempt {attempt + 1}/{retries} failed to retrieve Ingress '{ingress_name}': {e}")
        time.sleep(delay)
    
    if domain:
        # Use the domain from Ingress with HTTPS
        url = f"https://{domain}/{namespace}"
        print(f"Access URL is: {url}")
        return url
    
    # Fallback to LoadBalancer IP if no domain is retrieved
    print(f"Failed to retrieve domain after {retries} attempts. Waiting for LoadBalancer endpoint for service '{service_name}' in namespace '{ingress_namespace}'...")
    start_time = time.time()
    while True:
        try:
            service = api_instance.read_namespaced_service(name=service_name, namespace=ingress_namespace)
            if service.status.load_balancer.ingress:
                ingress = service.status.load_balancer.ingress[0]
                if ingress.hostname:
                    endpoint = ingress.hostname
                elif ingress.ip:
                    endpoint = ingress.ip
                else:
                    raise Exception(f"No valid IP or hostname found in LoadBalancer ingress for '{service_name}'")
                url = f"http://{endpoint}/{namespace}"
                print(f"LoadBalancer URL is ready: {url}")
                return url
            if time.time() - start_time > timeout:
                raise Exception(f"Timeout waiting for LoadBalancer endpoint for '{service_name}' in '{ingress_namespace}'")
            time.sleep(5)
        except client.ApiException as e:
            if e.status == 404:
                raise Exception(f"Service '{service_name}' not found in namespace '{ingress_namespace}'")
            else:
                raise e

# ------------------------------------------------------------------------------------------
def create_dspaces_resources(user_id: str):
    """
    Create all Kubernetes resources for a user's dspaces instance in a unique namespace.
    """
    # Generate unique namespace
    print(f'user id: {user_id} passed to create_dspaces_resources')
    namespace = f"dspaces-{user_id}"
    print(f'namespace : {namespace} created in create_dspaces_resources')
    # Define base directory for manifests
    manifest_dir = Path(__file__).parent / "k8s"

    # Create namespace
    namespace_manifest = {
        "apiVersion": "v1",
        "kind": "Namespace",
        "metadata": {"name": namespace}
    }
    try:
        apply_manifest(api_client, namespace_manifest)
    except client.ApiException as e:
        if e.status != 409:  # Namespace already exists
            raise e

    # Wait for namespace to be ready
    wait_for_namespace(v1_api, namespace)

    # Apply each manifest with namespace substitution
    for file_path in manifest_dir.glob("*.yaml"):  # Only process .yaml files
        if file_path.is_file():  # Ensure it’s a file, not a subdirectory
            manifests = load_yaml_file(file_path)
            for manifest in manifests:
                if manifest:
                    manifest["metadata"]["namespace"] = namespace
                    apply_manifest(api_client, manifest, namespace)

    # Apply network policy for isolation
    network_policy = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "NetworkPolicy",
        "metadata": {"name": f"dspaces-{user_id}-isolation", "namespace": namespace},
        "spec": {
            "podSelector": {"matchLabels": {"app": "dspaces-api", "user": user_id}},
            "policyTypes": ["Ingress"],
            "ingress": [{
                "from": [{"ipBlock": {"cidr": "0.0.0.0/0"}}],  # Adjust based on user IP or client (e.g., Ingress)
                "ports": [{"port": 8001, "protocol": "TCP"}]
            }]
        }
    }
    apply_manifest(api_client, network_policy, namespace)

    ingress_name = f"dspaces-api-ingress-{user_id}"
    # Dynamically create Ingress manifest
    ingress_manifest = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": ingress_name,
            "namespace": namespace,
            "annotations": {
                "nginx.ingress.kubernetes.io/rewrite-target": "/$2",
                "nginx.ingress.kubernetes.io/use-regex": "true",
                "cert-manager.io/cluster-issuer": "letsencrypt-prod"
            }
        },
        "spec": {
            "ingressClassName": "nginx",
            "tls": [{
                "hosts": ["vdc-190.chpc.utah.edu"], # Domain for the certificate
                "secretName": f"tls-{namespace}"  # Create a secret with the TLS certificate and key for the domain
            }],
            "rules": [{
                "host": "vdc-190.chpc.utah.edu", # Match the TLS host
                "http": {
                    "paths": [{
                        "path": f"/{namespace}(/|$)(.*)",
                        "pathType": "ImplementationSpecific",
                        "backend": {
                            "service": {
                                "name": "dspaces-api-service",
                                "port": {"number": 8001}
                            }
                        }
                    }]
                }
            }]
        }
    }
    apply_manifest(api_client, ingress_manifest, namespace)

    # Get access URL
    access_url = get_loadbalancer_url(networking_v1_api, v1_api, namespace, ingress_name, ingress_namespace="ingress-nginx")
    return {"dspaces access url": access_url}