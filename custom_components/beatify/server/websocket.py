"""WebSocket handler for Beatify game connections."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiohttp import WSMsgType, web

from custom_components.beatify.const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class BeatifyWebSocketHandler:
    """Handle WebSocket connections for Beatify."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize handler.

        Args:
            hass: Home Assistant instance
        """
        self.hass = hass
        self.connections: set[web.WebSocketResponse] = set()

    async def handle(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connection.

        Args:
            request: aiohttp request

        Returns:
            WebSocket response
        """
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.connections.add(ws)
        _LOGGER.debug("WebSocket connected, total: %d", len(self.connections))

        try:
            # Send initial state
            game_state = self.hass.data.get(DOMAIN, {}).get("game")
            if game_state:
                state = game_state.get_state()
                if state:
                    await ws.send_json({"type": "state", **state})

            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        await self._handle_message(ws, msg.json())
                    except Exception as err:  # noqa: BLE001
                        _LOGGER.warning("Failed to parse WebSocket message: %s", err)
                elif msg.type == WSMsgType.ERROR:
                    _LOGGER.error("WebSocket error: %s", ws.exception())

        finally:
            self.connections.discard(ws)
            _LOGGER.debug("WebSocket disconnected, total: %d", len(self.connections))

        return ws

    async def _handle_message(
        self, ws: web.WebSocketResponse, data: dict  # noqa: ARG002
    ) -> None:
        """Handle incoming WebSocket message.

        Args:
            ws: WebSocket connection
            data: Parsed message data
        """
        msg_type = data.get("type")

        if msg_type == "join":
            # Placeholder - full implementation in Epic 3
            _LOGGER.debug("Join request received: %s", data.get("name"))
        else:
            _LOGGER.warning("Unknown message type: %s", msg_type)

    async def broadcast(self, message: dict) -> None:
        """Broadcast message to all connected clients.

        Args:
            message: Message to broadcast
        """
        for ws in list(self.connections):
            if not ws.closed:
                try:
                    await ws.send_json(message)
                except Exception as err:  # noqa: BLE001
                    _LOGGER.warning("Failed to send to WebSocket: %s", err)
