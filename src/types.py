from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class AgentTask:
    agent: str          # "researcher" | "publisher"
    instructions: str   # CEO-written task brief
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None


@dataclass
class WorkflowContext:
    topic: str
    objectives: str = ""           # CEO-written objectives
    tasks: list[AgentTask] = field(default_factory=list)
    research_output: str = ""
    published_pdf_path: str = ""
    review_approved: bool = False
    review_feedback: str = ""
