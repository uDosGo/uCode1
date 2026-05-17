"""
UDO Runtime — Core orchestrator that coordinates all UDO subsystems.
"""

import os
import json
import time
import uuid
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


# ─── Data Models ───────────────────────────────────────────────────

@dataclass
class UDOSkill:
    id: str
    name: str
    description: str
    trigger: str  # 'event' | 'schedule' | 'manual'
    event_type: Optional[str] = None
    action: str = ""
    enabled: bool = True

@dataclass
class UDOTask:
    id: str
    type: str  # 'agent' | 'workflow' | 'autoloop'
    status: str = 'pending'  # 'running' | 'completed' | 'failed' | 'pending'
    priority: int = 0
    created_at: str = ""
    updated_at: str = ""

@dataclass
class UDOVariable:
    key: str
    value: str
    scope: str = 'user'  # 'user' | 'workspace' | 'system'
    encrypted: bool = False
    used_by: List[str] = field(default_factory=list)

@dataclass
class UDOAgent:
    id: str
    name: str
    type: str = 'generic'
    status: str = 'idle'  # 'idle' | 'running' | 'error'
    health: int = 100
    tasks_completed: int = 0

@dataclass
class UDOWorkflow:
    id: str
    name: str
    file: str = ""
    type: str = 'snack'
    status: str = 'active'  # 'active' | 'disabled' | 'error'
    runs: int = 0
    last_run: Optional[str] = None

@dataclass
class UDOPublishTarget:
    id: str
    name: str
    type: str  # 'github' | 'wordpress' | 'local'
    status: str = 'disconnected'  # 'connected' | 'disconnected' | 'error'

@dataclass
class MCPServerStatus:
    id: str
    name: str
    running: bool = False
    output: List[str] = field(default_factory=list)
    error: Optional[str] = None
    started_at: Optional[int] = None

@dataclass
class CheckResult:
    id: str
    name: str
    status: str = 'running'  # 'pass' | 'fail' | 'running'
    duration: float = 0.0
    timestamp: str = ""
    output: str = ""
    repository: str = ""


# ─── Runtime ───────────────────────────────────────────────────────

