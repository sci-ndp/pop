# Modular Registration Architecture

## Overview
This document outlines the architecture for a modular registration system that allows dynamic handling of different resource types through a plugin-based architecture.

## Directory Structure
```
api/
├── modules/
│   ├── __init__.py
│   ├── base.py           # Base module interface
│   ├── registry.py       # Module registry
│   ├── kafka_module.py   # Kafka implementation
│   ├── s3_module.py      # S3 implementation
│   └── url_module.py     # URL implementation
├── services/
│   └── registration_service.py  # Unified registration logic
└── routes/
    └── register_routes/
        └── register.py    # Unified registration endpoint
```

## Core Components

### 1. Base Module Interface
The foundation for all registration modules.

```python
# api/modules/base.py

class BaseModuleValidator:
    """
    Base class for module-specific validation models
    Define common validation rules here
    """
    pass

class BaseModule:
    """
    Abstract base class that all registration modules must implement
    """
    @property
    def name(self) -> str:
        """Unique identifier for the module"""
        pass

    @property
    def validator(self) -> type[BaseModuleValidator]:
        """Returns the validator class for this module"""
        pass

    def can_handle(self, metadata: dict) -> bool:
        """
        Determines if this module can process the given metadata
        Returns: True if module can handle the metadata
        """
        pass

    def enrich_metadata(self, metadata: dict) -> dict:
        """
        Adds module-specific fields to metadata
        Returns: Enriched metadata dictionary
        """
        pass

    async def process_registration(self, metadata: dict, ckan_instance) -> str:
        """
        Processes the registration for this module
        Returns: Resource ID if successful
        """
        pass
```

### 2. Module Implementation Example
Example of a concrete module implementation.

```python
# api/modules/kafka_module.py

class KafkaValidator(BaseModuleValidator):
    required_fields = {
        "kafka_topic": str,
        "kafka_host": str,
        "kafka_port": int
    }

class KafkaModule(BaseModule):
    name = "kafka"
    validator = KafkaValidator

    def can_handle(self, metadata):
        # Check if metadata contains required Kafka fields
        return all(key in metadata for key in ["kafka_topic", "kafka_host"])

    def enrich_metadata(self, metadata):
        # Add Kafka-specific metadata
        enriched = metadata.copy()
        enriched["type"] = "kafka_resource"
        return enriched

    async def process_registration(self, metadata, ckan_instance):
        # Validate and process Kafka registration
        # Return resource ID
        pass
```

### 3. Module Registry
Central registry for managing available modules.

```python
# api/modules/registry.py

class ModuleRegistry:
    _modules = {}

    @classmethod
    def register(cls, module_class):
        """Register a new module"""
        cls._modules[module_class.name] = module_class

    @classmethod
    def get_module(cls, name):
        """Get module by name"""
        return cls._modules.get(name)

    @classmethod
    def get_all_modules(cls):
        """Get all registered modules"""
        return list(cls._modules.values())
```

### 4. Registration Service
Core service handling the registration logic.

```python
# api/services/registration_service.py

class RegistrationService:
    @staticmethod
    async def register_resource(metadata: dict, server: str = "local"):
        """
        Main registration flow:
        1. Find compatible modules
        2. Enrich metadata
        3. Process registration with all compatible modules
        4. Return results
        """
        # Get appropriate CKAN instance
        ckan_instance = get_ckan_instance(server)

        # Find compatible modules
        compatible_modules = [
            module() for module in ModuleRegistry.get_all_modules()
            if module().can_handle(metadata)
        ]

        if not compatible_modules:
            raise ValidationError("No compatible module found")

        # Enrich metadata
        enriched_metadata = metadata.copy()
        for module in compatible_modules:
            enriched_metadata = module.enrich_metadata(enriched_metadata)

        # Process registration
        results = []
        for module in compatible_modules:
            result = await module.process_registration(
                enriched_metadata,
                ckan_instance
            )
            results.append({"module": module.name, "id": result})

        return {"registrations": results}
```

### 5. Registration Endpoint
Unified API endpoint for registration.

```python
# api/routes/register_routes/register.py

@router.post("/register")
async def register_resource(
    request: RegistrationRequest,
    server: Literal["local", "pre_ckan"] = "local"
):
    """
    Unified registration endpoint that:
    1. Validates incoming request
    2. Calls registration service
    3. Returns registration results
    """
    return await RegistrationService.register_resource(
        request.metadata,
        server
    )
```

## Usage Example

### Adding a New Module

1. Create new module class:
```python
# api/modules/new_module.py

class NewModuleValidator(BaseModuleValidator):
    # Define validation rules
    pass

class NewModule(BaseModule):
    name = "new_module"
    validator = NewModuleValidator

    def can_handle(self, metadata):
        # Implement handling logic
        pass

    def enrich_metadata(self, metadata):
        # Implement enrichment logic
        pass

    async def process_registration(self, metadata, ckan_instance):
        # Implement registration logic
        pass
```

2. Register the module:
```python
# api/modules/registry.py

from .new_module import NewModule
ModuleRegistry.register(NewModule)
```

### API Usage Example

```http
POST /register?server=local
Content-Type: application/json

{
    "dataset_name": "example_dataset",
    "dataset_title": "Example Dataset",
    "owner_org": "org_id",
    "metadata": {
        "kafka_topic": "example_topic",
        "kafka_host": "kafka.example.com",
        "kafka_port": 9092,
        "extras": {
            "description": "Example dataset description"
        }
    }
}
```

## Benefits

1. **Modularity**: Each data source type is isolated in its own module
2. **Single Responsibility**: Each component has a clear, specific purpose
3. **Extensibility**: Easy to add new data source types
4. **Maintainability**: Changes to one module don't affect others
5. **Reusability**: Common functionality shared through base classes
6. **Validation**: Each module can define its own validation rules
7. **Flexibility**: Multiple modules can process the same metadata

## Testing Strategy

1. **Unit Tests**: Test each module in isolation
2. **Integration Tests**: Test module interactions
3. **End-to-End Tests**: Test complete registration flow
4. **Validation Tests**: Test input validation
5. **Error Handling Tests**: Test error scenarios

```

This architecture document provides a clear roadmap for implementing the modular registration system, including code structure, component interactions, and usage examples.