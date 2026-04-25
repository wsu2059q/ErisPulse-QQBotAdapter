# QQBot适配器与OneBot12协议的转换对照

## QQBot特有事件类型

QQBot平台提供以下事件类型，可在消息处理中检测使用：

### 1. 消息事件

| QQBot事件类型 | eventType | 说明 | 转换后 |
|---|---|---|---|
| C2C_MESSAGE_CREATE | 私聊消息 | 用户发送的私聊消息 | OneBot12 `message` 事件，`detail_type` 为 `private` |
| GROUP_AT_MESSAGE_CREATE | 群@消息 | 群内用户@机器人发送的消息 | OneBot12 `message` 事件，`detail_type` 为 `group` |
| AT_MESSAGE_CREATE | 频道@消息 | 频道内@机器人发送的消息 | OneBot12 `message` 事件，`detail_type` 为 `channel` |
| MESSAGE_CREATE | 频道消息 | 频道内用户发送的消息 | OneBot12 `message` 事件，`detail_type` 为 `channel` |
| DIRECT_MESSAGE_CREATE | 私信消息 | 频道私信消息 | OneBot12 `message` 事件，`detail_type` 为 `private` |

### 2. 通知事件

| QQBot事件类型 | 说明 | 转换后 |
|---|---|---|
| FRIEND_ADD | 用户添加机器人为好友 | OneBot12 `notice` 事件，`detail_type` 为 `friend_add` |
| FRIEND_DEL | 用户删除机器人好友 | OneBot12 `notice` 事件，`detail_type` 为 `friend_del` |
| C2C_MSG_REJECT | 用户拒绝机器人私聊 | OneBot12 `notice` 事件，`detail_type` 为 `private_block` |
| C2C_MSG_RECEIVE | 用户允许机器人私聊 | OneBot12 `notice` 事件，`detail_type` 为 `private_allow` |
| GROUP_ADD_ROBOT | 群添加机器人 | OneBot12 `notice` 事件，`detail_type` 为 `group_increase` |
| GROUP_DEL_ROBOT | 群移除机器人 | OneBot12 `notice` 事件，`detail_type` 为 `group_decrease` |
| GROUP_MSG_REJECT | 群拒绝机器人消息 | OneBot12 `notice` 事件，`detail_type` 为 `group_block` |
| GROUP_MSG_RECEIVE | 群允许机器人消息 | OneBot12 `notice` 事件，`detail_type` 为 `group_allow` |
| GUILD_MEMBER_ADD | 频道成员加入 | OneBot12 `notice` 事件，`detail_type` 为 `group_member_increase` |
| GUILD_MEMBER_UPDATE | 频道成员更新 | OneBot12 `notice` 事件，`detail_type` 为 `group_member_update` |
| GUILD_MEMBER_REMOVE | 频道成员退出 | OneBot12 `notice` 事件，`detail_type` 为 `group_member_decrease` |
| GUILD_CREATE | 频道服务器创建 | OneBot12 `notice` 事件，`detail_type` 为 `guild_create` |
| GUILD_UPDATE | 频道服务器更新 | OneBot12 `notice` 事件，`detail_type` 为 `guild_update` |
| GUILD_DELETE | 频道服务器删除 | OneBot12 `notice` 事件，`detail_type` 为 `guild_delete` |
| CHANNEL_CREATE | 子频道创建 | OneBot12 `notice` 事件，`detail_type` 为 `channel_create` |
| CHANNEL_UPDATE | 子频道更新 | OneBot12 `notice` 事件，`detail_type` 为 `channel_update` |
| CHANNEL_DELETE | 子频道删除 | OneBot12 `notice` 事件，`detail_type` 为 `channel_delete` |

### 3. QQBot平台特有通知事件

