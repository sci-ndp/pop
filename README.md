[![Contributor Covenant](https://img.shields.io/badge/code%20of%20conduct-Contributor%20Covenant-brightgreen.svg)](CODE_OF_CONDUCT.md)

# Point Of Presence API (POP API)

A RESTful API to manage and interact with Point of Presence (POP) resources. The POP API provides endpoints for creating, retrieving, updating, and deleting the resources.

## Table of Contents

- [Installation](#installation)
- [Tutorial](#tutorial)
- [Running Tests](#running-tests)
- [Contributing](#contributing)
- [License](#license)

## Installation

This repository requires Docker and Docker Compose to be installed on your system. We recommend always downloading and using the [latest release available](https://github.com/sci-ndp/pop/releases), but you can also clone the repository to access the most recent code.

1. **Clone the repository** (optional for latest release):

2. **Create the `.env` files**:  
   In the `.env_variables` folder, you will find template files named `example.env_*`. These serve as templates for the required `.env_*` files. Copy these files and rename them as `.env_*`, adjusting values as needed.

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

The POP API provides core functionalities for managing and interacting with POP resources. These core features include:

- Managing and handling data within an internal CKAN instance.
- Searching for data across the internal CKAN instance and external CKAN instances.
- Authentication and authorization via Keycloak.

In addition to these core capabilities, the POP API also supports optional configurations to connect with other services being developed in SciDx. These integrations are designed to enhance functionality but are not required for the basic operation of the API:

1. **Kafka Integration**:  
   Enables the POP API to connect with a Kafka broker for real-time data streaming. To configure this integration, use the `.env_kafka` file located in the `env_variables` directory.

2. **JupyterLab Integration**:  
   Adds a link to a JupyterLab instance on the main page of the API, enabling users to access it directly. To enable this integration, configure the following variables in the `env_variables/.env_swagger` file:
   - `USE_JUPYTERLAB`: Set to `True` to enable the integration (default: `False`).
   - `JUPYTER_URL`: Specify the URL of the JupyterLab instance to be linked.

These optional features allow the POP API to seamlessly integrate with other components in SciDx, providing extended capabilities for specialized use cases.


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
