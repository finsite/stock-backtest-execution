"""Processor module for stock-backtest-execution.

Validates incoming execution requests and simulates trade execution,
including fill price, slippage, and fee calculation.
"""

from typing import Any

from app.utils.setup_logger import setup_logger
from app.utils.types import ValidatedMessage
from app.utils.validate_data import validate_message_schema

logger = setup_logger(__name__)


def validate_input_message(message: dict[str, Any]) -> ValidatedMessage:
    """Validate the incoming raw message against the expected schema.

    Args:
        message (dict[str, Any]): The raw message payload.

    Returns:
        ValidatedMessage: A validated message object.

    Raises:
        ValueError: If the message format is invalid.

    """
    logger.debug("🔍 Validating message schema...")
    if not validate_message_schema(message):
        logger.error("❌ Invalid message schema: %s", message)
        raise ValueError("Invalid message format")
    return message  # type: ignore[return-value]


def simulate_execution(message: ValidatedMessage) -> dict[str, Any]:
    """Simulate order execution with basic pricing and cost modeling.

    Args:
        message (ValidatedMessage): Validated trade request.

    Returns:
        dict[str, Any]: Enriched message with execution details.

    """
    symbol = message.get("symbol", "UNKNOWN")
    action = message.get("action", "HOLD")
    price = float(message.get("price", 100.0))
    quantity = int(message.get("quantity", 0))

    logger.info("💼 Simulating execution: %s %d shares of %s", action, quantity, symbol)

    # Placeholder logic
    slippage_pct = 0.001  # 0.1% slippage
    fee_per_share = 0.005  # $0.005 per share

    fill_price = price * (1 + slippage_pct if action == "BUY" else 1 - slippage_pct)
    total_fee = quantity * fee_per_share
    execution_cost = (
        fill_price * quantity + total_fee
        if action == "BUY"
        else -1 * (fill_price * quantity - total_fee)
    )

    result = {
        "fill_price": round(fill_price, 4),
        "slippage_pct": slippage_pct,
        "execution_fee": round(total_fee, 4),
        "execution_cost": round(execution_cost, 4),
        "status": "executed" if action in ("BUY", "SELL") else "noop",
    }

    logger.debug("📦 Execution result: %s", result)
    return {**message, **result}
