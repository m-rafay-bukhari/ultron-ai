from models.permission import PermissionScope


def get_scope_for_tool(tool_name: str) -> PermissionScope:
    """Derive permission scope from the tool's name/namespace."""
    if tool_name.startswith("filesystem."):
        return PermissionScope.FILE_SYSTEM
    elif tool_name.startswith("terminal."):
        return PermissionScope.TERMINAL
    elif tool_name.startswith("browser."):
        return PermissionScope.BROWSER
    elif tool_name.startswith("system."):
        return PermissionScope.SYSTEM
    else:
        return PermissionScope.INTEGRATION
