[![CI Pipeline](https://github.com/sci-ndp/pop/actions/workflows/ci.yml/badge.svg)](https://github.com/sci-ndp/pop/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-51%25-yellow.svg)](https://github.com/sci-ndp/pop/actions)
[![Flake8](https://img.shields.io/badge/flake8-passing-brightgreen.svg)](https://github.com/sci-ndp/pop/actions)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
# Point Of Presence API (POP API)

A RESTful API to manage and interact with Point of Presence (POP) resources. The POP API provides endpoints for creating, retrieving, updating, and deleting the resources.

## Table of Contents

- [Installation](#installation)
- [Tutorial](#tutorial)
- [Usage](#usage)
- [Optional Integrations](#optional-integrations)
- [System Metrics Logging](#system-metrics-logging)
- [Running Tests](#running-tests)
- [Contributing](#contributing)
- [License](#license)

## Installation

This repository requires Docker and Docker Compose to be installed on your system. We recommend always downloading and using the [latest release available](https://github.com/sci-ndp/pop/releases), but you can also clone the repository to access the most recent code.

1. **Clone the repository** (optional for latest release):

2. **Create the `.env` files**:  
   Create a `.env` file at the project root. Use the provided `example.env` file as a template, and set your configuration values appropriately.

3. **Start the Docker containers**:
   A script named `./start-dockers.sh` has been created to handle all necessary steps for running the Docker containers.

   ```bash
   ./start-dockers.sh
   ```

4. **Access the API**:
   By default, the API will be accessible at `http://localhost:8001`. You can modify this port in the Docker Compose configuration file if needed.

## Usage

For detailed usage instructions and endpoint descriptions, refer to the API swagger documentation, accessible once the server is running at `/docs`.

## Optional Integrations

The POP API provides core functionalities:

- Data management via an internal CKAN instance.
- Data searching across internal/external CKAN instances.
- Authentication and authorization via Keycloak.

Additional optional integrations can be enabled in the main `.env` file to enhance functionality:

- **Kafka Integration**: Enables Kafka integration for real-time streaming.
- **JupyterLab Integration**: Adds JupyterLab access directly from the dashboard.
- **DXSpaces Integration**: Enables DXSpaces (data staging service) access from the dashboard.

## System Metrics Logging

The POP API periodically logs essential system metrics, including:

- **Public IP address**
- **CPU usage**
- **Memory usage**
- **Disk usage**
- **Organization identification**

Additionally, it provides information about currently enabled and connected external services such as Kafka, JupyterLab, and CKAN instances.

### How It Works

Every 10 minutes (adjustable interval), the API logs these metrics in JSON format for easy integration with log-monitoring tools or further analysis.

### Organization Configuration

To identify which organization is running the POP installation, set the `ORGANIZATION` environment variable in your `.env` file:

```env
ORGANIZATION=University of Utah
```

If not configured, the system will use "Unknown Organization" as the default value.

### Example of Logged Metrics

The logs follow this structured JSON format:

```json
{
  "public_ip": "XXX.XXX.XXX.XXX",
  "cpu": "10%",
  "memory": "60%",
  "disk": "20%",
  "version": "0.6.0",
  "organization": "University of Utah",
  "services": {
    "jupyter": "https://jupyter.org/try-jupyter/lab/",
    "pre_ckan": "http://localhost:5000",
    "local_ckan": "http://localhost:5000",
    "kafka": {
      "host": "localhost",
      "port": 9092,
      "prefix": "data_stream_"
    }
  }
}
```

### Sending Metrics to External Endpoint (Optional)

If your API is configured to run publicly (`public=True` in `swagger_settings`), it will automatically send (POST) the metrics payload shown above to an external endpoint defined by the configuration setting `metrics_endpoint`.

To enable or disable sending metrics externally, adjust the following in `env_variables/.env_swagger`:

```env
PUBLIC=True
METRICS_ENDPOINT=http://your-external-endpoint.com/metrics
ORGANIZATION=University of Utah
```

- Set `PUBLIC=True` to enable metrics forwarding.
- Set the `METRICS_ENDPOINT` to your desired metrics collection endpoint.
- Set `ORGANIZATION` to identify your institution in the metrics data.

Ensure your external endpoint can accept POST requests with JSON payloads in the format described above.

### Troubleshooting

- If metrics are not sent correctly, verify that your external endpoint is reachable from your API instance.
- Check logs for error messages related to metrics collection or sending.
- Verify that the `ORGANIZATION` field is properly configured if you need to identify your POP installation.

## Running Tests

To run the tests, navigate to the project root and execute:

```bash
pytest
```

## Running Tests

To run the tests, navigate to the project root and execute:

```bash
pytest
```

Alternatively, since the Docker container `pop-api` has a Python environment with all necessary libraries, you can run the tests within the Docker container:

```bash
docker exec -it pop-api pytest
```

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a new branch** (`git checkout -b feature/new-feature`)
3. **Make your changes** and **commit** (`git commit -m 'Add new feature'`)
4. **Push** to the branch (`git push origin feature/new-feature`)
5. **Open a Pull Reques**

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/sci-ndp/pop-py/blob/main/LICENSE) file for details.
