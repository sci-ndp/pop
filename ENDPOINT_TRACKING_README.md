# Endpoint Tracking Implementation

This implementation adds comprehensive endpoint tracking functionality to the POP API, following the established patterns and architecture of the codebase.

## 🏗️ Architecture Overview

The endpoint tracking system follows the existing API structure:

```
api/
├── middleware/
│   ├── __init__.py
│   └── endpoint_tracking_middleware.py    # Middleware for automatic tracking
├── models/
│   └── endpoint_tracking_model.py         # Data model for tracking requests
├── services/
│   └── tracking_services/
│       ├── __init__.py
│       └── endpoint_tracker.py            # Business logic for tracking
├── routes/
│   └── tracking_routes/
│       ├── __init__.py
│       └── get_tracking_status.py         # Status endpoint for tracking
└── main.py                                # Middleware integration
```

## 🔧 Implementation Details

### 1. Middleware Integration
The `EndpointTrackingMiddleware` automatically tracks all API requests:

```python
# Added to main.py
app.add_middleware(EndpointTrackingMiddleware)
```

### 2. Automatic Tracking
Every **successful** endpoint call is automatically logged with the following information:
- **Endpoint**: The requested path
- **Method**: HTTP method (GET, POST, PUT, DELETE, etc.)
- **Client ID**: From environment variable `CLIENT_ID`
- **Organization**: From environment variable `ORGANIZATION`
- **Timestamp**: ISO 8601 formatted timestamp
- **User Agent**: Browser/client information
- **Remote Address**: Client IP address
- **Status Code**: HTTP response status (2xx only)
- **Request Data**: Key request parameters (e.g., organization name, search terms)
- **Query Parameters**: URL query parameters

### 3. Success-Only Logging
Only successful requests (HTTP status codes 200-299) are logged. This ensures:
- ✅ **Clean logs**: No noise from failed requests
- ✅ **Meaningful data**: Only track actual successful operations
- ✅ **Security**: Error details are not exposed in tracking logs

### 4. Request Data Extraction
The system intelligently extracts relevant data based on the endpoint:

**Organization Endpoints** (`/organization`):
- POST: `name`, `title`, `description`
- GET: `name`

**Search Endpoints** (`/search`):
- GET/POST: `search_term`, `dataset_name`, `dataset_title`, `owner_org`, `resource_format`

**Data Source Endpoints** (`/kafka`, `/s3`, `/url`, `/services`):
- POST/PUT: `dataset_name`, `dataset_title`, `owner_org`, specific resource fields

**General Dataset Endpoints** (`/general-dataset`):
- POST/PUT/PATCH: `name`, `title`, `owner_org`, `notes`

### 5. External API Integration
All tracking data is sent to an external API endpoint for centralized analytics:

```json
{
  "endpoint": "/organization",
  "method": "POST",
  "client_id": "your_client_id",
  "organization": "Your Organization Name",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "user_agent": "Mozilla/5.0...",
  "remote_addr": "192.168.1.100",
  "status_code": 201,
  "request_data": {
    "name": "research_org",
    "title": "Research Organization",
    "description": "Organization for research projects"
  },
  "query_params": {
    "server": "local"
  }
}
```

**HTTP POST Details:**
- **URL**: `ENDPOINT_TRACKING_API_URL` from environment
- **Method**: POST
- **Content-Type**: application/json
- **Headers**: 
  - `X-Client-ID`: Your client ID
  - `X-Organization`: Your organization name
  - `User-Agent`: POP-API version info
- **Timeout**: 10 seconds
- **Retry Logic**: Graceful failure (logs warning, continues operation)

### 6. Local + External Logging
The system provides dual logging:
- **Local**: JSON logs in `logs/metrics.log` for debugging
- **External**: HTTP POST to your analytics endpoint for centralized tracking
- **Fallback**: If external API fails, local logging continues uninterrupted
```

### 7. Configuration
The tracking system uses the existing configuration pattern:

```python
# From .env file
CLIENT_ID=your_client_id
ORGANIZATION="Your Organization Name"
ENDPOINT_TRACKING_ENABLED=True  # Enable/disable tracking
ENDPOINT_TRACKING_API_URL=https://api.example.com/endpoint-tracking  # External API endpoint
```

## 🚀 Usage

### Automatic Tracking
Once deployed, all successful API endpoints are automatically tracked. No additional code is required in individual route handlers.

### Optional Tracking
Tracking can be enabled or disabled via environment variable:
```bash
# Enable tracking
ENDPOINT_TRACKING_ENABLED=True

