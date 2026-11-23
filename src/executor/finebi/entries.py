# -*- coding: utf-8 -*-
"""FineBI 目录 entry 祖先链解析。

FineBI 的仪表板 entry 授权要求「祖先链完整」：只给仪表板自身授 viewPrivilege
而不给所属文件夹授 view，会报 ``forbid incomplete authorize exception``。
"""
from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional

LOGGER = logging.getLogger(__name__)

ROOT_ID = "decision-directory-root"


class EntryAncestorResolver:
    def __init__(self, platform, ttl: float = 300.0):
        self.platform = platform
        self.ttl = ttl
        self._at = 0.0
        self._parents: Dict[str, str] = {}

    def _load(self) -> None:
        now = time.time()
        if self._parents and now - self._at < self.ttl:
            return
        resp = self.platform.get_entry_tree("pc")
        data = (resp or {}).get("data")
        if isinstance(data, dict):
            nodes = data.get("items") or data.get("entry") or []
        else:
            nodes = data or []
        parents: Dict[str, str] = {}
        for node in nodes:
            if not isinstance(node, dict):
                continue
            node_id = str(node.get("id") or "")
            if not node_id:
                continue
            parent = node.get("pId") or node.get("parentId")
            if parent:
                parents[node_id] = str(parent)
        self._parents = parents
        self._at = now

    def ancestors(self, entry_id: str) -> List[str]:
        """返回 entry 的祖先 id（由近到远，不含根节点和自身）。"""
        entry_id = str(entry_id or "").strip()
        if not entry_id or not self.platform:
            return []
        try:
            self._load()
        except Exception as exc:  # noqa: BLE001 - 拿不到树就不做祖先处理
            LOGGER.warning("读取 FineBI 目录树失败，跳过祖先链检查：%s", exc)
            return []
        chain: List[str] = []
        current = self._parents.get(entry_id)
        seen = set()
        while current and current not in seen:
            seen.add(current)
            if current != ROOT_ID:
                chain.append(current)
            if current == ROOT_ID:
                break
            current = self._parents.get(current)
        return chain
