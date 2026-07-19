import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

# Import Core Refactored Modules
from core.context.container import Container
from core.events.bus import EventBus
from core.permissions.manager import PermissionManager
from core.reasoning.reasoner import Reasoner
from core.planner.planner import Planner
from core.execution.executor import Executor
from core.interfaces.tool import BaseTool
from storage.sqlite.connection import SQLiteConfigRepository
from storage.vector.chromadb import ChromaMemoryRepository

# Import Application Services
from services.memory.service import MemoryService

# Import Monitoring
from monitoring.health import HealthMonitor
from monitoring.telemetry import TelemetrySystem

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ultron_backend")

# Initialize the Dependency Injection Container
container = Container()


# Setup Lifespan/Startup
async def setup_dependencies() -> None:
    # 1. Core Event Bus & Storage Repositories
    event_bus = EventBus()

    config_repository = SQLiteConfigRepository(db_path="ultron.db")
    await config_repository.connect()

    memory_repository = ChromaMemoryRepository(persist_directory="vector_store")
    await memory_repository.connect()

    # 1a. AI Configuration System
    from services.ai.config import ModelConfigLoader

    config_loader = ModelConfigLoader()
    ai_config = config_loader.get_config()

    # 1b. Shared HTTP Connection Pool and Transport
    from core.transport.http import HTTPClientFactory, TimeoutPolicy, RetryPolicy
    from core.transport import AsyncHTTPTransport

    timeout_policy = TimeoutPolicy(
        connect=5.0,
        read=ai_config.ollama.timeout,
        write=10.0,
        pool=5.0,
    )
    retry_policy = RetryPolicy()

    http_client = HTTPClientFactory.get_client()
    http_transport = AsyncHTTPTransport(
        client=http_client,
        timeout_policy=timeout_policy,
        retry_policy=retry_policy,
    )

    # 1c. Provider Registry & Discovery
    from services.ai.registry import ModelRegistry
    from services.ai.discovery import ProviderDiscovery

    provider_registry = ModelRegistry()

    provider_discovery = ProviderDiscovery(registry=provider_registry)
    provider_discovery.discover_and_register("services.ai")

    # 1d. Model Manager & Configuration registration
    from services.ai.manager import ModelManager
    from services.ai.models import ModelMetadata

    model_manager = ModelManager(registry=provider_registry)

    for model_id, model_config in ai_config.models.items():
        try:
            model_manager.register_model(model_id, model_config, ModelMetadata())
        except Exception as e:
            logger.warning(
                f"Could not register model config '{model_id}' on startup: {e}"
            )

    # 2. Setup Telemetry monitoring for events
    _telemetry = TelemetrySystem(event_bus=event_bus)

    # 3. Permissions Manager
    permission_manager = PermissionManager()

    # 4. AI Reasoning & High-level Planner
    reasoner = Reasoner(model_name="ultron-llama3-local")
    planner = Planner(reasoner=reasoner)

    # 5. Core Services
    memory_service = MemoryService(memory_repository=memory_repository)

    # 6. Tool Resolver & Tool Registry initialization
    from tools.registry import ToolRegistry
    from tools.manager import ToolManager

    registry = ToolRegistry()
    manager = ToolManager(registry=registry)
    # Autodiscover tools from the 'tools' package
    manager.discover_tools(package_name="tools")

    async def tool_resolver(name: str) -> BaseTool:
        return registry.get(name)

    # 7. Execution Engine
    executor = Executor(
        permission_manager=permission_manager,
        event_bus=event_bus,
        tool_resolver=tool_resolver,
    )

    # 8. Register dependencies in the container
    container.event_bus = event_bus
    container.config_repository = config_repository
    container.memory_repository = memory_repository
    container.memory = memory_service
    container.reasoner = reasoner
    container.planner = planner
    container.executor = executor
    container.permission_manager = permission_manager

    # DI Wiring for Infrastructure
    container.config_loader = config_loader
    container.http_transport = http_transport
    container.provider_registry = provider_registry
    container.model_manager = model_manager

    # 9. Health verification during startup
    logger.info("Verifying core services health diagnostics on startup...")
    try:
        from monitoring.health import HealthMonitor

        monitor = HealthMonitor(config_repository=config_repository)
        health_status = await monitor.check_health()
        if health_status.get("status") != "healthy":
            logger.warning(f"Core services startup check degraded: {health_status}")
        else:
            logger.info("Startup health verification check successful.")
    except Exception as e:
        logger.error(f"Startup health verification check failed: {e}")

    logger.info("ULTRON AI Core dependencies successfully registered in container")


# FastAPI Application Setup
app = FastAPI(
    title="ULTRON AI - Core OS Backend",
    description="Production-grade local-first backend for the ULTRON AI Operating System.",
    version="1.0.0",
)


@app.on_event("startup")
async def on_startup() -> None:
    await setup_dependencies()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    try:
        await container.config_repository.disconnect()
        await container.memory_repository.disconnect()

        # Graceful shutdown of HTTP client pool
        from core.transport.http import HTTPClientFactory

        await HTTPClientFactory.close_client()
        logger.info("Graceful shutdown of HTTP client pool completed.")
    except Exception as e:
        logger.error(
            f"Error disconnecting repositories/HTTP client pool on shutdown: {e}"
        )


# Request Models
class GoalRequest(BaseModel):
    goal: str


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """System status and connection health checks diagnostics."""
    try:
        monitor = HealthMonitor(config_repository=container.config_repository)
        status = await monitor.check_health()
        return status
    except Exception as e:
        logger.error(f"Health check diagnostics error: {e}")
        raise HTTPException(status_code=500, detail="Health check degraded")


@app.post("/workflow/plan")
async def create_workflow_plan(request: GoalRequest) -> Dict[str, Any]:
    """Generate an execution plan workflow for a high-level goal."""
    try:
        workflow = await container.planner.create_plan(goal=request.goal)
        return {
            "workflow_id": workflow.id,
            "goal": workflow.goal,
            "steps": workflow.steps,
            "status": workflow.status,
        }
    except Exception as e:
        logger.error(f"Failed to generate workflow plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))
