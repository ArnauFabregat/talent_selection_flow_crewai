import json
from typing import Any, Tuple
from crewai import TaskOutput


def validate_json_output(result: TaskOutput) -> Tuple[bool, Any]:
    """Validate and parse JSON output."""
    try:
        # Try to parse as JSON
        data = json.loads(result.raw)
        return (True, data)
    except json.JSONDecodeError:
        return (False, "Invalid JSON format")
