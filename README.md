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
