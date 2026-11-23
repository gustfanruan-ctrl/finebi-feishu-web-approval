"""飞书通知：审批结果、授权结果、到期、离职汇总。

渠道选择（保持原设计）：
- 配置了自定义机器人 webhook → 优先用 webhook（群播）；
- 未配置 webhook → 按 open_id 发应用消息；
- 两者都没有 → 只记日志。
webhook 是群播，一条通知只应发一次；多收件人场景由 :meth:`Notifier.notify_users`
统一收口，避免对同一个 webhook 重复发送。通知失败不影响主流程。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Optional

LOGGER = logging.getLogger(__name__)


def build_card(title: str, content: str, link: str = "", color: str = "blue",
               fields: Optional[List[Any]] = None) -> Dict[str, Any]:
    elements: List[Dict[str, Any]] = []
    # 单据字段：两列展示（日期 / 自增键 / 申请人账号 / 权限内容 / 权限时间…）
    card_fields: List[Dict[str, Any]] = []
    for item in fields or []:
        try:
            label, value = item
        except (TypeError, ValueError):
            continue
        if value in (None, ""):
            continue
        card_fields.append({
            "is_short": len(str(value)) <= 24,
            "text": {"tag": "lark_md",
                     "content": "**%s**\n%s" % (label, value)},
        })
    if card_fields:
        elements.append({"tag": "div", "fields": card_fields})
    elements.append({"tag": "div", "text": {"tag": "lark_md", "content": content}})
    if link:
        elements.append({
            "tag": "action",
            "actions": [{
                "tag": "button",
                "text": {"tag": "plain_text", "content": "查看详情"},
                "type": "primary",
                "url": link,
            }],
        })
    return {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "template": color,
                "title": {"tag": "plain_text", "content": title},
            },
            "elements": elements,
        },
    }


class Notifier:
    def __init__(self, feishu=None, webhook_url: str = "",
                 admin_open_ids: Optional[List[str]] = None,
                 dry_run: bool = False):
        self.feishu = feishu
        self.webhook_url = webhook_url
        self.admin_open_ids = admin_open_ids or []
        self.dry_run = dry_run

    def _send(self, open_id: str, title: str, content: str,
              link: str = "", color: str = "blue",
              fields: Optional[List[Any]] = None) -> None:
        payload = build_card(title, content, link, color, fields=fields)
        try:
            if self.dry_run:
                LOGGER.info("[DRY-RUN][notify] %s -> %s", title, open_id or "webhook")
                return
            if self.webhook_url:
                self.feishu.send_webhook(self.webhook_url, payload)
                LOGGER.info("[notify] 已发送（webhook）：%s", title)
                return
            if self.feishu and open_id:
                self.feishu.send_card(open_id, payload)
                LOGGER.info("[notify] 已发送（open_id=%s）：%s", open_id, title)
                return
            LOGGER.info("[notify] 未配置通知渠道：%s", title)
        except Exception as exc:  # noqa: BLE001 - 通知失败不影响主流程
            LOGGER.warning("通知发送失败（%s）：%s", title, exc)

    def notify_user(self, open_id: str, title: str, content: str,
                    link: str = "", color: str = "blue",
                    fields: Optional[List[Any]] = None) -> None:
        self._send(open_id, title, content, link, color, fields=fields)

    def notify_users(self, open_ids: Iterable[str], title: str, content: str,
                     link: str = "", color: str = "blue",
                     fields: Optional[List[Any]] = None) -> None:
        """给多个 open_id 发同一通知；webhook 群播只发一次，避免重复消息。"""
        ids = [str(open_id) for open_id in (open_ids or []) if open_id]
        if not ids:
            self._send("", title, content, link, color, fields=fields)
            return
        if self.webhook_url:
            self._send("", title, content, link, color, fields=fields)
            return
        for open_id in ids:
            self._send(open_id, title, content, link, color, fields=fields)

    def notify_admins(self, title: str, content: str,
                      link: str = "", color: str = "orange",
                      fields: Optional[List[Any]] = None) -> None:
        if not self.admin_open_ids:
            self._send("", title, content, link, color, fields=fields)
            return
        self.notify_users(self.admin_open_ids, title, content, link, color, fields=fields)
