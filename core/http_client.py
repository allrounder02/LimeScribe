"""Shared HTTP client with connection pooling for all API calls."""

import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_shared_client: Optional[httpx.Client] = None


def get_shared_client() -> httpx.Client:
    """Get or create a shared httpx.Client with connection pooling."""
    global _shared_client
    if _shared_client is None:
        _shared_client = httpx.Client(
            timeout=120.0,
            limits=httpx.Limits(
                max_keepalive_connections=10,
                max_connections=20,
                keepalive_expiry=30.0,
            ),
            http2=True,
        )
        logger.debug("Created shared HTTP client with connection pooling")
    return _shared_client


def close_shared_client():
    """Close the shared client. Call on app shutdown."""
    global _shared_client
    if _shared_client is not None:
        _shared_client.close()
        _shared_client = None
        logger.debug("Closed shared HTTP client")
