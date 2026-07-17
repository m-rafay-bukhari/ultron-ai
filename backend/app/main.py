import logging
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

# Import Core Refactored Modules
from core.context.container import Container
from core.events.bus import EventBus
from core.permissions.manager import PermissionManager
from core.reasoning.reasoner import Reasoner
from core.planner.planner import Planner
from core.execution.executor import Executor
from storage.sqlite.connection import SQLiteStorage

# Import Application Services
from services.memory.service import MemoryService
from services.voice.service import VoiceService

# Import Monitoring
from monitoring.health import HealthMonitor
from monitoring.telemetry import TelemetrySystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ultron_backend")

# Initialize the Dependency Injection Container
container = Container()

# Setup Lifespan/Startup
async def setup_dependencies() -> None:
    # 1. Core Event Bus & Storage
    event_bus = EventBus()
    storage = SQLiteStorage(db_path="ultron.db")
    await storage.connect()

    # 2. Setup Telemetry monitoring for events
    telemetry = TelemetrySystem(event_bus=event_bus)

    # 3. Permissions Manager
    permission_manager = PermissionManager()

    # 4. AI Reasoning & High-level Planner
    reasoner = Reasoner(model_name="ultron-llama3-local")
    planner = Planner(reasoner=reasoner)

    # 5. Core Services
    memory_service = MemoryService(storage=storage)

    # 6. Tool Resolver & Tool Registry initialization
    from tools.registry import ToolRegistry
    from tools.manager import ToolManager
    
    registry = ToolRegistry()
    manager = ToolManager(registry=registry)
    # Autodiscover tools from the 'tools' package
    manager.discover_tools(package_name="tools")

    async def tool_resolver(name: str):
        return registry.get(name)

    # 7. Execution Engine
    executor = Executor(
        permission_manager=permission_manager,
        event_bus=event_bus,
        tool_resolver=tool_resolver
    )

    # 8. Register dependencies in the container
    container.event_bus = event_bus
    container.storage = storage
    container.memory = memory_service
    container.reasoner = reasoner
    container.planner = planner
    container.executor = executor
    container.permission_manager = permission_manager

    logger.info("ULTRON AI Core dependencies successfully registered in container")


# FastAPI Application Setup
app = FastAPI(
    title="ULTRON AI - Core OS Backend",
    description="Production-grade local-first backend for the ULTRON AI Operating System.",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    await setup_dependencies()

@app.on_event("shutdown")
async def on_shutdown():
    try:
        await container.storage.disconnect()
    except Exception as e:
        logger.error(f"Error disconnecting storage on shutdown: {e}")

# Request Models
class GoalRequest(BaseModel):
    goal: str

@app.get("/health")
async def health_check():
    """System status and connection health checks diagnostics."""
    try:
        monitor = HealthMonitor(storage=container.storage)
        status = await monitor.check_health()
        return status
    except Exception as e:
        logger.error(f"Health check diagnostics error: {e}")
        raise HTTPException(status_code=500, detail="Health check degraded")

@app.post("/workflow/plan")
async def create_workflow_plan(request: GoalRequest):
    """Generate an execution plan workflow for a high-level goal."""
    try:
        workflow = await container.planner.create_plan(goal=request.goal)
        return {
            "workflow_id": workflow.id,
            "goal": workflow.goal,
            "steps": workflow.steps,
            "status": workflow.status
        }
    except Exception as e:
        logger.error(f"Failed to generate workflow plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))
