import json
import logging
import os
from typing import Any

API_CACHE = True  # store results locally to save on request latency
API_CACHE_DIRECTORY = "cached_requests"

logger = logging.getLogger(__name__)


def get_cache_path(request_path: str) -> str:
    request_path = request_path.strip("/")
    file_name = request_path.replace("/", ".") + ".json"
    return os.path.join(API_CACHE_DIRECTORY, file_name)


def cache_exists(file_path: str) -> bool:
    return API_CACHE and os.path.isfile(file_path)


def cache_load(file_path: str) -> dict[str, Any]:
    if not API_CACHE:
        raise RuntimeError("API caching is not enabled")

    logger.debug("Loading request data from cache file %s", file_path)
    with open(file_path) as file:
        return json.load(file)


def cache_store(file_path: str, data: dict[str, Any]) -> None:
    if not API_CACHE:
        return

    logger.debug("Storing request data to cache file %s", file_path)
    os.makedirs(API_CACHE_DIRECTORY, exist_ok=True)
    with open(file_path, "w") as file:
        json.dump(data, file)
