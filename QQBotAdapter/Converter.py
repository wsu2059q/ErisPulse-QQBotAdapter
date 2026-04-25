import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional, List


class QQBotConverter:
    def __init__(self, bot_id_getter=None):
        self._bot_id_getter = bot_id_getter
        self._event_type_map = {
            "C2C_MESSAGE_CREATE": ("message", "private"),
            "GROUP_AT_MESSAGE_CREATE": ("message", "group"),
            "AT_MESSAGE_CREATE": ("message", "channel"),
            "MESSAGE_CREATE": ("message", "channel"),
            "DIRECT_MESSAGE_CREATE": ("message", "private"),
            "FRIEND_ADD": ("notice", "friend_add"),
            "FRIEND_DEL": ("notice", "friend_del"),
            "C2C_MSG_REJECT": ("notice", "private_block"),
            "C2C_MSG_RECEIVE": ("notice", "private_allow"),
            "GROUP_ADD_ROBOT": ("notice", "group_increase"),
            "GROUP_DEL_ROBOT": ("notice", "group_decrease"),
            "GROUP_MSG_REJECT": ("notice", "group_block"),
            "GROUP_MSG_RECEIVE": ("notice", "group_allow"),
            "GUILD_CREATE": ("notice", "guild_create"),
            "GUILD_UPDATE": ("notice", "guild_update"),
            "GUILD_DELETE": ("notice", "guild_delete"),
            "CHANNEL_CREATE": ("notice", "channel_create"),
            "CHANNEL_UPDATE": ("notice", "channel_update"),
            "CHANNEL_DELETE": ("notice", "channel_delete"),
            "GUILD_MEMBER_ADD": ("notice", "group_member_increase"),
            "GUILD_MEMBER_UPDATE": ("notice", "group_member_update"),
            "GUILD_MEMBER_REMOVE": ("notice", "group_member_decrease"),
            "MESSAGE_REACTION_ADD": ("notice", "qqbot_reaction_add"),
            "MESSAGE_REACTION_REMOVE": ("notice", "qqbot_reaction_remove"),
            "INTERACTION_CREATE": ("notice", "qqbot_interaction"),
            "MESSAGE_AUDIT_PASS": ("notice", "qqbot_audit_pass"),
            "MESSAGE_AUDIT_REJECT": ("notice", "qqbot_audit_reject"),
            "AUDIO_START": ("notice", "qqbot_audio_start"),
            "AUDIO_FINISH": ("notice", "qqbot_audio_finish"),
            "AT_MESSAGE_DELETE": ("notice", "qqbot_message_delete"),
            "PUBLIC_MESSAGE_DELETE": ("notice", "qqbot_message_delete"),
            "DIRECT_MESSAGE_DELETE": ("notice", "qqbot_message_delete"),
        }

    def convert(self, raw_event: Dict, ws_event_type: str = "") -> Optional[Dict]:
        if not isinstance(raw_event, dict):
            return None

        event_id = raw_event.get("id") or str(uuid.uuid4())

        timestamp = raw_event.get("timestamp")
        if timestamp:
            event_time = self._parse_timestamp(timestamp)
        else:
            event_time = int(time.time())

        raw_type = ws_event_type
        if not raw_type:
            for key in raw_event:
                if key not in ("id", "timestamp", "version", "shard") and key.isupper():
                    raw_type = key
                    break

        if not raw_type:
            inner_data = raw_event.get("d", raw_event)
            if isinstance(inner_data, dict):
                for key in inner_data:
                    if key.isupper() and "_" in key:
                        raw_type = key
                        break

        event_info = self._event_type_map.get(raw_type, None)
        if event_info is None:
            return self._create_unknown_event(raw_event, event_id, raw_type or "unknown")

        event_type, detail_type = event_info

        base_event = {
            "id": str(event_id),
            "time": event_time,
            "type": event_type,
            "detail_type": detail_type,
            "platform": "qqbot",
            "self": {
                "platform": "qqbot",
                "user_id": self._bot_id_getter() if self._bot_id_getter else "",
            },
            "qqbot_raw": raw_event,
            "qqbot_raw_type": raw_type,
        }

        handler = getattr(self, f"_handle_{event_type}", None)
        if handler:
            return handler(raw_event, base_event, raw_type)

        return base_event

    def _handle_message(self, raw_event: Dict, base_event: Dict, raw_type: str) -> Dict:
        detail_type = base_event["detail_type"]

        if raw_type == "C2C_MESSAGE_CREATE":
            author = raw_event.get("author", {})
            base_event["user_id"] = str(author.get("user_openid", ""))
            base_event["user_nickname"] = ""
            base_event["message_id"] = raw_event.get("id", "")
            base_event["qqbot_openid"] = author.get("user_openid", "")
        elif raw_type == "GROUP_AT_MESSAGE_CREATE":
            author = raw_event.get("author", {})
            base_event["user_id"] = str(author.get("member_openid", ""))
            base_event["user_nickname"] = ""
            base_event["group_id"] = raw_event.get("group_openid", "")
            base_event["message_id"] = raw_event.get("id", "")
            base_event["qqbot_group_openid"] = raw_event.get("group_openid", "")
            base_event["qqbot_member_openid"] = author.get("member_openid", "")
        elif raw_type in ("AT_MESSAGE_CREATE", "MESSAGE_CREATE"):
            author = raw_event.get("author", {})
            base_event["user_id"] = str(author.get("user_openid", author.get("id", "")))
            base_event["user_nickname"] = author.get("nick", author.get("username", ""))
            base_event["channel_id"] = raw_event.get("channel_id", "")
            base_event["group_id"] = raw_event.get("guild_id", "")
            base_event["message_id"] = raw_event.get("id", "")
        elif raw_type == "DIRECT_MESSAGE_CREATE":
            author = raw_event.get("author", {})
            base_event["user_id"] = str(author.get("user_openid", author.get("id", "")))
            base_event["user_nickname"] = author.get("nick", author.get("username", ""))
            base_event["message_id"] = raw_event.get("id", "")
            base_event["qqbot_guild_id"] = raw_event.get("guild_id", "")

        content = raw_event.get("content", "")
        attachments = raw_event.get("attachments", [])
        message_segments = []

        if raw_event.get("event_id"):
            pass

        if "reply_token" in raw_event and raw_type in ("C2C_MESSAGE_CREATE", "GROUP_AT_MESSAGE_CREATE"):
            pass

        for mention in raw_event.get("mentions", []):
            message_segments.append({
                "type": "mention",
                "data": {
                    "user_id": str(mention.get("id", "")),
                    "user_name": mention.get("nick", mention.get("username", "")),
                },
            })

        if content:
            message_segments.append({"type": "text", "data": {"text": content.strip()}})

        for attachment in attachments:
            content_type = attachment.get("content_type", "")
            url = attachment.get("url", "")
            if content_type.startswith("image"):
                message_segments.append({
                    "type": "image",
                    "data": {"url": url, "qqbot_attachment": attachment},
                })
            elif content_type.startswith("video"):
                message_segments.append({
                    "type": "video",
                    "data": {"url": url, "qqbot_attachment": attachment},
                })
            elif content_type.startswith("audio"):
                message_segments.append({
                    "type": "voice",
                    "data": {"url": url, "qqbot_attachment": attachment},
                })
            else:
                message_segments.append({
                    "type": "file",
                    "data": {"url": url, "qqbot_attachment": attachment},
                })

        base_event["message"] = message_segments
        base_event["alt_message"] = self._generate_alt_message(message_segments)

        if raw_type == "C2C_MESSAGE_CREATE":
            base_event["qqbot_event_id"] = raw_event.get("id", "")
            base_event["qqbot_reply_token"] = raw_event.get("reply_token", "")
        elif raw_type == "GROUP_AT_MESSAGE_CREATE":
            base_event["qqbot_event_id"] = raw_event.get("id", "")
            base_event["qqbot_reply_token"] = raw_event.get("reply_token", "")

        return base_event

    def _handle_notice(self, raw_event: Dict, base_event: Dict, raw_type: str) -> Dict:
        if raw_type == "GUILD_MEMBER_ADD":
            base_event["user_id"] = str(raw_event.get("user", {}).get("id", ""))
            base_event["user_nickname"] = raw_event.get("user", {}).get("nick", "")
            base_event["group_id"] = raw_event.get("guild_id", "")
            base_event["operator_id"] = ""
        elif raw_type in ("GUILD_MEMBER_UPDATE", "GUILD_MEMBER_REMOVE"):
            base_event["user_id"] = str(raw_event.get("user", {}).get("id", ""))
            base_event["user_nickname"] = raw_event.get("user", {}).get("nick", "")
            base_event["group_id"] = raw_event.get("guild_id", "")
            base_event["operator_id"] = str(raw_event.get("op_user_id", ""))
        elif raw_type in ("GROUP_ADD_ROBOT", "GROUP_DEL_ROBOT", "GROUP_MSG_REJECT", "GROUP_MSG_RECEIVE"):
            base_event["group_id"] = raw_event.get("group_openid", "")
            base_event["operator_id"] = raw_event.get("op_member_openid", "")
        elif raw_type in ("FRIEND_ADD", "FRIEND_DEL"):
            base_event["user_id"] = raw_event.get("openid", "")
            base_event["user_nickname"] = ""
        elif raw_type in ("C2C_MSG_REJECT", "C2C_MSG_RECEIVE"):
            base_event["user_id"] = raw_event.get("openid", "")
        elif raw_type == "INTERACTION_CREATE":
            base_event["qqbot_interaction_id"] = raw_event.get("id", "")
            base_event["qqbot_interaction_type"] = raw_event.get("type", "")
            base_event["qqbot_interaction_data"] = raw_event.get("data", {})
        elif raw_type in ("MESSAGE_AUDIT_PASS", "MESSAGE_AUDIT_REJECT"):
            base_event["qqbot_audit_id"] = raw_event.get("audit_id", "")
            base_event["qqbot_message_id"] = raw_event.get("message_id", "")
            if raw_type == "MESSAGE_AUDIT_REJECT":
                base_event["qqbot_audit_reject_reason"] = raw_event.get("audit_reject_reason", "")
        elif raw_type in ("CHANNEL_CREATE", "CHANNEL_UPDATE", "CHANNEL_DELETE"):
            base_event["channel_id"] = raw_event.get("id", "")
            base_event["group_id"] = raw_event.get("guild_id", "")
            base_event["qqbot_channel_name"] = raw_event.get("name", "")
        elif raw_type in ("GUILD_CREATE", "GUILD_UPDATE", "GUILD_DELETE"):
            base_event["group_id"] = raw_event.get("id", "")
            base_event["qqbot_guild_name"] = raw_event.get("name", "")
        elif raw_type == "qqbot_message_delete":
            base_event["message_id"] = raw_event.get("id", "")
            base_event["operator_id"] = raw_event.get("op_user_id", "")

        return base_event

    def _create_unknown_event(self, raw_event: Dict, event_id: str, raw_type: str) -> Dict:
        return {
            "id": str(event_id),
            "time": int(time.time()),
            "type": "unknown",
            "detail_type": "unknown",
            "platform": "qqbot",
            "self": {"platform": "qqbot", "user_id": self._bot_id_getter() if self._bot_id_getter else ""},
            "qqbot_raw": raw_event,
            "qqbot_raw_type": raw_type,
            "warning": f"Unsupported event type: {raw_type}",
            "alt_message": "This event type is not supported by this system.",
        }

    def _parse_timestamp(self, timestamp) -> int:
        if isinstance(timestamp, (int, float)):
            ts = int(timestamp)
            return ts // 1000 if ts > 10**12 else ts
        if isinstance(timestamp, str):
            try:
                ts = int(timestamp)
                return ts // 1000 if ts > 10**12 else ts
            except ValueError:
                pass
            try:
                dt = datetime.fromisoformat(timestamp)
                return int(dt.timestamp())
            except (ValueError, TypeError):
                pass
        return int(time.time())

    def _generate_alt_message(self, segments: List[Dict]) -> str:
        parts = []
        for seg in segments:
            seg_type = seg["type"]
            data = seg.get("data", {})
            if seg_type == "text":
                parts.append(data.get("text", ""))
            elif seg_type == "image":
                parts.append("[图片]")
            elif seg_type == "video":
                parts.append("[视频]")
            elif seg_type == "voice":
                parts.append("[语音]")
            elif seg_type == "file":
                parts.append("[文件]")
            elif seg_type in ("at", "mention"):
                parts.append(f"@{data.get('user_name', data.get('user_id', ''))}")
            elif seg_type == "reply":
                parts.append("[回复]")
        return " ".join(parts).strip()
