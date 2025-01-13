# api/routes/status_routes/kafka_details.py

from fastapi import APIRouter, HTTPException
from api.config.kafka_settings import kafka_settings

router = APIRouter()


@router.get(
    "/kafka-details",
    summary="Get Kafka connection details",
    description="Returns Kafka host, port, and connection status.",
)
async def get_kafka_details():
    """
    Endpoint to retrieve Kafka connection details.

    Returns
    -------
    dict
        Kafka connection details including host, port, and connection status.

    Raises
    ------
    HTTPException
        If there is an error retrieving Kafka details, an HTTPException
        is raised with a 500 status code.
    """
    try:
        return {
            "kafka_host": kafka_settings.kafka_host,
            "kafka_port": kafka_settings.kafka_port,
            "kafka_connection": kafka_settings.kafka_connection,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving Kafka details: {str(e)}")