class UDORuntime:
    """
    Central UDO runtime that manages all subsystems.
    In-memory store with optional file persistence.
    """

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir or os.path.expanduser("~/.udos/runtime"))
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # In-memory stores
        self.skills: Dict[str, UDOSkill] = {}
        self.tasks: Dict[str, UDOTask] = {}
        self.variables: Dict[str, UDOVariable] = {}
        self.agents: Dict[str, UDOAgent] = {}
        self.workflows: Dict[str, UDOWorkflow] = {}
        self.publish_targets: Dict[str, UDOPublishTarget] = {}
        self.mcp_servers: Dict[str, MCPServerStatus] = {}
        self.checks: Dict[str, CheckResult] = {}

        # Load persisted state
        self._load_state()

        # Seed defaults
        self._seed_defaults()

    # ─── Persistence ───────────────────────────────────────────────

    def _state_path(self, name: str) -> Path:
        return self.data_dir / f"{name}.json"

    def _save_state(self, name: str, data: Any):
        path = self._state_path(name)
        path.write_text(json.dumps(data, indent=2, default=str))

    def _load_state_file(self, name: str) -> list:
        path = self._state_path(name)
        if path.exists():
            return json.loads(path.read_text())
        return []

    def _load_state(self):
        for key, cls in [
            ("skills", UDOSkill),
            ("tasks", UDOTask),
            ("variables", UDOVariable),
            ("agents", UDOAgent),
            ("workflows", UDOWorkflow),
            ("publish_targets", UDOPublishTarget),
            ("mcp_servers", MCPServerStatus),
            ("checks", CheckResult),
        ]:
            items = self._load_state_file(key)
            store = getattr(self, key)
            store.clear()
            for item in items:
                obj = cls(**item)
                store[obj.id] = obj

    def _persist(self, name: str):
        store = getattr(self, name)
        self._save_state(name, [asdict(v) for v in store.values()])

    # ─── Defaults ──────────────────────────────────────────────────

    def _seed_defaults(self):
        if not self.skills:
            self.skills["skill-vault-sync"] = UDOSkill(
                id="skill-vault-sync",
                name="Vault Sync",
                description="Sync vault with remote repository",
                trigger="manual",
                action="vault-sync",
            )
            self.skills["skill-health-check"] = UDOSkill(
                id="skill-health-check",
                name="Health Check",
                description="Run system health diagnostics",
                trigger="schedule",
                event_type="cron:*/5 * * * *",
                action="health-check",
            )
            self._persist("skills")

        if not self.agents:
            self.agents["agent-default"] = UDOAgent(
                id="agent-default",
                name="Default Agent",
                type="generic",
            )
            self._persist("agents")

        if not self.workflows:
            self.workflows["wf-health"] = UDOWorkflow(
                id="wf-health",
                name="Health Monitor",
                file="snacks/health-monitor.yaml",
                type="snack",
            )
            self._persist("workflows")

        if not self.checks:
            self.checks["check-vault"] = CheckResult(
                id="check-vault",
                name="Vault Integrity",
                status="pass",
                timestamp=datetime.now().isoformat(),
                output="Vault is healthy",
                repository="local",
            )
            self._persist("checks")

    # ─── Skills ────────────────────────────────────────────────────

    def list_skills(self) -> List[UDOSkill]:
        return list(self.skills.values())

    def enable_skill(self, skill_id: str) -> bool:
        if skill_id in self.skills:
            self.skills[skill_id].enabled = True
            self._persist("skills")
            return True
        return False

    def disable_skill(self, skill_id: str) -> bool:
        if skill_id in self.skills:
            self.skills[skill_id].enabled = False
            self._persist("skills")
            return True
        return False

    def run_skill(self, skill_id: str) -> Dict[str, Any]:
        if skill_id not in self.skills:
            return {"success": False, "result": "Skill not found"}
        skill = self.skills[skill_id]
        # Execute the skill action
        result = self._execute_action(skill.action)
        return {"success": True, "result": result}

    # ─── Tasks ─────────────────────────────────────────────────────

    def list_tasks(self) -> List[UDOTask]:
        return sorted(list(self.tasks.values()), key=lambda t: t.priority, reverse=True)

    def create_task(self, task_type: str, priority: int = 0) -> UDOTask:
        task = UDOTask(
            id=f"task-{uuid.uuid4().hex[:8]}",
            type=task_type,
            status="pending",
            priority=priority,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        self.tasks[task.id] = task
        self._persist("tasks")
        return task

    def cancel_task(self, task_id: str) -> bool:
        if task_id in self.tasks:
            self.tasks[task_id].status = "failed"
            self.tasks[task_id].updated_at = datetime.now().isoformat()
            self._persist("tasks")
            return True
        return False

    def retry_task(self, task_id: str) -> bool:
        if task_id in self.tasks:
            self.tasks[task_id].status = "pending"
            self.tasks[task_id].updated_at = datetime.now().isoformat()
            self._persist("tasks")
            return True
        return False

    # ─── Variables ─────────────────────────────────────────────────

    def list_variables(self) -> List[UDOVariable]:
        return list(self.variables.values())

    def set_variable(self, key: str, value: str, scope: str = "user", encrypted: bool = False) -> bool:
        self.variables[key] = UDOVariable(
            key=key,
            value=value,
            scope=scope,
            encrypted=encrypted,
        )
        self._persist("variables")
        return True

    def delete_variable(self, key: str) -> bool:
        if key in self.variables:
            del self.variables[key]
            self._persist("variables")
            return True
        return False

    # ─── Agents ────────────────────────────────────────────────────

    def list_agents(self) -> List[UDOAgent]:
        return list(self.agents.values())

    def start_agent(self, agent_id: str) -> bool:
        if agent_id in self.agents:
            self.agents[agent_id].status = "running"
            self._persist("agents")
            return True
        return False

    def stop_agent(self, agent_id: str) -> bool:
        if agent_id in self.agents:
            self.agents[agent_id].status = "idle"
            self._persist("agents")
            return True
        return False

    def get_agent_health(self, agent_id: str) -> Dict[str, Any]:
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            return {"health": agent.health, "status": agent.status}
        return {"health": 0, "status": "unknown"}

    # ─── Workflows ─────────────────────────────────────────────────

    def list_workflows(self) -> List[UDOWorkflow]:
        return list(self.workflows.values())

    def run_workflow(self, workflow_id: str) -> bool:
        if workflow_id in self.workflows:
            wf = self.workflows[workflow_id]
            wf.runs += 1
            wf.last_run = datetime.now().isoformat()
            self._persist("workflows")
            return True
        return False

    def disable_workflow(self, workflow_id: str) -> bool:
        if workflow_id in self.workflows:
            self.workflows[workflow_id].status = "disabled"
            self._persist("workflows")
            return True
        return False

    def create_workflow(self, name: str, description: str = "") -> UDOWorkflow:
        wf_id = f"wf-{uuid.uuid4().hex[:8]}"
        wf = UDOWorkflow(
            id=wf_id,
            name=name,
            file=f"snacks/{wf_id}.yaml",
            type="snack",
            status="active",
        )
        self.workflows[wf.id] = wf
        self._persist("workflows")
        return wf

    # ─── Publish ───────────────────────────────────────────────────

    def list_publish_targets(self) -> List[UDOPublishTarget]:
        return list(self.publish_targets.values())

    def publish_to(self, target_id: str, content: Any) -> Dict[str, Any]:
        if target_id not in self.publish_targets:
            return {"success": False, "url": None}
        target = self.publish_targets[target_id]
        # Placeholder: actual publish logic per target type
        return {"success": True, "url": f"https://publish.udos/{target.name}/{uuid.uuid4().hex[:8]}"}

    # ─── Vault ─────────────────────────────────────────────────────

    def list_vault_entries(self, path: str = "/") -> List[Dict[str, Any]]:
        vault_dir = Path(os.path.expanduser("~/Vault"))
        target = vault_dir / path.lstrip("/")
        if not target.exists():
            return []
        entries = []
        for item in target.iterdir():
            entries.append({
                "name": item.name,
                "type": "dir" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else 0,
                "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
            })
        return sorted(entries, key=lambda e: (e["type"] != "dir", e["name"]))

    def read_vault_file(self, path: str) -> Dict[str, Any]:
        vault_dir = Path(os.path.expanduser("~/Vault"))
        target = vault_dir / path.lstrip("/")
        if not target.exists() or not target.is_file():
            return {"content": "", "metadata": {}}
        return {
            "content": target.read_text(),
            "metadata": {
                "name": target.name,
                "size": target.stat().st_size,
                "modified": datetime.fromtimestamp(target.stat().st_mtime).isoformat(),
            },
        }

    def write_vault_file(self, path: str, content: str) -> bool:
        vault_dir = Path(os.path.expanduser("~/Vault"))
        target = vault_dir / path.lstrip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return True

    # ─── MCP ───────────────────────────────────────────────────────

    def get_mcp_status(self) -> List[MCPServerStatus]:
        return list(self.mcp_servers.values())

    def start_mcp_server(self, server_id: str) -> bool:
        if server_id in self.mcp_servers:
            self.mcp_servers[server_id].running = True
            self.mcp_servers[server_id].started_at = int(time.time())
            self._persist("mcp_servers")
            return True
        return False

    def stop_mcp_server(self, server_id: str) -> bool:
        if server_id in self.mcp_servers:
            self.mcp_servers[server_id].running = False
            self._persist("mcp_servers")
            return True
        return False

    def call_mcp_tool(self, server_id: str, tool: str, args: Dict[str, Any]) -> Any:
        if server_id not in self.mcp_servers:
            return {"error": f"MCP server {server_id} not found"}
        if not self.mcp_servers[server_id].running:
            return {"error": f"MCP server {server_id} is not running"}
        # Placeholder: actual MCP tool call
        return {"result": f"Called {tool} on {server_id} with {args}"}

    # ─── Checks ────────────────────────────────────────────────────

    def list_checks(self) -> List[CheckResult]:
        return list(self.checks.values())

    def run_check(self, check_id: str) -> bool:
        if check_id in self.checks:
            check = self.checks[check_id]
            check.status = "running"
            check.timestamp = datetime.now().isoformat()
            start = time.time()
            # Simulate check execution
            check.status = "pass"
            check.duration = time.time() - start
            check.output = f"Check {check.name} passed"
            self._persist("checks")
            return True
        return False

    def get_check_results(self, check_id: str) -> Optional[CheckResult]:
        return self.checks.get(check_id)

    # ─── Command Execution ─────────────────────────────────────────

    def execute_command(self, command: str) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                shlex.split(command),
                capture_output=True,
                text=True,
                timeout=30,
            )
            return {
                "output": result.stdout + result.stderr,
                "exitCode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"output": "Command timed out", "exitCode": -1}
        except Exception as e:
            return {"output": str(e), "exitCode": -1}

    # ─── Internal ──────────────────────────────────────────────────

    def _execute_action(self, action: str) -> str:
        """Execute a skill action."""
        actions = {
            "vault-sync": "Vault sync initiated",
            "health-check": "System health: OK",
        }
        return actions.get(action, f"Unknown action: {action}")
