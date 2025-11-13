"""
Mentor-Student Management API
==============================

DBMS Concepts Demonstrated:
- Self-referencing foreign keys (user → user)
- Complex JOINs across multiple tables
- Aggregate functions for analytics
- Window functions for rankings
- Subqueries for nested data
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import Session, select, func, and_, or_
from sqlalchemy import desc

from ..core.firebase_auth import FirebaseUser, get_current_user
from ..db import get_session
from ..models import (
    User, UserRole, MentorStudentLink, StudentActivity,
    SavedPaper, Collection, CitationLink, ResearchChatSession
)

router = APIRouter()


# ============================================
# Pydantic Models
# ============================================

class MentorLinkRequest(BaseModel):
    """Request to link mentor with student"""
    student_email: str


class StudentSummary(BaseModel):
    """Student summary for mentor dashboard"""
    id: int
    email: str
    full_name: Optional[str]
    display_name: Optional[str]
    papers_saved: int
    collections_created: int
    citations_made: int
    chat_sessions: int
    last_activity: Optional[datetime]
    mentorship_started: datetime
    activities_last_week: int


class StudentAnalytics(BaseModel):
    """Detailed analytics for a specific student"""
    student_id: int
    student_name: str
    total_papers: int
    total_collections: int
    total_citations: int
    total_chat_sessions: int
    papers_last_7_days: int
    papers_last_30_days: int
    avg_papers_per_week: float
    most_active_day: Optional[str]
    research_topics: List[str]
    last_activity: Optional[datetime]


class ActivityLogRequest(BaseModel):
    """Log student activity"""
    student_id: int
    activity_type: str
    detail: Optional[str] = None
    metric_value: Optional[float] = None


# ============================================
# Mentor-Student Linking
# ============================================

@router.post("/link-student")
async def link_student_to_mentor(
    request: MentorLinkRequest,
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Link a student to current mentor
    
    DBMS Concepts:
    - Self-referencing foreign keys
    - Composite unique constraints
    - SELECT with WHERE clause
    """
    # Find student by email
    student_stmt = select(User).where(User.email == request.student_email)
    student = session.exec(student_stmt).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with email {request.student_email} not found"
        )
    
    # Check if link already exists
    link_stmt = select(MentorStudentLink).where(
        and_(
            MentorStudentLink.mentor_id == current_user.db_user.id,
            MentorStudentLink.student_id == student.id
        )
    )
    existing_link = session.exec(link_stmt).first()
    
    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student already linked to this mentor"
        )
    
    # Create link
    link = MentorStudentLink(
        mentor_id=current_user.db_user.id,
        student_id=student.id,
        created_at=datetime.utcnow()
    )
    
    session.add(link)
    session.commit()
    session.refresh(link)
    
    return {
        "message": "Student linked successfully",
        "link_id": link.id,
        "student_name": student.full_name or student.email
    }


