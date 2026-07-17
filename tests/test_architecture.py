import pytest
from core.context.container import Container
from core.events.bus import EventBus
from core.permissions.manager import PermissionManager
from core.reasoning.reasoner import Reasoner
from core.planner.planner import Planner
from core.execution.executor import Executor
from storage.sqlite.connection import SQLiteStorage
from models.event import WorkflowStarted
from tools.registry import ToolRegistry
from tools.manager import ToolManager

@pytest.mark.asyncio
async def test_dependency_injection_container():
    """Verify that dependencies can be registered and resolved from the container."""
    container = Container()
    
    event_bus = EventBus()
    storage = SQLiteStorage()
    permission_manager = PermissionManager()
    reasoner = Reasoner()
    planner = Planner(reasoner)
    
    async def dummy_resolver(name: str):
        raise NotImplementedError()
        
    executor = Executor(permission_manager, event_bus, dummy_resolver)

    container.event_bus = event_bus
    container.storage = storage
    container.reasoner = reasoner
    container.planner = planner
    container.executor = executor
    container.permission_manager = permission_manager

    assert container.event_bus is event_bus
    assert container.storage is storage
    assert container.reasoner is reasoner
    assert container.planner is planner
    assert container.executor is executor
    assert container.permission_manager is permission_manager

@pytest.mark.asyncio
async def test_event_bus_publish_subscribe():
    """Verify the pub/sub event system functions correctly."""
    event_bus = EventBus()
    received_events = []

    async def sample_handler(event: WorkflowStarted):
        received_events.append(event)

    event_bus.subscribe(WorkflowStarted, sample_handler)

    test_event = WorkflowStarted(workflow_id="wf-123", goal="Test goal")
    await event_bus.publish(test_event)

    assert len(received_events) == 1
    assert received_events[0].workflow_id == "wf-123"
    assert received_events[0].goal == "Test goal"

def test_tool_manager_discovery():
    """Verify that the ToolManager discovers built-in tools."""
    registry = ToolRegistry()
    manager = ToolManager(registry)
    
    manager.discover_tools(package_name="tools")
    
    # We should have discovered at least our browser, terminal, system, filesystem tools
    tools = registry.list_tools()
    assert len(tools) > 0
    assert "browser.navigate" in tools
    assert "filesystem.read_file" in tools
    assert "terminal.run_command" in tools
