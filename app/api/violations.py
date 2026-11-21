from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from app.database.db import get_db
from app.models.violation import Violation
from app.models.result import Result
from app.models.assessment import Assessment
from app.models.user import User
from app.services.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/violations", tags=["Violations"])

MAX_VIOLATIONS = 5

class ViolationCreate(BaseModel):
    assessment_id: int
    violation_type: str

async def _violation_count(db: AsyncSession, user_id: int, assessment_id: int) -> int:
    result = await db.execute(
        select(func.count(Violation.id)).where(
            Violation.user_id == user_id,
            Violation.assessment_id == assessment_id,
        )
    )
    return result.scalar() or 0

def _limit_fields(count: int) -> dict:
    return {
        "count": count,
        "max_violations": MAX_VIOLATIONS,
        "remaining": max(0, MAX_VIOLATIONS - count),
        "blocked": count >= MAX_VIOLATIONS,
    }

@router.post("/")
async def log_violation(data: ViolationCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    violation = Violation(user_id=current_user.id, assessment_id=data.assessment_id, violation_type=data.violation_type)
    db.add(violation)
    await db.commit()
    count = await _violation_count(db, current_user.id, data.assessment_id)
    return {"message": "Violation logged", **_limit_fields(count)}

class FaceVerifyRequest(BaseModel):
    assessment_id: int
    image_base64: str
    strict: bool = False

@router.post("/verify-face")
async def verify_face(data: FaceVerifyRequest, current_user: User = Depends(get_current_user)):
    from app.services.vision import detect_faces

    result = detect_faces(data.image_base64, strict=data.strict)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

@router.get("/{assessment_id}")
async def get_violations(assessment_id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(
        select(Violation, User.fullname).join(User).where(Violation.assessment_id == assessment_id)
    )
    rows = result.all()
    return [{"id": v.id, "fullname": name, "violation_type": v.violation_type, "timestamp": v.timestamp} for v, name in rows]
