from typing import Dict, Any

class SystemMetrics:
    """Tracks and exposes performance counters and Gauges for system diagnostics."""

    def __init__(self) -> None:
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}

    def increment(self, name: str, value: int = 1) -> None:
        self._counters[name] = self._counters.get(name, 0) + value

    def set_gauge(self, name: str, value: float) -> None:
        self._gauges[name] = value

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges)
        }