# Disable tracking
ENDPOINT_TRACKING_ENABLED=False
```

### Excluded Paths
The following paths are excluded from tracking to reduce noise:
- `/` (root/home page)
- `/static/*` (static files)
- `/favicon.ico`
- `/docs` (Swagger documentation)
- `/openapi.json`
- `/redoc`

### Viewing Tracking Status
Access the tracking status endpoint:
```
GET /tracking/tracking-status
```

Response:
```json
{
  "tracking_enabled": true,
  "client_id": "your_client_id", 
  "organization": "Your Organization Name",
  "success_only": true,
  "request_data_tracking": true,
  "message": "Endpoint tracking is active and configured"
}
```

## 📊 Real-World Examples

### Organization Creation
When a user creates an organization named "climate_research":
```json
{
  "endpoint": "/organization",
  "method": "POST",
  "client_id": "your_client_id",
  "organization": "Your Organization Name",
  "status_code": 201,
  "request_data": {
    "name": "climate_research",
    "title": "Climate Research Organization",
    "description": "Organization for climate data analysis"
  },
  "query_params": {
    "server": "local"
  }
}
```

### Data Search
When a user searches for "weather data":
```json
{
  "endpoint": "/search",
  "method": "GET",
  "client_id": "your_client_id",
  "organization": "Your Organization Name", 
  "status_code": 200,
  "request_data": {
    "search_term": "weather data",
    "owner_org": "climate_research"
  },
  "query_params": {
    "server": "local",
    "limit": "20"
  }
}
```

### Kafka Dataset Registration
When a user registers a Kafka topic "temperature_sensors":
```json
{
  "endpoint": "/kafka",
  "method": "POST",
  "client_id": "your_client_id",
  "organization": "Your Organization Name",
  "status_code": 201,
  "request_data": {
    "dataset_name": "temperature_data",
    "dataset_title": "Temperature Sensor Data",
    "owner_org": "climate_research",
    "kafka_topic": "temperature_sensors"
  }
}
```

## 📊 Log Analysis

### Finding Tracking Logs
All tracking logs are prefixed with `ENDPOINT_TRACKING:` for easy filtering:

```bash
# View all endpoint tracking logs
grep "ENDPOINT_TRACKING:" logs/metrics.log

# View specific endpoint tracking
grep "ENDPOINT_TRACKING:" logs/metrics.log | grep "/organization"

# View specific HTTP methods
grep "ENDPOINT_TRACKING:" logs/metrics.log | grep "POST"
```

### Log Format
Each log entry contains:
1. Standard log prefix with timestamp and level
2. `ENDPOINT_TRACKING:` identifier
3. JSON payload with tracking data

Example log entry:
```
2025-01-15 10:30:00 [INFO] api.services.tracking_services.endpoint_tracker: ENDPOINT_TRACKING: {"endpoint": "/organization", "method": "POST", "client_id": "your_client_id", "organization": "Your Organization Name", "timestamp": "2025-01-15T10:30:00.000Z", "user_agent": "curl/7.68.0", "remote_addr": "192.168.1.100", "status_code": 201}
```

## 🧪 Testing

The implementation includes comprehensive tests:

```bash
# Run endpoint tracking tests
pytest tests/test_endpoint_tracking.py -v

# Run all tests
pytest tests/ -v
```

## 🔒 Security Considerations

1. **Data Privacy**: Only metadata is logged, not request/response bodies
2. **IP Handling**: Respects proxy headers (X-Forwarded-For, X-Real-IP)
3. **Error Handling**: Graceful degradation if tracking fails
4. **Configuration**: Sensitive data comes from environment variables

## 📈 Performance Impact

- **Minimal Overhead**: Logging is asynchronous and non-blocking
- **Selective Tracking**: Static files and documentation are excluded
- **Error Isolation**: Tracking failures don't affect API responses
- **Structured Data**: JSON format for efficient log parsing

## 🔧 Customization

### Adding Custom Tracking Data
Extend the `EndpointTrackingRequest` model in `endpoint_tracking_model.py`:

```python
class EndpointTrackingRequest(BaseModel):
    # ... existing fields ...
    custom_field: Optional[str] = Field(None, description="Custom tracking data")
```

### Modifying Excluded Paths
Update the `exclude_paths` list in `endpoint_tracking_middleware.py`:

```python
self.exclude_paths = [
    "/",
    "/static",
    "/favicon.ico",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/your-custom-path"  # Add custom exclusions
]
```

### Custom Log Format
Modify the `log_endpoint_access` function in `endpoint_tracker.py` to change the log format or add additional processing.

## 🚦 Key Features Summary

✅ **Success-Only Logging**: Only successful requests (2xx status codes) are tracked
✅ **Request Data Extraction**: Intelligent extraction of meaningful request parameters
✅ **Optional Tracking**: Can be enabled/disabled via `ENDPOINT_TRACKING_ENABLED` environment variable
✅ **Structured JSON Logs**: Easy to parse and analyze
✅ **Zero Configuration**: Works out of the box with existing endpoints
✅ **Performance Optimized**: Minimal overhead, non-blocking logging
✅ **Security Conscious**: No sensitive data logged, only metadata and key parameters

1. **Environment Variables**: Ensure `CLIENT_ID` and `ORGANIZATION` are set in your `.env` file
2. **Log Rotation**: The existing log rotation handles tracking logs automatically
3. **Monitoring**: Use the `/tracking/tracking-status` endpoint for health checks
4. **Backward Compatibility**: All existing functionality remains unchanged

## 📚 Code Standards Compliance

This implementation strictly follows the existing codebase patterns:

- ✅ **Services Pattern**: Business logic in separate service modules
- ✅ **Model-Based**: Pydantic models for data validation
- ✅ **Configuration Management**: Environment-based configuration
- ✅ **Error Handling**: Comprehensive error handling and logging
- ✅ **Testing**: Full test coverage following existing patterns
- ✅ **Documentation**: Comprehensive inline and API documentation
- ✅ **Route Structure**: Consistent with existing route organization
- ✅ **Middleware Integration**: Proper FastAPI middleware implementation

The tracking system seamlessly integrates with the existing codebase without disrupting any current functionality while providing powerful endpoint monitoring capabilities.
