"""
Main entry point for SentientEcho agent.
"""

import asyncio
import sys
from sentient_agent_framework import DefaultServer

try:
    from .sentient_echo_agent import SentientEchoAgent
    from .config import get_settings, validate_config
    from .utils.logger import get_logger
    from .server import EnhancedSentientServer
except ImportError:
    # For direct execution/testing
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from sentient_echo_agent import SentientEchoAgent
    from config import get_settings, validate_config
    from utils.logger import get_logger
    from server import EnhancedSentientServer

logger = get_logger(__name__)


async def main():
    """Main application entry point."""
    try:
        # Validate configuration
        logger.info("Starting SentientEcho agent...")
        validate_config()
        
        settings = get_settings()
        logger.info(f"Configuration loaded successfully for {settings.agent_name}")
        
        # Create the agent
        agent = SentientEchoAgent(name=settings.agent_name)
        logger.info(f"Created {settings.agent_name} agent")

        # Create and configure the enhanced server
        server = EnhancedSentientServer(agent)
        logger.info(f"Created enhanced server for {settings.agent_name}")

        # Start the server
        logger.info(f"Starting enhanced server on {settings.agent_host}:{settings.agent_port}")
        server.run(
            host=settings.agent_host,
            port=settings.agent_port,
            debug=False
        )
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal, stopping server...")
    except Exception as e:
        logger.error(f"Failed to start SentientEcho agent: {e}", exc_info=True)
        sys.exit(1)


def run_server():
    """Run the server (for use with uvicorn or similar)."""
    try:
        validate_config()
        settings = get_settings()

        agent = SentientEchoAgent(name=settings.agent_name)
        server = EnhancedSentientServer(agent)

        return server.app  # Return FastAPI app for ASGI servers

    except Exception as e:
        logger.error(f"Failed to create server: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
