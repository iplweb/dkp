"""Utility helpers for cache operations within the comms app."""
from __future__ import annotations

import logging
from typing import Iterable

from django.core.cache import caches

logger = logging.getLogger(__name__)

USER_COUNT_PATTERN = "user_count:*"


def _delete_with_delete_pattern(cache_backend) -> bool:
    """Attempt to remove keys via delete_pattern, return True if supported."""
    delete_pattern = getattr(cache_backend, "delete_pattern", None)
    if not callable(delete_pattern):
        return False
    try:
        delete_pattern(USER_COUNT_PATTERN)
        return True
    except NotImplementedError:
        # Backend exposes delete_pattern but does not implement it.
        return False


def _delete_with_keys(cache_backend) -> bool:
    """Attempt to remove keys using a keys scan, return True if any deleted."""
    keys_method = getattr(cache_backend, "keys", None)
    if not callable(keys_method):
        return False

    try:
        raw_keys: Iterable[str] = keys_method(USER_COUNT_PATTERN)
    except NotImplementedError:
        return False

    raw_keys = list(raw_keys)
    if not raw_keys:
        return True  # Nothing matched, but pattern support exists

    # django-redis may return bytes
    keys = [key.decode("utf-8") if isinstance(key, bytes) else key for key in raw_keys]
    cache_backend.delete_many(keys)
    return True


def _delete_with_locmem(cache_backend) -> bool:
    """Fallback for in-memory caches that expose internal dictionaries."""
    internal_cache = getattr(cache_backend, "_cache", None)
    if not isinstance(internal_cache, dict):
        return False

    keys_to_remove = [key for key in internal_cache if "user_count:" in str(key)]
    if not keys_to_remove:
        return True

    expire_info = getattr(cache_backend, "_expire_info", None)

    for key in list(keys_to_remove):
        internal_cache.pop(key, None)
        if isinstance(expire_info, dict):
            expire_info.pop(key, None)
    return True


def reset_connection_counts(cache_alias: str = "default") -> None:
    """Clear cached user-count entries for nurses, surgeons, and anesthetists."""
    cache_backend = caches[cache_alias]

    if _delete_with_delete_pattern(cache_backend):
        logger.info("Cleared cached user counts using delete_pattern")
        return

    if _delete_with_keys(cache_backend):
        logger.info("Cleared cached user counts using key scan")
        return

    if _delete_with_locmem(cache_backend):
        logger.info("Cleared cached user counts using in-memory fallback")
        return

    logger.warning("Unable to clear cached user counts for alias '%s'", cache_alias)
