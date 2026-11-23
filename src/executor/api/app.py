"""HTTP API（可选依赖 fastapi/uvicorn）。

启动：python -m executor.cli serve --port 8080
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from ..config import Settings
from ..runtime import build


def create_app(settings: Optional[Settings] = None):
    try:
        from fastapi import Body, FastAPI, Header, HTTPException
    except ImportError as exc:  # pragma: no cover - 运行环境相关
        raise RuntimeError("需要先安装 fastapi/uvicorn：pip install -r requirements.txt") from exc

    settings = settings or Settings.load()
    ctx = build(settings)
    app = FastAPI(title="FineBI × 飞书 权限自动化执行器", version="0.1.0")

    def _auth(authorization: Optional[str] = None) -> None:
        if not settings.api_token:
            return
        if authorization != "Bearer " + settings.api_token:
            raise HTTPException(status_code=401, detail="unauthorized")

    @app.get("/health")
    def health() -> Dict[str, Any]:
        return {"status": "ok", "dry_run": settings.dry_run,
                "approval_code": settings.feishu_approval_code}

    @app.post("/grant")
    def grant(body: Dict[str, Any] = Body(...),
              authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
        _auth(authorization)
        from ..models import PermissionRequest
        req = PermissionRequest.from_dict(body)
        return ctx.permission.grant(req).to_dict()

    @app.post("/revoke")
    def revoke(body: Dict[str, Any] = Body(...),
               authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
        _auth(authorization)
        if body.get("ledger_id"):
            rows = [r for r in ctx.storage.active_ledger() if r["id"] == body["ledger_id"]]
            if not rows:
                return {"error": "ledger not found"}
            return ctx.revoke.revoke_ledger(rows[0], reason=body.get("reason", "手动回收"))
        if body.get("user"):
            return {"results": ctx.revoke.revoke_user(body["user"],
                                                      reason=body.get("reason", "手动回收"))}
        return {"error": "需要 ledger_id 或 user"}

    @app.post("/expire")
    def expire(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
        _auth(authorization)
        return {"results": ctx.expire.run_once()}

    @app.post("/offboard")
    def offboard(body: Dict[str, Any] = Body(...),
                 authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
        _auth(authorization)
        return ctx.offboard.offboard(body.get("user", ""), body.get("accepter", ""))

    @app.post("/poll")
    def poll(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
        _auth(authorization)
        return ctx.poller.run_once()

    @app.post("/reconcile")
    def reconcile(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
        _auth(authorization)
        return {"diffs": ctx.reconcile.run()}

    @app.post("/jobs/run")
    def run_jobs(body: Dict[str, Any] = Body(default={}),
                 authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
        _auth(authorization)
        return ctx.jobs.run_due(limit=int(body.get("limit", 100)))

    @app.post("/requests/{request_id}/retry")
    def retry_request(request_id: str,
                      authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
        _auth(authorization)
        row = ctx.storage.get_request(request_id)
        if not row:
            raise HTTPException(status_code=404, detail="request not found")
        from ..models import PermissionRequest
        return ctx.permission.grant(PermissionRequest.from_dict(row["payload"])).to_dict()

    return app
