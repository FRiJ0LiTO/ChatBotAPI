import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop_policy():
    # Return a custom event loop policy if needed
    return asyncio.DefaultEventLoopPolicy()
