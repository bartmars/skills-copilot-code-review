"""Endpoints for school announcements."""

from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..database import announcements_collection
from .auth import get_authenticated_teacher

router = APIRouter(prefix="/announcements", tags=["announcements"])


class AnnouncementInput(BaseModel):
    message: str = Field(..., min_length=1, max_length=300)
    start_date: Optional[date] = None
    expiration_date: date


def serialize_announcement(announcement: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": announcement["_id"],
        "message": announcement["message"],
        "start_date": announcement.get("start_date"),
        "expiration_date": announcement["expiration_date"],
    }


def validate_dates(payload: AnnouncementInput) -> Dict[str, Any]:
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty")
    start_date = payload.start_date.isoformat() if payload.start_date else None
    expiration_date = payload.expiration_date.isoformat()
    if start_date and start_date > expiration_date:
        raise HTTPException(
            status_code=422,
            detail="Start date must be on or before the expiration date",
        )
    return {
        "message": message,
        "start_date": start_date,
        "expiration_date": expiration_date,
    }


@router.get("", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    today = date.today().isoformat()
    query = {
        "expiration_date": {"$gte": today},
        "$or": [
            {"start_date": None},
            {"start_date": {"$lte": today}},
        ],
    }
    return [
        serialize_announcement(item)
        for item in announcements_collection.find(query).sort("expiration_date", 1)
    ]


@router.get("/manage", response_model=List[Dict[str, Any]])
def list_announcements(
    teacher: Dict[str, Any] = Depends(get_authenticated_teacher),
) -> List[Dict[str, Any]]:
    return [
        serialize_announcement(item)
        for item in announcements_collection.find().sort("expiration_date", 1)
    ]


@router.post("", status_code=201, response_model=Dict[str, Any])
def create_announcement(
    payload: AnnouncementInput,
    teacher: Dict[str, Any] = Depends(get_authenticated_teacher),
) -> Dict[str, Any]:
    from secrets import token_urlsafe

    announcement = {"_id": token_urlsafe(12), **validate_dates(payload)}
    announcements_collection.insert_one(announcement)
    return serialize_announcement(announcement)


@router.put("/{announcement_id}", response_model=Dict[str, Any])
def update_announcement(
    announcement_id: str,
    payload: AnnouncementInput,
    teacher: Dict[str, Any] = Depends(get_authenticated_teacher),
) -> Dict[str, Any]:
    announcement = announcements_collection.find_one_and_update(
        {"_id": announcement_id},
        {"$set": validate_dates(payload)},
        return_document=True,
    )
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return serialize_announcement(announcement)


@router.delete("/{announcement_id}", status_code=204)
def delete_announcement(
    announcement_id: str,
    teacher: Dict[str, Any] = Depends(get_authenticated_teacher),
) -> None:
    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")