| QQBot事件类型 | 说明 | 转换后 |
|---|---|---|
| MESSAGE_REACTION_ADD | 消息表情回应添加 | OneBot12 `notice` 事件，`detail_type` 为 `qqbot_reaction_add` |
| MESSAGE_REACTION_REMOVE | 消息表情回应移除 | OneBot12 `notice` 事件，`detail_type` 为 `qqbot_reaction_remove` |
| INTERACTION_CREATE | 交互事件（按钮点击等） | OneBot12 `notice` 事件，`detail_type` 为 `qqbot_interaction` |
| MESSAGE_AUDIT_PASS | 消息审核通过 | OneBot12 `notice` 事件，`detail_type` 为 `qqbot_audit_pass` |
| MESSAGE_AUDIT_REJECT | 消息审核拒绝 | OneBot12 `notice` 事件，`detail_type` 为 `qqbot_audit_reject` |
| AUDIO_START | 音频开始播放 | OneBot12 `notice` 事件，`detail_type` 为 `qqbot_audio_start` |
| AUDIO_FINISH | 音频播放结束 | OneBot12 `notice` 事件，`detail_type` 为 `qqbot_audio_finish` |
| AT_MESSAGE_DELETE | @消息被删除 | OneBot12 `notice` 事件，`detail_type` 为 `qqbot_message_delete` |
| PUBLIC_MESSAGE_DELETE | 公开消息被删除 | OneBot12 `notice` 事件，`detail_type` 为 `qqbot_message_delete` |
| DIRECT_MESSAGE_DELETE | 私信消息被删除 | OneBot12 `notice` 事件，`detail_type` 为 `qqbot_message_delete` |

### 事件处理示例

```python
from ErisPulse.Core.Event import notice, message

# 处理消息事件
@message.on_message()
async def handle_message(event):
    if event.get("platform") != "qqbot":
        return

    detail_type = event.get("detail_type")

    if detail_type == "private":
        text = event.get_text()
        # 处理私聊消息...
    elif detail_type == "group":
        # 处理群@消息...
        group_id = event.get("group_id")
    elif detail_type == "channel":
        # 处理频道消息...
        channel_id = event.get("channel_id")

# 处理通知事件
@notice.on_notice()
async def handle_notice(event):
    if event.get("platform") != "qqbot":
        return

    detail_type = event.get("detail_type")

    if detail_type == "friend_add":
        user_id = event.get_user_id()
    elif detail_type == "group_increase":
        group_id = event.get("group_id")
    elif detail_type == "qqbot_interaction":
        interaction_id = event.get("qqbot_interaction_id", "")
        interaction_type = event.get("qqbot_interaction_type", "")
        interaction_data = event.get("qqbot_interaction_data", {})
    elif detail_type == "qqbot_audit_pass":
        audit_id = event.get("qqbot_audit_id", "")
        message_id = event.get("qqbot_message_id", "")
    elif detail_type == "qqbot_audit_reject":
        audit_id = event.get("qqbot_audit_id", "")
        reject_reason = event.get("qqbot_audit_reject_reason", "")
    elif detail_type == "qqbot_message_delete":
        message_id = event.get("message_id", "")
```

---

## 消息事件转换对照

### 1. 私聊消息（C2C_MESSAGE_CREATE）

原始事件:
```json
{
  "id": "msg_id_example",
  "author": {
    "user_openid": "USER_OPENID"
  },
  "content": "Hello",
  "timestamp": "2026-04-25T12:00:00+08:00",
  "attachments": []
}
```

转换后:
```json
{
  "id": "msg_id_example",
  "time": 1745558400,
  "type": "message",
  "detail_type": "private",
  "sub_type": "",
  "platform": "qqbot",
  "self": {
    "platform": "qqbot",
    "user_id": "BOT_APPID"
  },
  "qqbot_raw": {
    "...": "原始事件内容"
  },
  "qqbot_raw_type": "C2C_MESSAGE_CREATE",
  "user_id": "USER_OPENID",
  "user_nickname": "",
  "message_id": "msg_id_example",
  "qqbot_openid": "USER_OPENID",
  "qqbot_event_id": "msg_id_example",
  "qqbot_reply_token": "",
  "message": [
    {
      "type": "text",
      "data": {
        "text": "Hello"
      }
    }
  ],
  "alt_message": "Hello"
}
```

### 2. 群@消息（GROUP_AT_MESSAGE_CREATE）

原始事件:
```json
{
  "id": "group_msg_id_example",
  "author": {
    "member_openid": "MEMBER_OPENID"
  },
  "content": "你好",
  "group_openid": "GROUP_OPENID",
  "timestamp": "2026-04-25T12:00:00+08:00",
  "attachments": []
}
```

转换后:
```json
{
  "id": "group_msg_id_example",
  "time": 1745558400,
  "type": "message",
  "detail_type": "group",
  "sub_type": "",
  "platform": "qqbot",
  "self": {
    "platform": "qqbot",
    "user_id": "BOT_APPID"
  },
  "qqbot_raw": {
    "...": "原始事件内容"
  },
  "qqbot_raw_type": "GROUP_AT_MESSAGE_CREATE",
  "user_id": "MEMBER_OPENID",
  "user_nickname": "",
  "group_id": "GROUP_OPENID",
  "message_id": "group_msg_id_example",
  "qqbot_group_openid": "GROUP_OPENID",
  "qqbot_member_openid": "MEMBER_OPENID",
  "qqbot_event_id": "group_msg_id_example",
  "qqbot_reply_token": "",
  "message": [
    {
      "type": "text",
      "data": {
        "text": "你好"
      }
    }
  ],
  "alt_message": "你好"
}
```

