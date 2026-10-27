from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ACTIVITIES_DIR = PROJECT_ROOT / "activities"
ALLOWED_FORMATS = {"online", "offline"}
FORMAT_LABELS = {"online": "线上", "offline": "线下"}


class ActivityError(ValueError):
    """活动包不存在或内容不符合约定。"""


@dataclass(frozen=True)
class ActivityProfile:
    id: str
    name: str
    formats: tuple[str, ...]
    audience: str
    organizer: str
    notice_channel: str
    assistant_role: str
    router_role: str
    prompt_audience: str
    assignment_contact: str
    knowledge_path: Path
    documents_path: Path | None
    description: str

    @property
    def format_label(self) -> str:
        return "、".join(FORMAT_LABELS[item] for item in self.formats)


def list_activities() -> list[ActivityProfile]:
    if not ACTIVITIES_DIR.is_dir():
        raise ActivityError(f"活动目录不存在：{ACTIVITIES_DIR}")
    profiles = [_load_activity_file(path) for path in sorted(ACTIVITIES_DIR.glob("*/activity.json"))]
    ids = [profile.id for profile in profiles]
    if len(ids) != len(set(ids)):
        raise ActivityError("活动包 ID 重复。")
    if "summer-camp" not in ids:
        raise ActivityError("缺少默认活动包 summer-camp。")
    return profiles


def load_activity(activity_id: str | None) -> ActivityProfile:
    target = (activity_id or "summer-camp").strip() or "summer-camp"
    for profile in list_activities():
        if profile.id == target:
            return profile
    known = "、".join(profile.id for profile in list_activities())
    raise ActivityError(f"未知活动 {target}。可选：{known}")


def _load_activity_file(path: Path) -> ActivityProfile:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ActivityError(f"活动包无法读取：{path}") from exc
    if not isinstance(raw, dict):
        raise ActivityError(f"活动包必须是 JSON 对象：{path}")

    required = [
        "id",
        "name",
        "formats",
        "audience",
        "organizer",
        "notice_channel",
        "assistant_role",
        "router_role",
        "prompt_audience",
        "assignment_contact",
        "knowledge",
        "description",
    ]
    missing = [field for field in required if field not in raw]
    if missing:
        raise ActivityError(f"{path} 缺少字段：{', '.join(missing)}")

    activity_id = str(raw["id"]).strip()
    if activity_id != path.parent.name:
        raise ActivityError(f"{path} 的 id 必须与目录名一致。")
    formats = raw["formats"]
    if not isinstance(formats, list) or not formats:
        raise ActivityError(f"{activity_id} 至少要声明一种形式：online 或 offline。")
    normalized_formats = tuple(str(item).strip() for item in formats)
    if any(item not in ALLOWED_FORMATS for item in normalized_formats):
        raise ActivityError(f"{activity_id} 的 formats 只能包含 online 和 offline。")

    knowledge_path = _resolve(str(raw["knowledge"]))
    if not knowledge_path.is_file():
        raise ActivityError(f"{activity_id} 的知识库不存在：{knowledge_path}")
    documents_raw = str(raw.get("documents") or "").strip()
    documents_path = _resolve(documents_raw) if documents_raw else None
    if documents_path is not None and not documents_path.is_dir():
        raise ActivityError(f"{activity_id} 的资料目录不存在：{documents_path}")

    return ActivityProfile(
        id=activity_id,
        name=str(raw["name"]).strip(),
        formats=normalized_formats,
        audience=str(raw["audience"]).strip(),
        organizer=str(raw["organizer"]).strip(),
        notice_channel=str(raw["notice_channel"]).strip(),
        assistant_role=str(raw["assistant_role"]).strip(),
        router_role=str(raw["router_role"]).strip(),
        prompt_audience=str(raw["prompt_audience"]).strip(),
        assignment_contact=str(raw["assignment_contact"]).strip(),
        knowledge_path=knowledge_path,
        documents_path=documents_path,
        description=str(raw["description"]).strip(),
    )


def _resolve(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path
