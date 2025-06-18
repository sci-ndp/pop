# api/routes/status_routes/kafka_details.py

from fastapi import APIRouter, HTTPException

from api.config.kafka_settings import kafka_settings

router = APIRouter()


@router.get(
    "/kafka-details",
    summary="Get Kafka connection details",
    description=(
        "Returns Kafka host, port, connection status, prefix, "
        "and max number of streams."
    ),
)
async def get_kafka_details():
    """
    Endpoint to retrieve Kafka connection details.

    Returns
    -------
    dict
        Kafka connection details including:
          - host (str)
          - port (int)
          - connection status (bool)
          - kafka_prefix (str, optional)
          - max_streams (int, optional)

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
            "kafka_prefix": kafka_settings.kafka_prefix,
            "max_streams": kafka_settings.max_streams,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving Kafka details: {str(e)}"
        )