### 3. 频道@消息（AT_MESSAGE_CREATE）

原始事件:
```json
{
  "id": "channel_msg_id_example",
  "author": {
    "user_openid": "USER_OPENID",
    "id": "USER_ID",
    "nick": "用户昵称"
  },
  "content": "频道消息",
  "channel_id": "CHANNEL_ID",
  "guild_id": "GUILD_ID",
  "timestamp": "2026-04-25T12:00:00+08:00",
  "attachments": [],
  "mentions": [
    {"id": "MENTIONED_USER_ID", "nick": "被@用户昵称"}
  ]
}
```

转换后:
```json
{
  "id": "channel_msg_id_example",
  "time": 1745558400,
  "type": "message",
  "detail_type": "channel",
  "sub_type": "",
  "platform": "qqbot",
  "self": {
    "platform": "qqbot",
    "user_id": "BOT_APPID"
  },
  "qqbot_raw": {
    "...": "原始事件内容"
  },
  "qqbot_raw_type": "AT_MESSAGE_CREATE",
  "user_id": "USER_OPENID",
  "user_nickname": "用户昵称",
  "channel_id": "CHANNEL_ID",
  "group_id": "GUILD_ID",
  "message_id": "channel_msg_id_example",
  "message": [
    {
      "type": "mention",
      "data": {
        "user_id": "MENTIONED_USER_ID",
        "user_name": "被@用户昵称"
      }
    },
    {
      "type": "text",
      "data": {
        "text": "频道消息"
      }
    }
  ],
  "alt_message": "@被@用户昵称 频道消息"
}
```

### 4. 带图片的消息

原始事件:
```json
{
  "id": "msg_with_image",
  "author": {
    "member_openid": "MEMBER_OPENID"
  },
  "content": "看这个图片",
  "group_openid": "GROUP_OPENID",
  "timestamp": "2026-04-25T12:00:00+08:00",
  "attachments": [
    {
      "content_type": "image/png",
      "url": "https://multimedia.nt.qq.com/image_example.png"
    }
  ]
}
```

转换后:
```json
{
  "id": "msg_with_image",
  "time": 1745558400,
  "type": "message",
  "detail_type": "group",
  "sub_type": "",
  "platform": "qqbot",
  "self": {
    "platform": "qqbot",
    "user_id": "BOT_APPID"
  },
  "qqbot_raw": {
    "...": "原始事件内容"
  },
  "qqbot_raw_type": "GROUP_AT_MESSAGE_CREATE",
  "user_id": "MEMBER_OPENID",
  "user_nickname": "",
  "group_id": "GROUP_OPENID",
  "message_id": "msg_with_image",
  "qqbot_group_openid": "GROUP_OPENID",
  "qqbot_member_openid": "MEMBER_OPENID",
  "qqbot_event_id": "msg_with_image",
  "qqbot_reply_token": "",
  "message": [
    {
      "type": "text",
      "data": {
        "text": "看这个图片"
      }
    },
    {
      "type": "image",
      "data": {
        "url": "https://multimedia.nt.qq.com/image_example.png",
        "qqbot_attachment": {
          "content_type": "image/png",
          "url": "https://multimedia.nt.qq.com/image_example.png"
        }
      }
    }
  ],
  "alt_message": "看这个图片 [图片]"
}
```

### 5. 群添加机器人事件（GROUP_ADD_ROBOT）

原始事件:
```json
{
  "timestamp": "2026-04-25T12:00:00+08:00",
  "group_openid": "GROUP_OPENID",
  "op_member_openid": "OPERATOR_OPENID"
}
```

转换后:
```json
{
  "id": "auto_generated_uuid",
  "time": 1745558400,
  "type": "notice",
  "detail_type": "group_increase",
  "sub_type": "",
  "platform": "qqbot",
  "self": {
    "platform": "qqbot",
    "user_id": "BOT_APPID"
  },
  "qqbot_raw": {
    "...": "原始事件内容"
  },
  "qqbot_raw_type": "GROUP_ADD_ROBOT",
  "group_id": "GROUP_OPENID",
  "operator_id": "OPERATOR_OPENID"
}
```

