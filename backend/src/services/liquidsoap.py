"""
Liquidsoap orchestration service.

Generates a .liq script for a station using Jinja2 templates and writes
it to the media root. When a Liquidsoap daemon is running it can be
reloaded via its telnet interface.
"""

import asyncio
import logging
import socket
from pathlib import Path

import aiofiles
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.core.config import settings

logger = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "liquidsoap"


def _get_jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=select_autoescape(enabled_extensions=()),
        keep_trailing_newline=True,
    )


class LiquidSoapService:
    def render_config(self, station: object, playlists: list, mounts: list) -> str:
        """Render the Jinja2 template to a Liquidsoap script string."""
        env = _get_jinja_env()
        template = env.get_template("station.liq.j2")
        media_root = Path(settings.MEDIA_ROOT)
        return template.render(
            station=station,
            playlists=playlists,
            mounts=mounts,
            media_root=str(media_root),
            webhook_url=(
                f"http://backend:8000/api/v1/stations/{station.id}/now-playing"  # type: ignore[attr-defined]
            ),
            icecast_host=settings.ICECAST_HOST,
            icecast_port=settings.ICECAST_PORT,
            icecast_source_password=settings.ICECAST_SOURCE_PASSWORD,
            telnet_port=settings.LIQUIDSOAP_TELNET_PORT,
        )

    async def write_config(self, station: object, playlists: list, mounts: list) -> Path:
        """Write the generated .liq config to disk and return the path."""
        script = self.render_config(station, playlists, mounts)
        station_dir = Path(settings.MEDIA_ROOT) / station.short_name  # type: ignore[attr-defined]
        station_dir.mkdir(parents=True, exist_ok=True)
        config_path = station_dir / "station.liq"
        async with aiofiles.open(config_path, "w") as f:
            await f.write(script)
        logger.info("Wrote Liquidsoap config: %s", config_path)
        return config_path

    async def reload(self) -> bool:
        """
        Send the 'uptime' command to the Liquidsoap telnet interface to verify
        connectivity. In production, send 'exit' or a source-specific reload.
        Returns True if the daemon responded.
        """
        host = settings.LIQUIDSOAP_TELNET_HOST
        port = settings.LIQUIDSOAP_TELNET_PORT
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=3
            )
            writer.write(b"uptime\n")
            await writer.drain()
            await asyncio.wait_for(reader.read(256), timeout=2)
            writer.close()
            await writer.wait_closed()
            return True
        except (OSError, asyncio.TimeoutError, socket.error):
            logger.warning("Could not connect to Liquidsoap telnet at %s:%d", host, port)
            return False


liquidsoap_service = LiquidSoapService()
