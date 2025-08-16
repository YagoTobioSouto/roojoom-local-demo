import os
import sys
import json
from datetime import datetime
from loguru import logger

# Remove default logger
logger.remove(0)

# Configure logger for ECS deployment
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
environment = os.getenv("ENVIRONMENT", "development").lower()
service_name = os.getenv("SERVICE_NAME", "pipecat-voice-agent")
service_version = os.getenv("SERVICE_VERSION", "1.0")


def structured_formatter(record):
    """Custom formatter for structured logging in CloudWatch."""
    # Base structured log entry
    log_entry = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "logger": record["name"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
        "message": record["message"],
        "service": {
            "name": service_name,
            "version": service_version,
            "environment": environment,
        },
    }

    # Add extra context if available
    if record.get("extra"):
        extra = record["extra"]

        # Add request context if available
        if "request_id" in extra:
            log_entry["request_id"] = extra["request_id"]
        if "user_id" in extra:
            log_entry["user_id"] = extra["user_id"]
        if "room_url" in extra:
            log_entry["room_url"] = extra["room_url"]
        if "bot_pid" in extra:
            log_entry["bot_pid"] = extra["bot_pid"]
        if "daily_room_id" in extra:
            log_entry["daily_room_id"] = extra["daily_room_id"]

        # Add performance metrics if available
        if "duration_ms" in extra:
            log_entry["performance"] = {"duration_ms": extra["duration_ms"]}

        # Add error context if available
        if "error_type" in extra:
            log_entry["error"] = {
                "type": extra["error_type"],
                "code": extra.get("error_code"),
                "details": extra.get("error_details"),
            }

    # Add exception info if present
    if record["exception"]:
        log_entry["exception"] = {
            "type": record["exception"].type.__name__,
            "value": str(record["exception"].value),
            "traceback": (
                record["exception"].traceback.format()
                if record["exception"].traceback
                else None
            ),
        }

    return json.dumps(log_entry, default=str)


# Add human-readable logging for development
if environment == "development":
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        serialize=False,
        backtrace=True,
        diagnose=True,
        enqueue=True,
        catch=True,
    )

# Add structured JSON logging for production/ECS environments
logger.add(
    sys.stdout,
    level=log_level,
    format=structured_formatter,
    serialize=False,  # We handle serialization in the formatter
    backtrace=False,
    diagnose=False,
    enqueue=True,
    catch=True,
)


# Add performance logging helper
def log_performance(func_name: str, duration_ms: float, **kwargs):
    """Helper function to log performance metrics."""
    logger.info(f"Performance: {func_name} completed in {duration_ms:.2f}ms - {kwargs}")


# Add error logging helper
def log_error(error: Exception, error_code: str = None, **kwargs):
    """Helper function to log errors with structured context."""
    logger.error(f"Error occurred: {error} - Code: {error_code} - Context: {kwargs}")


# Add request logging helper
def log_request(request_id: str, method: str, path: str, **kwargs):
    """Helper function to log HTTP requests."""
    logger.info(f"HTTP {method} {path} - RequestID: {request_id} - Context: {kwargs}")


# Add bot lifecycle logging helper
def log_bot_lifecycle(event: str, bot_pid: int, room_url: str = None, **kwargs):
    """Helper function to log bot lifecycle events."""
    logger.info(
        f"Bot lifecycle: {event} (PID: {bot_pid}) - Room: {room_url} - Context: {kwargs}"
    )


# Export helpers for use in other modules
__all__ = ["logger", "log_performance", "log_error", "log_request", "log_bot_lifecycle"]