### 6. 好友添加事件（FRIEND_ADD）

原始事件:
```json
{
  "timestamp": "2026-04-25T12:00:00+08:00",
  "openid": "USER_OPENID"
}
```

转换后:
```json
{
  "id": "auto_generated_uuid",
  "time": 1745558400,
  "type": "notice",
  "detail_type": "friend_add",
  "sub_type": "",
  "platform": "qqbot",
  "self": {
    "platform": "qqbot",
    "user_id": "BOT_APPID"
  },
  "qqbot_raw": {
    "...": "原始事件内容"
  },
  "qqbot_raw_type": "FRIEND_ADD",
  "user_id": "USER_OPENID",
  "user_nickname": ""
}
```

### 7. 交互事件（INTERACTION_CREATE）

原始事件:
```json
{
  "id": "interaction_id",
  "type": "INTERACTION_TYPE",
  "data": {
    "resolved": {}
  },
  "timestamp": "2026-04-25T12:00:00+08:00"
}
```

转换后:
```json
{
  "id": "interaction_id",
  "time": 1745558400,
  "type": "notice",
  "detail_type": "qqbot_interaction",
  "sub_type": "",
  "platform": "qqbot",
  "self": {
    "platform": "qqbot",
    "user_id": "BOT_APPID"
  },
  "qqbot_raw": {
    "...": "原始事件内容"
  },
  "qqbot_raw_type": "INTERACTION_CREATE",
  "qqbot_interaction_id": "interaction_id",
  "qqbot_interaction_type": "INTERACTION_TYPE",
  "qqbot_interaction_data": {
    "resolved": {}
  }
}
```

### 8. 消息审核事件

审核通过（MESSAGE_AUDIT_PASS）:
```json
{
  "id": "audit_event_id",
  "audit_id": "AUDIT_ID",
  "message_id": "MESSAGE_ID",
  "timestamp": "2026-04-25T12:00:00+08:00"
}
```

转换后:
```json
{
  "id": "audit_event_id",
  "time": 1745558400,
  "type": "notice",
  "detail_type": "qqbot_audit_pass",
  "sub_type": "",
  "platform": "qqbot",
  "self": {
    "platform": "qqbot",
    "user_id": "BOT_APPID"
  },
  "qqbot_raw": {
    "...": "原始事件内容"
  },
  "qqbot_raw_type": "MESSAGE_AUDIT_PASS",
  "qqbot_audit_id": "AUDIT_ID",
  "qqbot_message_id": "MESSAGE_ID"
}
```

审核拒绝（MESSAGE_AUDIT_REJECT）:
```json
{
  "id": "audit_event_id",
  "audit_id": "AUDIT_ID",
  "message_id": "MESSAGE_ID",
  "audit_reject_reason": "内容违规",
  "timestamp": "2026-04-25T12:00:00+08:00"
}
```

转换后:
```json
{
  "id": "audit_event_id",
  "time": 1745558400,
  "type": "notice",
  "detail_type": "qqbot_audit_reject",
  "sub_type": "",
  "platform": "qqbot",
  "self": {
    "platform": "qqbot",
    "user_id": "BOT_APPID"
  },
  "qqbot_raw": {
    "...": "原始事件内容"
  },
  "qqbot_raw_type": "MESSAGE_AUDIT_REJECT",
  "qqbot_audit_id": "AUDIT_ID",
  "qqbot_message_id": "MESSAGE_ID",
  "qqbot_audit_reject_reason": "内容违规"
}
```

### 9. 频道成员变更事件

成员加入（GUILD_MEMBER_ADD）:
```json
{
  "guild_id": "GUILD_ID",
  "user": {
    "id": "USER_ID",
    "nick": "用户昵称"
  },
  "timestamp": "2026-04-25T12:00:00+08:00"
}
```

转换后:
```json
{
  "id": "auto_generated_uuid",
  "time": 1745558400,
  "type": "notice",
  "detail_type": "group_member_increase",
  "sub_type": "",
  "platform": "qqbot",
  "self": {
    "platform": "qqbot",
    "user_id": "BOT_APPID"
  },
  "qqbot_raw": {
    "...": "原始事件内容"
  },
  "qqbot_raw_type": "GUILD_MEMBER_ADD",
  "user_id": "USER_ID",
  "user_nickname": "用户昵称",
  "group_id": "GUILD_ID",
  "operator_id": ""
}
```

---

## QQBot发送消息类型（OneBot12扩展）

