# tasks/notify_skill_publish.py

from celery_app import app
from bson import ObjectId
from core.config import settings
from tasks.sendgrid_utils import send_email
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List,Tuple
from uuid import UUID
import json
from tasks.models import (
    SkillModel,
    WorkspaceModel,
    WorkspaceMemberModel,
    UserRole,  UserModel
)
import uuid
from bson.binary import Binary, UUID_SUBTYPE

language = "he"

with open("templet_language/language.json", "r", encoding="utf-8") as f:
    templates = json.load(f)

skill_template = templates["skill"][language]
text_direction = "rtl" if language in ["he", "ar"] else "ltr"
text_align = "right" if language in ["he", "ar"] else "left"

client = AsyncIOMotorClient(settings.MONGO_URI)
source_db = client["htd-core-ms"]

def generate_skill_published_email_template(user_name, skill_name, workspace_name, creator_name, org_login_url):
    return {
        "subject": skill_template['subject'].format(skill_name=skill_name, creator_name=creator_name),
        "title": f"""
            <h1 style="
                text-align: center;
                font-size: 28px;
                color: #2b6cb0;
                margin-top: 0;
                margin-bottom: 30px;
                font-family: Arial, sans-serif;
            ">
                {skill_template['title']}
            </h1>
        """,

        "body": f"""
            <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; font-size: 16px; text-align: {text_align};" dir="{text_direction}">
                <p style="font-size: 18px; margin-bottom: 20px;">{skill_template['body']['hi']} {user_name},</p>
        
                <p>
                    {skill_template['body']['firstLinePatr1']}
                    <strong style="color: #2b6cb0;">{skill_name}</strong> 
                    {skill_template['body']['firstLinePatr2']}
                    <strong style="color: #2b6cb0;">{workspace_name}</strong> 
                    {skill_template['body']['firstLinePatr3']}
                    <strong>{creator_name}</strong>.
                </p>
        
                <p>{skill_template['body']['secondLine']}</p>
        
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{org_login_url}" 
                       style="display: inline-block; background-color: #4CAF50; color: white; text-decoration: none; 
                              padding: 12px 24px; border-radius: 6px; font-weight: bold; font-size: 16px;">
                       {skill_template['body']['AccessTheSkill']}
                    </a>
                </div>
        
            </div>
        """,

        "footer": skill_template['footer']
    }


async def get_skill_and_workspace(skill_id: str) -> Tuple[SkillModel, WorkspaceModel]:
    """
        Get the Skill and associated Workspace from the database using the given skill_id.
        This function:
        1. Converts the string skill_id into UUID and Binary format for querying.
        2. Fetches the Skill document from the 'skills' collection.
        3. Extracts the first workspace_id from the skill.
        4. Fetches the corresponding Workspace document from the 'workspaces' collection.
        5. Returns both as Pydantic models (SkillModel and WorkspaceModel).
        Raises a ValueError if the skill or workspace cannot be found.
    """
    uuid_value = uuid.UUID(skill_id)
    binary_id = Binary(uuid_value.bytes, subtype=UUID_SUBTYPE)

    skill_doc = await source_db["skills"].find_one({"id": binary_id})
    if not skill_doc:
        raise ValueError("Skill not found")

    skill = SkillModel(**skill_doc)

    if not skill.workspace_ids:
        raise ValueError("No workspace IDs found in skill")

    workspace_id = skill.workspace_ids[0]
    binary_ws_id = Binary.from_uuid(workspace_id, UUID_SUBTYPE)
    ws_doc = await source_db["workspaces"].find_one({"id": binary_ws_id})
    if not ws_doc:
        raise ValueError("Workspace not found")

    workspace = WorkspaceModel(**ws_doc)

    return skill, workspace
@app.task
async def notify_skill_published(skill_id: str):
    try:
        skill, workspace = await get_skill_and_workspace(skill_id)

        creator_doc = await source_db.users.find_one({
            "id": Binary(skill.created_by_uid.bytes, UUID_SUBTYPE)
        })
        if not creator_doc:
            raise ValueError("Creator not found")
        creator = UserModel(**creator_doc)

        learner_ids = [
            Binary(member.user_id.bytes, UUID_SUBTYPE)
            for member in workspace.members
            if member.role in [UserRole.LEARNER, UserRole.VIEWER]
        ]

        learners_docs = await source_db["users"].find({
            "id": {"$in": learner_ids}
        }).to_list(length=None)

        learners = [UserModel(**doc) for doc in learners_docs]

        for user in learners:
            dynamic_data = generate_skill_published_email_template(
                user_name=user.full_name,
                skill_name=skill.name,
                workspace_name=workspace.name,
                creator_name=creator.full_name,
                org_login_url=f"https://app.betayeda.com/org/{workspace.id}"
            )

            await send_email(
                to_email=user.email,
                dynamic_data=dynamic_data,
                template_id=settings.SENDGRID_SKILL_PUBLISHED_TEMPLATE_ID,
                subject=dynamic_data["subject"]
            )

            print(f"✔Email sent to: {user.full_name} <{user.email}>")


    except ValueError as e:
        print(f"Skill publish email aborted: {e}")