@router.delete("/unlink-student/{student_id}")
async def unlink_student_from_mentor(
    student_id: int,
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Unlink a student from current mentor
    
    DBMS Concepts:
    - DELETE with WHERE clause
    - Composite key lookup
    """
    # Find link
    link_stmt = select(MentorStudentLink).where(
        and_(
            MentorStudentLink.mentor_id == current_user.db_user.id,
            MentorStudentLink.student_id == student_id
        )
    )
    link = session.exec(link_stmt).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student link not found"
        )
    
    session.delete(link)
    session.commit()
    
    return {"message": "Student unlinked successfully"}


@router.get("/my-students", response_model=List[StudentSummary])
async def get_my_students(
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get all students linked to current mentor with summary statistics
    
    DBMS Concepts Demonstrated:
    - Multi-table JOIN (6 tables)
    - LEFT JOIN for optional relationships
    - GROUP BY with multiple aggregations
    - Subquery for activities count
    - ORDER BY on computed columns
    """
    mentor_id = current_user.db_user.id
    
    # Complex query joining 6 tables with aggregations
    # This is more efficient than N+1 queries
    query = """
        SELECT 
            u.id,
            u.email,
            u.full_name,
            u.display_name,
            COUNT(DISTINCT sp.id) as papers_saved,
            COUNT(DISTINCT c.id) as collections_created,
            COUNT(DISTINCT cl.id) as citations_made,
            COUNT(DISTINCT rcs.id) as chat_sessions,
            MAX(sp.saved_at) as last_activity,
            msl.created_at as mentorship_started,
            (
                SELECT COUNT(*)
                FROM studentactivity sa
                WHERE sa.student_id = u.id 
                AND sa.mentor_id = :mentor_id
                AND sa.occurred_at > datetime('now', '-7 days')
            ) as activities_last_week
        FROM user u
        JOIN mentorstudentlink msl ON u.id = msl.student_id
        LEFT JOIN savedpaper sp ON u.id = sp.user_id
        LEFT JOIN collection c ON u.id = c.user_id
        LEFT JOIN citationlink cl ON u.id = cl.user_id
        LEFT JOIN researchchatsession rcs ON u.id = rcs.user_id
        WHERE msl.mentor_id = :mentor_id
        GROUP BY u.id, u.email, u.full_name, u.display_name, msl.created_at
        ORDER BY activities_last_week DESC, last_activity DESC
    """
    
    results = session.execute(query, {"mentor_id": mentor_id}).fetchall()
    
    return [
        StudentSummary(
            id=row[0],
            email=row[1],
            full_name=row[2],
            display_name=row[3],
            papers_saved=row[4],
            collections_created=row[5],
            citations_made=row[6],
            chat_sessions=row[7],
            last_activity=row[8],
            mentorship_started=row[9],
            activities_last_week=row[10]
        )
        for row in results
    ]


# ============================================
# Student Analytics
# ============================================

@router.get("/student/{student_id}/analytics", response_model=StudentAnalytics)
async def get_student_analytics(
    student_id: int,
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get detailed analytics for a specific student
    
    DBMS Concepts:
    - Multiple aggregate queries
    - Date range filtering
    - Subqueries for complex calculations
    """
    mentor_id = current_user.db_user.id
    
    # Verify student is linked to mentor
    link_stmt = select(MentorStudentLink).where(
        and_(
            MentorStudentLink.mentor_id == mentor_id,
            MentorStudentLink.student_id == student_id
        )
    )
    link = session.exec(link_stmt).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student not linked to this mentor"
        )
    
    # Get student info
    student = session.get(User, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Total papers
    total_papers_stmt = select(func.count(SavedPaper.id)).where(
        SavedPaper.user_id == student_id
    )
    total_papers = session.exec(total_papers_stmt).first() or 0
    
    # Total collections
    total_collections_stmt = select(func.count(Collection.id)).where(
        Collection.user_id == student_id
    )
    total_collections = session.exec(total_collections_stmt).first() or 0
    
    # Total citations
    total_citations_stmt = select(func.count(CitationLink.id)).where(
        CitationLink.user_id == student_id
    )
    total_citations = session.exec(total_citations_stmt).first() or 0
    
    # Total chat sessions
    total_chats_stmt = select(func.count(ResearchChatSession.id)).where(
        ResearchChatSession.user_id == student_id
    )
    total_chats = session.exec(total_chats_stmt).first() or 0
    
    # Papers last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    papers_7d_stmt = select(func.count(SavedPaper.id)).where(
        and_(
            SavedPaper.user_id == student_id,
            SavedPaper.saved_at >= seven_days_ago
        )
    )
    papers_7d = session.exec(papers_7d_stmt).first() or 0
    
    # Papers last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    papers_30d_stmt = select(func.count(SavedPaper.id)).where(
        and_(
            SavedPaper.user_id == student_id,
            SavedPaper.saved_at >= thirty_days_ago
        )
    )
    papers_30d = session.exec(papers_30d_stmt).first() or 0
    
    # Calculate avg papers per week
    # Get date of first paper
    first_paper_stmt = select(func.min(SavedPaper.saved_at)).where(
        SavedPaper.user_id == student_id
    )
    first_paper_date = session.exec(first_paper_stmt).first()
    
    avg_papers_per_week = 0.0
    if first_paper_date and total_papers > 0:
        weeks_active = (datetime.utcnow() - first_paper_date).days / 7
        if weeks_active > 0:
            avg_papers_per_week = total_papers / weeks_active
    
    # Get last activity
    last_activity_stmt = select(func.max(SavedPaper.saved_at)).where(
        SavedPaper.user_id == student_id
    )
    last_activity = session.exec(last_activity_stmt).first()
    
    # Get research topics (from paper tags)
    topics_stmt = select(SavedPaper.tags).where(
        and_(
            SavedPaper.user_id == student_id,
            SavedPaper.tags.isnot(None)
        )
    )
    tags_results = session.exec(topics_stmt).all()
    
    # Parse and count tags
    topic_counts = {}
    for tags in tags_results:
        if tags:
            for tag in tags.split(','):
                tag = tag.strip()
                if tag:
                    topic_counts[tag] = topic_counts.get(tag, 0) + 1
    
    # Get top 10 topics
    research_topics = sorted(topic_counts.keys(), key=lambda t: topic_counts[t], reverse=True)[:10]
    
    return StudentAnalytics(
        student_id=student_id,
        student_name=student.full_name or student.email or "Unknown",
        total_papers=int(total_papers),
        total_collections=int(total_collections),
        total_citations=int(total_citations),
        total_chat_sessions=int(total_chats),
        papers_last_7_days=int(papers_7d),
        papers_last_30_days=int(papers_30d),
        avg_papers_per_week=round(avg_papers_per_week, 2),
        most_active_day=None,  # TODO: Calculate from activity logs
        research_topics=research_topics,
        last_activity=last_activity
    )


# ============================================
# Activity Logging
# ============================================

@router.post("/log-activity")
async def log_student_activity(
    request: ActivityLogRequest,
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Log activity for a student (mentor only)
    
    DBMS Concepts:
    - INSERT operation
    - Foreign key validation
    - Timestamp tracking
    """
    mentor_id = current_user.db_user.id
    
    # Verify student is linked to mentor
    link_stmt = select(MentorStudentLink).where(
        and_(
            MentorStudentLink.mentor_id == mentor_id,
            MentorStudentLink.student_id == request.student_id
        )
    )
    link = session.exec(link_stmt).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student not linked to this mentor"
        )
    
    # Create activity log
    activity = StudentActivity(
        mentor_id=mentor_id,
        student_id=request.student_id,
        activity_type=request.activity_type,
        detail=request.detail,
        metric_value=request.metric_value,
        occurred_at=datetime.utcnow()
    )
    
    session.add(activity)
    session.commit()
    session.refresh(activity)
    
    return {
        "activity_id": activity.id,
        "message": "Activity logged successfully"
    }


@router.get("/student/{student_id}/activities")
async def get_student_activities(
    student_id: int,
    limit: int = Query(50, ge=1, le=200),
    days: int = Query(30, ge=1, le=365),
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get activity log for a student
    
    DBMS Concepts:
    - SELECT with WHERE and ORDER BY
    - Date range filtering
    - LIMIT for pagination
    """
    mentor_id = current_user.db_user.id
    
    # Verify student is linked to mentor
    link_stmt = select(MentorStudentLink).where(
        and_(
            MentorStudentLink.mentor_id == mentor_id,
            MentorStudentLink.student_id == student_id
        )
    )
    link = session.exec(link_stmt).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student not linked to this mentor"
        )
    
    # Get activities
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    activity_stmt = (
        select(StudentActivity)
        .where(
            and_(
                StudentActivity.student_id == student_id,
                StudentActivity.mentor_id == mentor_id,
                StudentActivity.occurred_at >= cutoff_date
            )
        )
        .order_by(StudentActivity.occurred_at.desc())
        .limit(limit)
    )
    
    activities = session.exec(activity_stmt).all()
    
    return {
        "activities": [
            {
                "id": a.id,
                "activity_type": a.activity_type,
                "detail": a.detail,
                "metric_value": a.metric_value,
                "occurred_at": a.occurred_at.isoformat()
            }
            for a in activities
        ]
    }


# ============================================
# Mentor Dashboard Summary
# ============================================

@router.get("/dashboard")
async def get_mentor_dashboard(
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get comprehensive mentor dashboard data
    
    DBMS Concepts:
    - Multiple aggregate queries
    - Subqueries for complex metrics
    - Performance optimization with single queries
    """
    mentor_id = current_user.db_user.id
    
    # Total students
    total_students_stmt = select(func.count(MentorStudentLink.id)).where(
        MentorStudentLink.mentor_id == mentor_id
    )
    total_students = session.exec(total_students_stmt).first() or 0
    
    # Active students (activity in last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    active_students_query = """
        SELECT COUNT(DISTINCT msl.student_id)
        FROM mentorstudentlink msl
        JOIN savedpaper sp ON msl.student_id = sp.user_id
        WHERE msl.mentor_id = :mentor_id
        AND sp.saved_at >= :cutoff_date
    """
    active_students = session.execute(
        active_students_query,
        {"mentor_id": mentor_id, "cutoff_date": seven_days_ago}
    ).scalar() or 0
    
    # Total papers saved by all students
    total_papers_query = """
        SELECT COUNT(sp.id)
        FROM mentorstudentlink msl
        JOIN savedpaper sp ON msl.student_id = sp.user_id
        WHERE msl.mentor_id = :mentor_id
    """
    total_papers = session.execute(
        total_papers_query,
        {"mentor_id": mentor_id}
    ).scalar() or 0
    
    # Papers this week
    papers_this_week_query = """
        SELECT COUNT(sp.id)
        FROM mentorstudentlink msl
        JOIN savedpaper sp ON msl.student_id = sp.user_id
        WHERE msl.mentor_id = :mentor_id
        AND sp.saved_at >= :cutoff_date
    """
    papers_this_week = session.execute(
        papers_this_week_query,
        {"mentor_id": mentor_id, "cutoff_date": seven_days_ago}
    ).scalar() or 0
    
    return {
        "total_students": int(total_students),
        "active_students_last_7_days": int(active_students),
        "inactive_students": int(total_students) - int(active_students),
        "total_papers_saved": int(total_papers),
        "papers_saved_this_week": int(papers_this_week),
        "avg_papers_per_student": round(int(total_papers) / max(int(total_students), 1), 2)
    }
