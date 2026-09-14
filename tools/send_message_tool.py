"""Send Message Tool -- cross-channel messaging via platform APIs (send, list targets,
react); works in both CLI and gateway contexts."""

import asyncio
import json
import logging
import os
from functools import partial

from agent.secret_scope import get_secret

logger = logging.getLogger(__name__)

from tools.send_message_targets import _HOME_CHANNEL_ENV_OVERRIDES, _SLACK_USER_ID_RE, resolve_send_target
from tools.send_message_senders import (
    _AUDIO_EXTS, _DEFAULT_CAPTION_LIMIT, _IMAGE_EXTS, _NO_DELIVERABLE, _VIDEO_EXTS, _VOICE_EXTS,
    _adapter_media_method, _error, _live_adapter, _media_caption_split, _plugin_standalone_sender,
    _registry_standalone_send, _resolve_slack_user_target, _sanitize_error_text, _send_bluebubbles,
    _send_matrix_via_adapter, _send_qqbot, _send_signal, _send_telegram, _send_weixin, _send_yuanbao)
from tools.registry import tool_error

# NOTE: ``send_message`` is intentionally NOT registered as an agent-callable model tool
# (the agent must not fire cross-platform messages on its own); cron delivery, the
# ``hermes send`` CLI, the kanban notifier and the opt-in MCP server import the helpers.


def prepare_send_message_platforms() -> None:
    """Load enabled standalone plugins before tool schemas/cache keys are built."""
    from hermes_cli.plugins import discover_plugins
    discover_plugins()
