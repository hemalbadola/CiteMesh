from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    student = "student"
    mentor = "mentor"
    researcher = "researcher"
    admin = "admin"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    firebase_uid: str = Field(index=True, unique=True)
    email: Optional[str] = Field(default=None, index=True, nullable=True, unique=True)
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    role: UserRole = Field(default=UserRole.student)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    last_login_at: Optional[datetime] = None


class UserRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)  # type: ignore[assignment]

    id: int
    firebase_uid: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None


class Profile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True, unique=True)
    bio: Optional[str] = None
    affiliation: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class MentorStudentLink(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    mentor_id: int = Field(foreign_key="user.id", index=True)
    student_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class SavedPaper(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    paper_id: str = Field(index=True)
    title: str
    authors: Optional[str] = None
    summary: Optional[str] = None
    published_year: Optional[int] = None
    tags: Optional[str] = None
    saved_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ResearchChatSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str
    system_prompt: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ResearchChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="researchchatsession.id", index=True)
    sender: str = Field(description="user or assistant")
    content: str
    references: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class StudentActivity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    mentor_id: int = Field(foreign_key="user.id", index=True)
    student_id: int = Field(foreign_key="user.id", index=True)
    activity_type: str
    detail: Optional[str] = None
    metric_value: Optional[float] = None
    occurred_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class CitationLink(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    source_paper_id: str = Field(index=True)
    target_paper_id: str = Field(index=True)
    weight: float = Field(default=1.0)
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ResearchTimelineEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    concept: str
    description: Optional[str] = None
    year: Optional[int] = Field(default=None, index=True)
    source_paper_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Collection(SQLModel, table=True):
    """User-created collections of papers."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    name: str
    description: Optional[str] = None
    color: Optional[str] = Field(default="#6366f1")  # Default purple
    icon: Optional[str] = Field(default="📚")
    is_public: bool = Field(default=False)
    paper_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class CollectionPaper(SQLModel, table=True):
    """Papers within collections."""
    id: Optional[int] = Field(default=None, primary_key=True)
    collection_id: int = Field(foreign_key="collection.id", index=True)
    paper_id: str = Field(index=True)
    paper_title: str
    paper_authors: Optional[str] = None
    paper_year: Optional[int] = None
    note: Optional[str] = None
    order_index: int = Field(default=0)
    added_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class PaperCluster(SQLModel, table=True):
    """Auto-generated clusters from ML analysis."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    label: str
    description: Optional[str] = None
    method: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class PaperClusterMembership(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cluster_id: int = Field(foreign_key="papercluster.id", index=True)
    paper_id: str = Field(index=True)
    paper_title: Optional[str] = None
    note: Optional[str] = None
    added_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class LiteratureReview(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    topic: str
    prompt: Optional[str] = None
    content: Optional[str] = None
    status: str = Field(default="draft")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class PaperComparison(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    paper_a_id: str
    paper_b_id: str
    focus: Optional[str] = None
    summary: Optional[str] = None
    strengths_a: Optional[str] = None
    strengths_b: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ReadingGroup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    mentor_id: int = Field(foreign_key="user.id", index=True)
    name: str
    description: Optional[str] = None
    focus_area: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ReadingGroupMembership(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="readinggroup.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    role: str = Field(default="student")
    joined_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ReadingGroupPost(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="readinggroup.id", index=True)
    author_id: int = Field(foreign_key="user.id", index=True)
    content: str
    paper_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ContradictionFlag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    paper_id: str = Field(index=True)
    conflicting_paper_id: str = Field(index=True)
    summary: Optional[str] = None
    severity: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class LearningPath(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    mentor_id: int = Field(foreign_key="user.id", index=True)
    title: str
    description: Optional[str] = None
    skill_focus: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class LearningPathStep(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    path_id: int = Field(foreign_key="learningpath.id", index=True)
    step_order: int = Field(index=True)
    title: str
    description: Optional[str] = None
    resource_url: Optional[str] = None
    estimated_minutes: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
