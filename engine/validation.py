import math

NUMERIC_FIELDS = {
    "arrival_rate": (1, 1000, "Arrival rate"),
    "service_time": (0.1, 120, "Service time"),
    "staff": (1, 50, "Current staff"),
    "operating_hours": (1, 24, "Operating hours"),
    "staff_cost": (0, 1_000_000_000, "Staff cost"),
    "max_wait": (0.1, 120, "Maximum waiting time"),
    "budget": (0, 1_000_000_000_000, "Budget"),
}

OPTIONAL_FIELDS = {
    "speedup_percent": (0, 50, 20, "Faster-service assumption"),
    "speedup_cost": (0, 1_000_000_000, 30000, "Daily cost of faster service"),
    "preorder_share_percent": (0, 60, 25, "Pre-order share"),
    "preorder_cost": (0, 1_000_000_000, 50000, "Daily cost of pre-order system"),
}

MAX_CUSTOM_SCENARIOS = 5


def read_number(data, key, low, high, label, default=None):
    if key not in data:
        if default is None:
            raise ValueError(f"{label} is missing.")
        return float(default)

    value = data[key]
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a number.")
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be a number.")

    if not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number.")
    if not low <= value <= high:
        raise ValueError(f"{label} must be between {low:g} and {high:g}.")
    return value


def validate_inputs(data):
    if not isinstance(data, dict):
        raise ValueError("The request must be a JSON object.")

    clean = {}
    for name, (low, high, label) in NUMERIC_FIELDS.items():
        clean[name] = read_number(data, name, low, high, label)

    if clean["staff"] != int(clean["staff"]):
        raise ValueError("Current staff must be a whole number.")
    clean["staff"] = int(clean["staff"])

    for name, (low, high, default, label) in OPTIONAL_FIELDS.items():
        clean[name] = read_number(data, name, low, high, label, default)

    custom = data.get("custom_scenarios", [])
    if not isinstance(custom, list):
        raise ValueError("custom_scenarios must be a list.")
    if len(custom) > MAX_CUSTOM_SCENARIOS:
        raise ValueError(f"You can add at most {MAX_CUSTOM_SCENARIOS} custom scenarios.")
    clean["custom_scenarios"] = custom

    description = data.get("description", "")
    if not isinstance(description, str):
        description = ""
    clean["description"] = description.strip()[:2000]

    return clean