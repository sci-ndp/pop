# api\services\status_services\full_metrics.py
from .check_api_status import get_status
from .system_metrics import get_public_ip, get_system_metrics


def get_full_metrics():
    """
    Retrieve full system metrics including public IP, CPU, memory, disk,
    and the current status of all integrated services.
    """
    public_ip = get_public_ip()
    cpu, mem, disk = get_system_metrics()

    services_status = get_status()

    metrics = {
        "public_ip": public_ip,
        "cpu": f"{cpu}%",
        "memory": f"{mem}%",
        "disk": f"{disk}%",
        "services": services_status,
    }

    return metrics
