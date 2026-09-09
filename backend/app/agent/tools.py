from typing import Any, Callable


def calculate_revenue_growth(previous_revenue: float, current_revenue: float) -> float:
    if previous_revenue == 0:
        raise ValueError("previous_revenue must not be zero")
    return round((current_revenue - previous_revenue) / previous_revenue * 100, 2)


def calculate_debt_to_ebitda(total_debt: float, ebitda: float) -> float:
    if ebitda == 0:
        raise ValueError("ebitda must not be zero")
    return round(total_debt / ebitda, 2)


def calculate_profit_margin(net_income: float, revenue: float) -> float:
    if revenue == 0:
        raise ValueError("revenue must not be zero")
    return round(net_income / revenue * 100, 2)


TOOL_REGISTRY: dict[str, Callable[..., float]] = {
    "calculate_revenue_growth": calculate_revenue_growth,
    "calculate_debt_to_ebitda": calculate_debt_to_ebitda,
    "calculate_profit_margin": calculate_profit_margin,
}


def execute_tool(name: str, arguments: dict[str, Any]) -> float:
    try:
        tool = TOOL_REGISTRY[name]
    except KeyError as exc:
        raise ValueError(f"Unknown tool: {name}") from exc
    return tool(**arguments)
