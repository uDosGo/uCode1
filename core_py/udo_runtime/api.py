"""
UDO Runtime API — Flask blueprint for UDO endpoints.

Mounts at /api/udo/* on the ThinUI API server.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from flask import Blueprint, jsonify, request

from .runtime import UDORuntime

# Singleton runtime instance
_runtime: Optional[UDORuntime] = None


def get_runtime() -> UDORuntime:
    global _runtime
    if _runtime is None:
        _runtime = UDORuntime()
    return _runtime


def create_udo_blueprint() -> Blueprint:
    """Create the UDO API blueprint."""
    bp = Blueprint("udo", __name__, url_prefix="/api/udo")
    rt = get_runtime()

    # ─── Health ────────────────────────────────────────────────────

    @bp.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "version": "0.1.0",
            "runtime": "udo-python",
        })

    # ─── Skills ────────────────────────────────────────────────────

    @bp.route("/skills", methods=["GET"])
    def list_skills():
        skills = rt.list_skills()
        return jsonify([{
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "trigger": s.trigger,
            "eventType": s.event_type,
            "action": s.action,
            "enabled": s.enabled,
        } for s in skills])

    @bp.route("/skills/<skill_id>/enable", methods=["POST"])
    def enable_skill(skill_id: str):
        success = rt.enable_skill(skill_id)
        return jsonify({"success": success})

    @bp.route("/skills/<skill_id>/disable", methods=["POST"])
    def disable_skill(skill_id: str):
        success = rt.disable_skill(skill_id)
        return jsonify({"success": success})

    @bp.route("/skills/<skill_id>/run", methods=["POST"])
    def run_skill(skill_id: str):
        result = rt.run_skill(skill_id)
        return jsonify(result)

    # ─── Tasks ─────────────────────────────────────────────────────

    @bp.route("/tasks", methods=["GET"])
    def list_tasks():
        tasks = rt.list_tasks()
        return jsonify([{
            "id": t.id,
            "type": t.type,
            "status": t.status,
            "priority": t.priority,
            "createdAt": t.created_at,
            "updatedAt": t.updated_at,
        } for t in tasks])

    @bp.route("/tasks/<task_id>/cancel", methods=["POST"])
    def cancel_task(task_id: str):
        success = rt.cancel_task(task_id)
        return jsonify({"success": success})

    @bp.route("/tasks/<task_id>/retry", methods=["POST"])
    def retry_task(task_id: str):
        success = rt.retry_task(task_id)
        return jsonify({"success": success})

    # ─── Variables ─────────────────────────────────────────────────

    @bp.route("/variables", methods=["GET"])
    def list_variables():
        vars_ = rt.list_variables()
        return jsonify([{
            "key": v.key,
            "value": v.value,
            "scope": v.scope,
            "encrypted": v.encrypted,
            "usedBy": v.used_by,
        } for v in vars_])

    @bp.route("/variables", methods=["POST"])
    def set_variable():
        data = request.get_json()
        if not data or "key" not in data:
            return jsonify({"error": "Missing key"}), 400
        success = rt.set_variable(
            data["key"],
            data.get("value", ""),
            data.get("scope", "user"),
            data.get("encrypted", False),
        )
        return jsonify({"success": success})

    @bp.route("/variables/<key>", methods=["DELETE"])
    def delete_variable(key: str):
        success = rt.delete_variable(key)
        return jsonify({"success": success})

    # ─── Agents ────────────────────────────────────────────────────

    @bp.route("/agents", methods=["GET"])
    def list_agents():
        agents = rt.list_agents()
        return jsonify([{
            "id": a.id,
            "name": a.name,
            "type": a.type,
            "status": a.status,
            "health": a.health,
            "tasksCompleted": a.tasks_completed,
        } for a in agents])

    @bp.route("/agents/<agent_id>/start", methods=["POST"])
    def start_agent(agent_id: str):
        success = rt.start_agent(agent_id)
        return jsonify({"success": success})

    @bp.route("/agents/<agent_id>/stop", methods=["POST"])
    def stop_agent(agent_id: str):
        success = rt.stop_agent(agent_id)
        return jsonify({"success": success})

    @bp.route("/agents/<agent_id>/health", methods=["GET"])
    def agent_health(agent_id: str):
        result = rt.get_agent_health(agent_id)
        return jsonify(result)

    # ─── Workflows ─────────────────────────────────────────────────

    @bp.route("/workflows", methods=["GET"])
    def list_workflows():
        workflows = rt.list_workflows()
        return jsonify([{
            "id": w.id,
            "name": w.name,
            "file": w.file,
            "type": w.type,
            "status": w.status,
            "runs": w.runs,
            "lastRun": w.last_run,
        } for w in workflows])

    @bp.route("/workflows/<wf_id>/run", methods=["POST"])
    def run_workflow(wf_id: str):
        success = rt.run_workflow(wf_id)
        return jsonify({"success": success})

    @bp.route("/workflows", methods=["POST"])
    def create_workflow():
        data = request.get_json() or {}
        name = data.get("name", "Unnamed Workflow")
        description = data.get("description", "")
        wf = rt.create_workflow(name, description)
        return jsonify({
            "id": wf.id,
            "name": wf.name,
            "file": wf.file,
            "type": wf.type,
            "status": wf.status,
            "runs": wf.runs,
            "lastRun": wf.last_run,
        }), 201

    @bp.route("/workflows/<wf_id>/disable", methods=["POST"])
    def disable_workflow(wf_id: str):
        success = rt.disable_workflow(wf_id)
        return jsonify({"success": success})

    # ─── Publish ───────────────────────────────────────────────────

    @bp.route("/publish/targets", methods=["GET"])
    def list_publish_targets():
        targets = rt.list_publish_targets()
        return jsonify([{
            "id": t.id,
            "name": t.name,
            "type": t.type,
            "status": t.status,
        } for t in targets])

    @bp.route("/publish/<target_id>", methods=["POST"])
    def publish_to(target_id: str):
        data = request.get_json() or {}
        result = rt.publish_to(target_id, data)
        return jsonify(result)

    # ─── Vault ─────────────────────────────────────────────────────

    @bp.route("/vault", methods=["GET"])
    def list_vault():
        path = request.args.get("path", "/")
        entries = rt.list_vault_entries(path)
        return jsonify(entries)

    @bp.route("/vault/read", methods=["POST"])
    def read_vault():
        data = request.get_json()
        if not data or "path" not in data:
            return jsonify({"error": "Missing path"}), 400
        result = rt.read_vault_file(data["path"])
        return jsonify(result)

    @bp.route("/vault/write", methods=["POST"])
    def write_vault():
        data = request.get_json()
        if not data or "path" not in data:
            return jsonify({"error": "Missing path"}), 400
        success = rt.write_vault_file(data["path"], data.get("content", ""))
        return jsonify({"success": success})

    # ─── MCP ───────────────────────────────────────────────────────

    @bp.route("/mcp/status", methods=["GET"])
    def mcp_status():
        servers = rt.get_mcp_status()
        return jsonify([{
            "id": s.id,
            "name": s.name,
            "running": s.running,
            "output": s.output,
            "error": s.error,
            "startedAt": s.started_at,
        } for s in servers])

    @bp.route("/mcp/<server_id>/start", methods=["POST"])
    def start_mcp(server_id: str):
        success = rt.start_mcp_server(server_id)
        return jsonify({"success": success})

    @bp.route("/mcp/<server_id>/stop", methods=["POST"])
    def stop_mcp(server_id: str):
        success = rt.stop_mcp_server(server_id)
        return jsonify({"success": success})

    @bp.route("/mcp/<server_id>/call", methods=["POST"])
    def call_mcp(server_id: str):
        data = request.get_json() or {}
        result = rt.call_mcp_tool(
            server_id,
            data.get("tool", ""),
            data.get("args", {}),
        )
        return jsonify(result)

    # ─── Checks ────────────────────────────────────────────────────

    @bp.route("/checks", methods=["GET"])
    def list_checks():
        checks = rt.list_checks()
        return jsonify([{
            "id": c.id,
            "name": c.name,
            "status": c.status,
            "duration": c.duration,
            "timestamp": c.timestamp,
            "output": c.output,
            "repository": c.repository,
        } for c in checks])

    @bp.route("/checks/<check_id>/run", methods=["POST"])
    def run_check(check_id: str):
        success = rt.run_check(check_id)
        return jsonify({"success": success})

    @bp.route("/checks/<check_id>/results", methods=["GET"])
    def check_results(check_id: str):
        result = rt.get_check_results(check_id)
        if result is None:
            return jsonify({"error": "Check not found"}), 404
        return jsonify({
            "id": result.id,
            "name": result.name,
            "status": result.status,
            "duration": result.duration,
            "timestamp": result.timestamp,
            "output": result.output,
            "repository": result.repository,
        })

    # ─── Command Execution ─────────────────────────────────────────

    @bp.route("/exec", methods=["POST"])
    def execute():
        data = request.get_json()
        if not data or "command" not in data:
            return jsonify({"error": "Missing command"}), 400
        result = rt.execute_command(data["command"])
        return jsonify(result)

    return bp
