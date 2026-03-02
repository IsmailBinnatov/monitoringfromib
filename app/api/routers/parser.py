from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

from app.models import User as UserModel, UserRole, SystemTask
from app.auth.auth import get_current_user, is_super_admin
from app.database import get_async_db
from app.parser.parser import main

from app import exceptions
from app.logs.logger import logger


router = APIRouter(
    prefix="/parser",
    tags=["Parser Control"]
)


@router.post("/run")
async def parser_trigger(
    background_tasks: BackgroundTasks,
    offset: int = 0,
    limit: int = 10,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """The parser trigger, gets offset and limit params (except for the semaphore for donor-site safety), can only be used by authorized users and only once per hour."""
    logger.info("The parser started from endpoint")
    task = (await db.scalars(select(SystemTask).where(SystemTask.task_name == "product_parsing"))).first()
    now = datetime.now(timezone.utc)

    if current_user.role != UserRole.SUPER_ADMIN:
        if task and task.last_run_at:
            time_passed = now - task.last_run_at
            if time_passed < timedelta(hours=1):
                minutes_left = 60 - int(time_passed.total_seconds() / 60)
                exceptions.too_many_requests_429(
                    f"The parser has already been launched recently. Please wait for {minutes_left} minutes.")

    if not task:
        task = SystemTask(
            task_name="product_parsing",
            last_run_at=now,
            status="running",
            user_id=current_user.id
        )
        db.add(task)
    else:
        task.last_run_at = now
        task.status = "running"
        task.user_id = current_user.id

    await db.commit()

    background_tasks.add_task(main, offset, limit)

    return {
        "status": "success",
        "message": f"Parsing started (offset: {offset}, limit: {limit})."
    }


@router.post("/reset-timer")
async def reset_parsing_timer(
    db: AsyncSession = Depends(get_async_db),
    super_admin: UserModel = Depends(is_super_admin)
):
    """Endpoint for resetting the parser timer (only for super-admins)"""
    task = (await db.scalars(select(SystemTask).where(SystemTask.task_name == "product_parsing"))).first()

    if task:
        task.last_run_at = None
        task.status = "idle"
        await db.commit()
        logger.info(
            "The parser timer has been successfully reset  by super-admin")
        return {"message": "The timer has been successfully reset. The parser can be restarted."}

    return {"message": "No record for the parser has been created yet."}
