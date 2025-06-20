[![CI Pipeline](https://github.com/sci-ndp/pop/actions/workflows/ci.yml/badge.svg)](https://github.com/sci-ndp/pop/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-71%25-green.svg)](https://github.com/sci-ndp/pop/actions)
[![Flake8](https://img.shields.io/badge/flake8-passing-brightgreen.svg)](https://github.com/sci-ndp/pop/actions)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Point of Presence API (POP API)

A comprehensive **federated data management platform** that provides a unified REST API for managing datasets, streaming data, and integrating multiple data services. The POP API serves as a central point of access for data discovery, registration, and management across distributed CKAN instances, Kafka streams, and cloud storage.

## 🚀 Key Features

- **Federated Data Discovery**: Search and access datasets across multiple CKAN instances (local, global, pre-production)
- **Multi-format Data Sources**: Support for URLs, S3 buckets, Kafka streams, and various file formats (CSV, JSON, NetCDF, TXT)
- **Real-time Streaming**: Kafka integration for live data streams and event processing
- **Centralized Authentication**: Keycloak integration for secure, role-based access control
- **Service Registry**: Register and discover microservices and APIs
- **System Monitoring**: Built-in metrics collection and health monitoring
- **JupyterLab Integration**: Direct access to data analysis environments
- **RESTful API**: Comprehensive OpenAPI/Swagger documentation

## ⚡ Quick Start

Get the POP API running in under 5 minutes:

### Prerequisites
- Docker and Docker Compose
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/sci-ndp/pop.git
cd pop
```

### 2. Configure Environment
```bash
cp example.env .env
# Edit .env with your configuration (see Configuration section below)
```

### 3. Start the Services
```bash
docker-compose up -d
```

### 4. Access the API
- **API Documentation**: http://localhost:8001/docs
- **Dashboard**: http://localhost:8001/
- **Health Check**: http://localhost:8001/status/

## 🐳 Installation

### Option 1: Docker (Recommended)

1. **Clone and configure**:
   ```bash
   git clone https://github.com/sci-ndp/pop.git
   cd pop
   cp example.env .env
   ```

2. **Edit configuration** (see [Configuration](#configuration) section)

3. **Start services**:
   ```bash
   docker-compose up -d
   ```

### Option 2: Local Development

1. **Prerequisites**:
   ```bash
   # Python 3.9+
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp example.env .env
   # Edit .env file
   ```

4. **Run the application**:
   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## ⚙️ Configuration

### Core Services (Required)

```bash
# CKAN Configuration
CKAN_LOCAL_ENABLED=false           # Enable local CKAN instance
CKAN_URL=http://localhost:5000     # Your local CKAN URL
CKAN_GLOBAL_URL=https://global-ckan.example.com  # Global CKAN URL
CKAN_API_KEY=your-api-key         # CKAN API key

# Authentication
KEYCLOAK_URL=http://localhost:8080
REALM_NAME=your-realm
CLIENT_ID=your-client
CLIENT_SECRET=your-secret

# API Settings
SWAGGER_TITLE=POP API
SWAGGER_DESCRIPTION=Point of Presence Data Management API
ORGANIZATION=Your Organization Name
```

### Optional Integrations

```bash
# Kafka Streaming
KAFKA_CONNECTION=true
KAFKA_HOST=localhost
KAFKA_PORT=9092

# JupyterLab Integration
USE_JUPYTERLAB=true
JUPYTER_URL=https://jupyter.example.com

# DXSpaces Integration
USE_DXSPACES=true
DXSPACES_URL=https://dxspaces.example.com

# Pre-production CKAN
PRE_CKAN_ENABLED=true
PRE_CKAN_URL=https://pre-ckan.example.com
PRE_CKAN_API_KEY=pre-ckan-api-key
```

For a complete list of all environment variables, see the [example.env](example.env) file.

## 📖 Usage Examples

### Register a Dataset
```bash
# Register a CSV dataset
curl -X POST "http://localhost:8001/url" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "resource_name": "weather_data",
    "resource_title": "Weather Station Data",
    "owner_org": "research_org",
    "resource_url": "https://example.com/weather.csv",
    "file_type": "CSV",
    "notes": "Daily weather measurements"
  }'
```

### Search Datasets
```bash
# Search by organization
curl "http://localhost:8001/search?owner_org=research_org"

# Search with multiple terms
curl -X POST "http://localhost:8001/search" \
  -H "Content-Type: application/json" \
  -d '{
    "search_term": "weather,temperature",
    "resource_format": "csv"
  }'
```

### Register a Kafka Stream
```bash
curl -X POST "http://localhost:8001/kafka" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_name": "sensor_stream",
    "dataset_title": "IoT Sensor Stream",
    "owner_org": "iot_team",
    "kafka_topic": "sensors",
    "kafka_host": "localhost",
    "kafka_port": "9092"
  }'
```

### Code Standards
- **Style**: Black formatter, Flake8 linter
- **Documentation**: NumPy-style docstrings
- **Testing**: pytest with coverage
- **Type Hints**: Required for all functions

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api

# Run specific test file
pytest tests/test_routes.py

# Run in Docker container
docker exec -it pop-api pytest
```

## 🔧 Troubleshooting

### Common Issues

**API not starting**
```bash
# Check logs
docker logs pop-api

# Verify environment variables
docker exec -it pop-api env | grep CKAN
```

**CKAN connection issues**
- Verify CKAN_URL is accessible
- Check API key permissions
- Ensure firewall allows connections

**Keycloak authentication failing**
- Verify realm and client configuration
- Check client secret
- Confirm user exists in Keycloak

**Kafka streams not working**
- Verify Kafka broker is running
- Check topic exists
- Confirm network connectivity

### Performance Optimization
- Enable connection pooling for high traffic
- Configure appropriate worker processes
- Use Redis for session storage in production
- Set up database connection limits

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Steps
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `pytest`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📊 System Metrics

The POP API automatically collects and logs system metrics every 10 minutes:

```json
{
  "public_ip": "XXX.XXX.XXX.XXX",
  "cpu": "15%",
  "memory": "65%", 
  "disk": "45%",
  "version": "0.6.0",
  "organization": "Your Organization",
  "services": {
    "local_ckan": {"url": "http://localhost:5000"},
    "kafka": {"host": "localhost", "port": 9092}
  }
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [API Docs](http://localhost:8001/docs)
- **Issues**: [GitHub Issues](https://github.com/sci-ndp/pop/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sci-ndp/pop/discussions)