QQBot适配器支持使用 OneBot12 消息段格式发送消息，支持以下类型：

### 1. 基础消息类型

| 类型 | 说明 | 参数 | msg_type |
|------|------|------|----------|
| `text` | 纯文本 | `text`: 文本内容 | 0 |
| `markdown` | Markdown格式 | `content`: Markdown内容 | 2 |
| `ark` | Ark模板消息 | `template_id`: 模板ID, `kv`: 键值对列表 | 3 |
| `embed` | Embed消息 | embed结构体数据 | 4 |

### 2. 媒体消息类型

| 类型 | 说明 | 参数 | msg_type |
|------|------|------|----------|
| `image` | 图片 | `file`: 文件路径/URL/bytes | 7 |
| `video` | 视频 | `file`: 文件路径/URL/bytes | 7 |
| `voice` | 语音 | `file`: 文件路径/URL/bytes | 7 |
| `file` | 文件 | `file`: 文件路径/URL/bytes | 7 |

> 媒体消息会先通过上传接口获取 `file_info`，然后以 msg_type=7 发送。

### 3. QQBot特有类型

| 类型 | 说明 | 参数 |
|------|------|------|
| `reply` | 回复消息 | `message_id`: 消息ID（通过链式修饰 `.Reply()` 设置） |
| `mention` | @用户 | `user_id`: 用户ID（通过链式修饰 `.At()` 设置） |

### 键盘消息

```python
keyboard = {
    "content": [
        [
            {"label": "按钮1", "type": 2, "data": "value1"},
            {"label": "按钮2", "type": 0, "data": "https://example.com"}
        ]
    ]
}

await qqbot.Send.To("group", group_id).Keyboard(keyboard).Text("带键盘的消息")
```

### 4. 使用链式调用发送

```python
from ErisPulse import sdk
qqbot = sdk.adapter.get("qqbot")

# 基础发送
await qqbot.Send.To("user", user_openid).Text("Hello")

# 发送带@的消息
await qqbot.Send.To("group", group_openid).At("member_openid").Text("@成员")

# 发送带按钮键盘的消息
await qqbot.Send.To("group", group_openid).Keyboard(keyboard).Text("请确认")

# 发送回复消息
await qqbot.Send.To("group", group_openid).Reply("msg_id").Text("回复内容")

# 发送Markdown消息
await qqbot.Send.To("group", group_openid).Markdown("# 标题\n内容")

# 发送Ark模板消息
await qqbot.Send.To("user", user_openid).Ark(template_id=1, kv=[{"key": "k", "value": "v"}])

# 发送Embed消息
await qqbot.Send.To("group", group_openid).Embed({"title": "标题", "content": "内容"})

# 使用 Raw_ob12 发送复杂消息
message = [
    {"type": "text", "data": {"text": "第一行"}},
    {"type": "image", "data": {"file": "https://example.com/img.jpg"}},
    {"type": "text", "data": {"text": "第二行"}}
]
await qqbot.Send.To("group", group_openid).Raw_ob12(message)
```

### 5. 发送目标类型

| target_type | 说明 | endpoint |
|-------------|------|----------|
| `user` | 私聊用户（openid） | `/v2/users/{target_id}/messages` |
| `group` | 群聊（group_openid） | `/v2/groups/{target_id}/messages` |
| `channel` | 频道 | `/channels/{target_id}/messages` |
| `dms` | 频道私信 | `/dms/{target_id}/messages` |

### 6. 媒体上传

发送图片、视频、语音、文件等媒体类型时，适配器会自动调用上传接口：

- 私聊：`POST /v2/users/{target_id}/files`
- 群聊：`POST /v2/groups/{target_id}/files`

支持的 `file_type` 参数：
| file_type | 类型 |
|-----------|------|
| 1 | 图片 |
| 2 | 视频 |
| 3 | 语音 |
| 4 | 文件 |

`file` 参数支持以下格式：
- `bytes`：二进制数据（自动base64编码）
- `str`（URL）：以 `http://` 或 `https://` 开头的网络地址
- `str`（本地路径）：本地文件路径

### 7. 消息回复机制

QQBot平台的群消息和私聊消息支持被动回复。适配器会自动管理回复所需的 `msg_id`：

- 收到消息时，适配器自动缓存 `message_id` 到 `_pending_msg_ids`
- 发送消息时，如果设置了 `.Reply(msg_id)`，会使用该ID作为回复引用
- 如果未显式设置 `.Reply()`，适配器会自动使用缓存的对应目标 `msg_id`
