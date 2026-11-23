"""权限一致性校验（FR-GRN-10）。

约束 C-06：父目录有“授权”权限时，子目录不得关闭“授权”。
资源层级来自 config.resources 的 `parent` 字段（资源 ID 或资源名）。
未配置层级时跳过（本地联调可先不启用，产品文档 G-03 已列）。
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from ..errors import BusinessError


class ParentChildError(BusinessError):
    """父子目录权限不一致（E2002）。"""


def _first_data(resp: Any) -> Any:
    if not isinstance(resp, dict):
        return None
    data = resp.get("data")
    if isinstance(data, list) and data:
        item = data[0]
        if isinstance(item, dict):
            return item.get("data")
    return data


def _find(resources: Dict[str, Any], key: str) -> Optional[Dict[str, Any]]:
    if not resources:
        return None
    node = resources.get(key)
    if isinstance(node, dict):
        return node
    for value in resources.values():
        if not isinstance(value, dict):
            continue
        if str(value.get("resource_id")) == str(key) or str(value.get("id")) == str(key):
            return value
    return None


def check_parent_empower(finebi, resources: Dict[str, Any], user: str,
                         resource_id: str) -> None:
    """关闭子目录“授权”前检查祖先链；父级 empowerPrivilege=true 时抛 E2002。"""
    node = _find(resources, resource_id)
    if not node:
        return
    parent = node.get("parent") or node.get("parent_id")
    seen = set()
    while parent and str(parent) not in seen:
        seen.add(str(parent))
        data = _first_data(finebi.get_folder_permission(user, str(parent)))
        if isinstance(data, dict) and data.get("empowerPrivilege"):
            raise ParentChildError(
                "父目录 %s 已开启“授权”权限，子目录 %s 不能关闭“授权”（E2002）"
                % (parent, resource_id))
        parent_node = _find(resources, str(parent))
        parent = (parent_node or {}).get("parent") or (parent_node or {}).get("parent_id")
