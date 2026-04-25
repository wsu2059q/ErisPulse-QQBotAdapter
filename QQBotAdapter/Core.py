import asyncio
import aiohttp
import json
import uuid
from typing import Dict, List, Any, Optional
from ErisPulse import sdk
from ErisPulse.Core import router
from .Converter import QQBotConverter
from .WebSocket import QQBotWebSocket


class QQBotAdapter(sdk.BaseAdapter):
    class Send(sdk.BaseAdapter.Send):
        def __init__(self, adapter, target_type=None, target_id=None, account_id=None):
            super().__init__(adapter, target_type, target_id, account_id)
            self._at_user_ids = []
            self._at_all = False
            self._reply_message_id = None
            self._keyboard = None

        def Text(self, text: str):
            return self.Raw_ob12([{"type": "text", "data": {"text": text}}])

        def Image(self, file: bytes | str):
            return self.Raw_ob12([{"type": "image", "data": {"file": file}}])

        def Markdown(self, content: str):
            return self.Raw_ob12([{"type": "markdown", "data": {"content": content}}])

        def Ark(self, template_id: int, kv: list):
            return self.Raw_ob12([{"type": "ark", "data": {"template_id": template_id, "kv": kv}}])

        def Embed(self, embed_data: dict):
            return self.Raw_ob12([{"type": "embed", "data": embed_data}])

        def Keyboard(self, keyboard: dict):
            self._keyboard = keyboard
            return self

        def Reply(self, message_id: str) -> "Send":
            self._reply_message_id = message_id
            return self

        def At(self, user_id: str) -> "Send":
            self._at_user_ids.append(user_id)
            return self

        def AtAll(self) -> "Send":
            self._at_all = True
            return self

        def _reset_modifiers(self):
            self._at_user_ids = []
            self._at_all = False
            self._reply_message_id = None
            self._keyboard = None

        def Raw_ob12(self, message: List[Dict], **kwargs):
            return asyncio.create_task(self._do_send_raw_ob12(message, **kwargs))

        async def _do_send_raw_ob12(self, message: List[Dict], **kwargs):
            text_parts = []
            media_info = None
            msg_type = 0
            markdown_data = None
            ark_data = None
            embed_data = None

            for segment in message:
                seg_type = segment.get("type")
                data = segment.get("data", {})

                if seg_type == "text":
                    text_parts.append(data.get("text", ""))
                elif seg_type == "image":
                    file = data.get("file", data.get("url", ""))
                    if isinstance(file, bytes):
                        media_info = await self._adapter._upload_media(file, self._target_type, self._target_id, 1)
                    elif file:
                        media_info = await self._adapter._upload_media(file, self._target_type, self._target_id, 1)
                    if media_info:
                        msg_type = 7
                elif seg_type == "voice":
                    file = data.get("file", data.get("url", ""))
                    if isinstance(file, (bytes, str)) and file:
                        media_info = await self._adapter._upload_media(file, self._target_type, self._target_id, 3)
                    if media_info:
                        msg_type = 7
                elif seg_type == "video":
                    file = data.get("file", data.get("url", ""))
                    if isinstance(file, (bytes, str)) and file:
                        media_info = await self._adapter._upload_media(file, self._target_type, self._target_id, 2)
                    if media_info:
                        msg_type = 7
                elif seg_type == "file":
                    file = data.get("file", data.get("url", ""))
                    if isinstance(file, (bytes, str)) and file:
                        media_info = await self._adapter._upload_media(file, self._target_type, self._target_id, 4)
                    if media_info:
                        msg_type = 7
                elif seg_type == "markdown":
                    msg_type = 2
                    markdown_data = data
                elif seg_type == "ark":
                    msg_type = 3
                    ark_data = data
                elif seg_type == "embed":
                    msg_type = 4
                    embed_data = data

            for uid in self._at_user_ids:
                text_parts.append(f"<@{uid}>")
            if self._at_all:
                text_parts.insert(0, "@所有人")

            content = "".join(text_parts) or " "
            msg_id = self._reply_message_id or kwargs.get("msg_id", "")
            if not msg_id and self._target_type and self._target_id:
                msg_id = self._adapter._pending_msg_ids.get(f"{self._target_type}:{self._target_id}", "")
            params = {"msg_type": msg_type, "content": content if msg_type in (0, 7) else "", "msg_id": msg_id}

            if msg_type == 2 and markdown_data:
                params["markdown"] = {"content": markdown_data.get("content", "")}
            elif msg_type == 3 and ark_data:
                params["ark"] = {"template_id": ark_data.get("template_id", 0), "kv": ark_data.get("kv", [])}
            elif msg_type == 4 and embed_data:
                params["embed"] = embed_data
            elif msg_type == 7 and media_info:
                params["media"] = {"file_info": media_info}

            if self._keyboard:
                params["keyboard"] = self._keyboard

            endpoint = self._get_send_endpoint()
            if not endpoint:
                self._reset_modifiers()
                return {
                    "status": "failed",
                    "retcode": 10003,
                    "data": None,
                    "message_id": "",
                    "message": "无法确定发送目标",
                    "qqbot_raw": None,
                }

            self._reset_modifiers()
            return await self._adapter.call_api(endpoint=endpoint, **params)

        def _get_send_endpoint(self) -> Optional[str]:
            if self._target_type == "user":
                return f"/v2/users/{self._target_id}/messages"
            elif self._target_type == "group":
                return f"/v2/groups/{self._target_id}/messages"
            elif self._target_type == "channel":
                return f"/channels/{self._target_id}/messages"
            elif self._target_type == "dms":
                return f"/dms/{self._target_id}/messages"
            return None

    def __init__(self, sdk):
        super().__init__()
        self.sdk = sdk
        self.logger = sdk.logger
        self.config = self._load_config()
        self.appid = self.config.get("appid", "")
        self.secret = self.config.get("secret", "")
        self._access_token = None
        self._token_expires = 0
        self.bot_id = ""
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws_client: Optional[QQBotWebSocket] = None
        self._heartbeat_meta_task: Optional[asyncio.Task] = None
        self._pending_msg_ids: Dict[str, str] = {}

        converter = QQBotConverter(bot_id_getter=lambda: self.bot_id)
        self.convert = converter.convert

    def _load_config(self):
        config = self.sdk.config.getConfig("QQBot_Adapter")
        if not config:
            default_config = {
                "appid": "YOUR_APPID",
                "secret": "YOUR_CLIENT_SECRET",
                "sandbox": False,
                "intents": [1, 30, 25],
            }
            try:
                self.sdk.config.setConfig("QQBot_Adapter", default_config)
                self.logger.warning("QQBot适配器配置不存在，已自动创建默认配置")
            except Exception as e:
                self.logger.error(f"保存默认配置失败: {e}")
            return default_config
        return config

    def _get_base_url(self) -> str:
        if self.config.get("sandbox", False):
            return "https://sandbox.api.sgroup.qq.com"
        return "https://api.sgroup.qq.com"

    def _get_intents_value(self) -> int:
        intents = self.config.get("intents", [1, 30, 25])
        value = 0
        for intent in intents:
            value |= (1 << intent)
        return value

    async def _ensure_token(self) -> str:
        import time as _time
        if self._access_token and _time.time() < self._token_expires - 120:
            return self._access_token
        await self._refresh_token()
        return self._access_token

    async def _refresh_token(self):
        import time as _time
        url = "https://bots.qq.com/app/getAppAccessToken"
        payload = {"appId": self.appid, "clientSecret": self.secret}
        try:
            async with self.session.post(url, json=payload) as resp:
                data = await resp.json()
                self._access_token = data.get("access_token", "")
                expires_in = int(data.get("expires_in", 7200))
                self._token_expires = _time.time() + expires_in
                self.logger.debug("Access Token 已获取/刷新")
        except Exception as e:
            self.logger.error(f"获取 Access Token 失败: {e}")
            raise

    async def _upload_media(self, file, target_type: str, target_id: str, file_type: int) -> Optional[str]:
        url = f"{self._get_base_url()}"
        if target_type == "user":
            url += f"/v2/users/{target_id}/files"
        elif target_type == "group":
            url += f"/v2/groups/{target_id}/files"
        else:
            return None

        token = await self._ensure_token()
        headers = {"Authorization": f"QQBot {token}", "Content-Type": "application/json"}

        payload = {"file_type": file_type, "srv_send_msg": False}

        if isinstance(file, str) and file.startswith(("http://", "https://")):
            payload["url"] = file
        elif isinstance(file, bytes):
            import base64
            payload["file_data"] = base64.b64encode(file).decode("utf-8")
        elif isinstance(file, str):
            try:
                import os
                if os.path.isfile(file):
                    with open(file, "rb") as f:
                        file_bytes = f.read()
                    import base64
                    payload["file_data"] = base64.b64encode(file_bytes).decode("utf-8")
                else:
                    self.logger.error(f"文件不存在: {file}")
                    return None
            except Exception as e:
                self.logger.error(f"读取本地文件失败: {e}")
                return None

        try:
            async with self.session.post(url, json=payload, headers=headers) as resp:
                data = await resp.json()
                self.logger.debug(f"上传媒体响应: {data}")
                file_info = data.get("file_info", "")
                if not file_info:
                    self.logger.error(f"上传媒体失败: {data}")
                    return None
                return file_info
        except Exception as e:
            self.logger.error(f"上传媒体异常: {e}")
            return None

    async def call_api(self, endpoint: str, **params):
        token = await self._ensure_token()
        url = f"{self._get_base_url()}{endpoint}"
        headers = {"Authorization": f"QQBot {token}", "Content-Type": "application/json"}

        try:
            async with self.session.post(url, json=params, headers=headers) as resp:
                raw_response = await resp.json()

                self.logger.debug(f"QQBot API 请求: {url}")
                self.logger.debug(f"QQBot API 响应: {raw_response}")

                if not isinstance(raw_response, dict):
                    return {
                        "status": "failed",
                        "retcode": 34000,
                        "data": None,
                        "message_id": "",
                        "message": f"API 返回了意外格式: {type(raw_response)}",
                        "qqbot_raw": raw_response,
                    }

                code = raw_response.get("code", 0)
                success = 200 <= resp.status < 300 and code == 0
                msg_id = raw_response.get("id", raw_response.get("data", {}).get("id", ""))

                return {
                    "status": "ok" if success else "failed",
                    "retcode": 0 if success else code or 34000,
                    "data": raw_response.get("data", raw_response),
                    "message_id": str(msg_id) if msg_id else "",
                    "message": "" if success else raw_response.get("message", "Unknown QQBot API error"),
                    "qqbot_raw": raw_response,
                }

        except asyncio.TimeoutError:
            self.logger.error(f"QQBot API 请求超时: {endpoint}")
            return {
                "status": "failed",
                "retcode": 32000,
                "data": None,
                "message_id": "",
                "message": "请求超时",
                "qqbot_raw": None,
            }
        except Exception as e:
            self.logger.error(f"调用 QQBot API 失败: {e}")
            return {
                "status": "failed",
                "retcode": 33000,
                "data": None,
                "message_id": "",
                "message": f"API调用失败: {str(e)}",
                "qqbot_raw": None,
            }

    def _store_event_msg_id(self, event: Dict):
        if event.get("type") != "message":
            return
        detail_type = event.get("detail_type", "")
        msg_id = event.get("message_id", "")
        if not msg_id:
            return
        if detail_type == "group" and "group_id" in event:
            self._pending_msg_ids[f"group:{event['group_id']}"] = msg_id
        elif detail_type == "private":
            user_id = event.get("user_id", "")
            if user_id:
                self._pending_msg_ids[f"user:{user_id}"] = msg_id
        elif detail_type == "channel":
            channel_id = event.get("channel_id", "")
            if channel_id:
                self._pending_msg_ids[f"channel:{channel_id}"] = msg_id

    async def _on_connect(self):
        await self.sdk.adapter.emit({
            "type": "meta",
            "detail_type": "connect",
            "platform": "qqbot",
            "self": {"platform": "qqbot", "user_id": self.bot_id},
        })

        self._heartbeat_meta_task = asyncio.create_task(self._heartbeat_meta_loop())

    async def _heartbeat_meta_loop(self):
        try:
            while True:
                await asyncio.sleep(30)
                await self.sdk.adapter.emit({
                    "type": "meta",
                    "detail_type": "heartbeat",
                    "platform": "qqbot",
                    "self": {"platform": "qqbot", "user_id": self.bot_id},
                })
        except asyncio.CancelledError:
            pass

    async def start(self):
        self.session = aiohttp.ClientSession()

        try:
            await self._ensure_token()
        except Exception as e:
            self.logger.error(f"初始化 Token 失败: {e}")
            if self.session:
                await self.session.close()
            raise

        self.ws_client = QQBotWebSocket(self)
        await self.ws_client.connect()
        await self.ws_client.start_token_refresh()
        self.logger.info("QQBot 适配器已启动")

    async def shutdown(self):
        if self.bot_id:
            await self.sdk.adapter.emit({
                "type": "meta",
                "detail_type": "disconnect",
                "platform": "qqbot",
                "self": {"platform": "qqbot", "user_id": self.bot_id},
            })

        if self._heartbeat_meta_task:
            self._heartbeat_meta_task.cancel()
            try:
                await self._heartbeat_meta_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_meta_task = None

        if self.ws_client:
            await self.ws_client.close()
            self.ws_client = None

        if self.session:
            await self.session.close()
            self.session = None
        self.logger.info("QQBot 适配器已关闭")
