from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import IntEnum


class UserRole(IntEnum):
    CREATOR = 1
    ADMIN = 2
    LEARNER = 3
    VIEWER = 4

class WorkspaceMemberModel(BaseModel):
    user_id: UUID
    role: UserRole
    joined_at: Optional[datetime] = None


class WorkspaceModel(BaseModel):
    id: UUID
    name: str
    members: List[WorkspaceMemberModel]

class UserModel(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr

class SkillModel(BaseModel):
    id: UUID
    name: str
    published_at: Optional[datetime]
    due_date: Optional[datetime]
    workspace_ids: List[UUID]
    created_by_uid: UUID
