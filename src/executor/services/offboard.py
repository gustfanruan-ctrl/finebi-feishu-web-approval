"""离职/转岗：资源交接 + 权限回收 + 账号禁用。

交接接口（docs/finebi/开放平台 FineBI接口（对外）.md「资源交接」段）：
- ``GET  /v3/bi/conf/handover/analysis/get``：我的分析（folders/subjects，无 tables）；
- ``GET  /v3/bi/conf/handover/table/get``：公共数据（folders/tables，无 subjects）；
- ``POST /v3/bi/conf/handover/start``：``resourceInPublicData.packIds/tableNames`` 与
  ``resourceInUserAnalysis.packIds/subjectIds`` 是两组独立字段，不能混用。

本模块按来源分别收集资源：公共数据文件夹/表进公共数据字段，我的分析文件夹/主题进
分析字段。分析文件夹目前 FineBIClient.handover_start 还没有对应参数，调用方会先尝试
``analysis_pack_ids``，不支持时退化为只交接主题并记录待人工提示。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

LOGGER = logging.getLogger(__name__)


def _collect(node: Any, packs: List[str], tables: List[str],
             subjects: List[str]) -> None:
    """递归收集 folders/tables/subjects；根节点自身 id（__root_group__ 等）不算资源。"""
    if not isinstance(node, dict):
        return
    for folder in node.get("folders") or []:
        if isinstance(folder, dict) and folder.get("id"):
            packs.append(str(folder["id"]))
            _collect(folder, packs, tables, subjects)
    for table in node.get("tables") or []:
        if isinstance(table, dict) and table.get("id"):
            tables.append(str(table["id"]))
    for subject in node.get("subjects") or []:
        if isinstance(subject, dict) and subject.get("id"):
            subjects.append(str(subject["id"]))


def _handover_failures(resp: Any) -> Dict[str, List[str]]:
    """解析 handover/start 的 ``failResource``，返回非空失败项。"""
    data = (resp or {}).get("data") if isinstance(resp, dict) else None
    if isinstance(data, list) and data:
        first = data[0]
        data = first.get("data") if isinstance(first, dict) else None
    if not isinstance(data, dict):
        return {}
    failures: Dict[str, List[str]] = {}
    fail = data.get("failResource") or {}
    if isinstance(fail, dict):
        for group, values in fail.items():
            if not isinstance(values, dict):
                continue
            for key, items in values.items():
                if items:
                    failures["%s.%s" % (group, key)] = [str(item) for item in items]
    return failures


class OffboardService:
    def __init__(self, finebi, storage, platform=None, revoke_service=None,
                 dry_run: bool = False, notifier=None):
        self.finebi = finebi
        self.platform = platform
        self.revoke_service = revoke_service
        self.storage = storage
        self.dry_run = dry_run
        self.notifier = notifier

    def offboard(self, user: str, accepter: str = "") -> Dict[str, Any]:
        summary: Dict[str, Any] = {"user": user, "accepter": accepter, "steps": []}
        public_packs: List[str] = []
        public_tables: List[str] = []
        public_subjects: List[str] = []
        analysis_packs: List[str] = []
        analysis_tables: List[str] = []
        analysis_subjects: List[str] = []
        all_packs: List[str] = []
        all_tables: List[str] = []
        all_subjects: List[str] = []

        if not self.dry_run:
            analysis = self.finebi.handover_analysis(user)
            public = self.finebi.handover_public(user)
            analysis_data = (analysis or {}).get("data") or {}
            public_data = (public or {}).get("data") or {}
            _collect(public_data, public_packs, public_tables, public_subjects)
            _collect(analysis_data, analysis_packs, analysis_tables, analysis_subjects)
            # 汇总字段按资源类型给管理员看（两类文件夹合并展示，明细见 public/user_analysis）
            all_packs = public_packs + analysis_packs
            all_tables = public_tables + analysis_tables
            all_subjects = public_subjects + analysis_subjects
        summary["resources"] = {
            "packs": sorted(set(all_packs)),
            "tables": sorted(set(all_tables)),
            "subjects": sorted(set(all_subjects)),
            "public": {"packs": sorted(set(public_packs)),
                       "tables": sorted(set(public_tables))},
            "user_analysis": {"packs": sorted(set(analysis_packs)),
                              "subjects": sorted(set(analysis_subjects))},
        }

        if accepter and not self.dry_run:
            kwargs = {
                "pack_ids": sorted(set(public_packs)),
                "table_names": sorted(set(public_tables)),
                "subject_ids": sorted(set(analysis_subjects)),
            }
            try:
                resp = self.finebi.handover_start(
                    user, accepter,
                    analysis_pack_ids=sorted(set(analysis_packs)), **kwargs)
            except TypeError:
                # 兼容旧 FineBIClient（无 analysis_pack_ids 参数）：先交接主题+公共数据
                resp = self.finebi.handover_start(user, accepter, **kwargs)
                if analysis_packs:
                    summary.setdefault("warnings", []).append(
                        "我的分析文件夹未自动交接（客户端不支持 resourceInUserAnalysis.packIds），"
                        "需在 FineBI 后台人工处理：%s" % sorted(set(analysis_packs)))
            try:
                summary["handover"] = resp
                failures = _handover_failures(resp)
                if failures:
                    summary.setdefault("warnings", []).append("部分资源交接失败：%s" % failures)
                    self.storage.log("WARNING", "offboard", "资源交接存在失败资源",
                                     {"user": user, "failures": failures})
                summary["steps"].append("handover_done")
            except Exception as exc:  # noqa: BLE001
                LOGGER.exception("资源交接失败")
                summary["handover_error"] = str(exc)
                self.storage.log("ERROR", "offboard", "资源交接失败：%s" % exc, {"user": user})
        elif accepter:
            summary["handover"] = {"dry_run": True, "accepter": accepter}
        else:
            summary["handover"] = {"skipped": True, "reason": "未指定交接人"}

        if self.revoke_service:
            summary["revoked"] = self.revoke_service.revoke_user(user, reason="离职/转岗回收")
            summary["steps"].append("permissions_revoked")

        if self.platform and not self.dry_run:
            try:
                self.platform.set_user_enabled(user, False)
                summary["disabled"] = True
                summary["steps"].append("user_disabled")
            except Exception as exc:  # noqa: BLE001
                summary["disable_error"] = str(exc)
                self.storage.log("ERROR", "offboard", "禁用用户失败：%s" % exc, {"user": user})

        self.storage.log("INFO", "offboard", "离职回收完成", summary)
        if self.notifier:
            self.notifier.notify_admins(
                "离职权限清理完成",
                "用户 `%s`：交接 %s，回收 %s 条，禁用=%s" % (
                    user, "成功" if summary.get("steps", []).count("handover_done") else "未完成/待人工",
                    len(summary.get("revoked") or []), summary.get("disabled", False)))
        return summary
