from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from app.models.api_call import APICall
from app.schemas.api_call import APICallCreate, APICallFilter, APICallStats

def create_api_call(db: Session, api_call: APICallCreate) -> APICall:
    """Create a new API call record"""
    db_api_call = APICall(**api_call.dict())
    db.add(db_api_call)
    db.commit()
    db.refresh(db_api_call)
    return db_api_call

def get_api_calls(
    db: Session, 
    filter_params: APICallFilter,
    skip: int = 0, 
    limit: int = 100
) -> List[APICall]:
    """Get API calls with filtering"""
    query = db.query(APICall)
    
    # Apply filters
    if filter_params.tenant_id is not None:
        query = query.filter(APICall.tenant_id == filter_params.tenant_id)
    
    if filter_params.date_from is not None:
        query = query.filter(APICall.created_at >= filter_params.date_from)
    
    if filter_params.date_to is not None:
        query = query.filter(APICall.created_at <= filter_params.date_to)
    
    if filter_params.endpoint is not None:
        query = query.filter(APICall.endpoint.contains(filter_params.endpoint))
    
    if filter_params.method is not None:
        query = query.filter(APICall.method == filter_params.method)
    
    if filter_params.response_status is not None:
        query = query.filter(APICall.response_status == filter_params.response_status)
    
    # Order by most recent first
    query = query.order_by(APICall.created_at.desc())
    
    return query.offset(skip).limit(limit).all()

def get_api_calls_count(
    db: Session, 
    filter_params: APICallFilter
) -> int:
    """Get total count of API calls with filtering"""
    query = db.query(APICall)
    
    # Apply filters
    if filter_params.tenant_id is not None:
        query = query.filter(APICall.tenant_id == filter_params.tenant_id)
    
    if filter_params.date_from is not None:
        query = query.filter(APICall.created_at >= filter_params.date_from)
    
    if filter_params.date_to is not None:
        query = query.filter(APICall.created_at <= filter_params.date_to)
    
    if filter_params.endpoint is not None:
        query = query.filter(APICall.endpoint.contains(filter_params.endpoint))
    
    if filter_params.method is not None:
        query = query.filter(APICall.method == filter_params.method)
    
    if filter_params.response_status is not None:
        query = query.filter(APICall.response_status == filter_params.response_status)
    
    return query.count()

def get_api_call_stats(
    db: Session, 
    filter_params: APICallFilter
) -> APICallStats:
    """Get statistics for API calls"""
    query = db.query(APICall)
    
    # Apply same filters as get_api_calls
    if filter_params.tenant_id is not None:
        query = query.filter(APICall.tenant_id == filter_params.tenant_id)
    
    if filter_params.date_from is not None:
        query = query.filter(APICall.created_at >= filter_params.date_from)
    
    if filter_params.date_to is not None:
        query = query.filter(APICall.created_at <= filter_params.date_to)
    
    if filter_params.endpoint is not None:
        query = query.filter(APICall.endpoint.contains(filter_params.endpoint))
    
    if filter_params.method is not None:
        query = query.filter(APICall.method == filter_params.method)
    
    if filter_params.response_status is not None:
        query = query.filter(APICall.response_status == filter_params.response_status)
    
    # Get total calls
    total_calls = query.count()
    
    if total_calls == 0:
        return APICallStats(
            total_calls=0,
            total_processing_time=0.0,
            avg_processing_time=0.0,
            total_response_size=0,
            avg_response_size=0.0,
            success_rate=0.0,
            calls_by_endpoint={},
            calls_by_status={}
        )
    
    # Get processing time stats
    processing_stats = query.with_entities(
        func.sum(APICall.processing_time).label('total_time'),
        func.avg(APICall.processing_time).label('avg_time'),
        func.sum(APICall.response_size).label('total_size'),
        func.avg(APICall.response_size).label('avg_size')
    ).first()
    
    # Get success rate
    success_calls = query.filter(APICall.response_status < 400).count()
    success_rate = (success_calls / total_calls) * 100 if total_calls > 0 else 0
    
    # Get calls by endpoint
    endpoint_stats = query.with_entities(
        APICall.endpoint,
        func.count(APICall.id).label('count')
    ).group_by(APICall.endpoint).all()
    
    calls_by_endpoint = {row.endpoint: row.count for row in endpoint_stats}
    
    # Get calls by status
    status_stats = query.with_entities(
        APICall.response_status,
        func.count(APICall.id).label('count')
    ).group_by(APICall.response_status).all()
    
    calls_by_status = {row.response_status: row.count for row in status_stats}
    
    return APICallStats(
        total_calls=total_calls,
        total_processing_time=processing_stats.total_time or 0.0,
        avg_processing_time=processing_stats.avg_time or 0.0,
        total_response_size=processing_stats.total_size or 0,
        avg_response_size=processing_stats.avg_size or 0.0,
        success_rate=success_rate,
        calls_by_endpoint=calls_by_endpoint,
        calls_by_status=calls_by_status
    )

def get_api_calls_by_date_range(
    db: Session,
    tenant_id: Optional[int] = None,
    date_range: str = "today"
) -> List[APICall]:
    """Get API calls for common date ranges"""
    now = datetime.utcnow()
    
    if date_range == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == "this_week":
        start_date = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == "last_week":
        start_date = (now - timedelta(days=now.weekday() + 7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=7)
    elif date_range == "this_month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == "last_month":
        if now.month == 1:
            start_date = now.replace(year=now.year-1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = now.replace(month=now.month-1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date.replace(day=28) + timedelta(days=4)
        end_date = end_date.replace(day=1) - timedelta(days=1)
    elif date_range == "this_year":
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif date_range == "last_year":
        start_date = now.replace(year=now.year-1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(year=now.year-1, month=12, day=31, hour=23, minute=59, second=59)
    else:
        # Default to today
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    
    query = db.query(APICall).filter(
        APICall.created_at >= start_date,
        APICall.created_at <= end_date
    )
    
    if tenant_id is not None:
        query = query.filter(APICall.tenant_id == tenant_id)
    
    return query.order_by(APICall.created_at.desc()).all()

def delete_old_api_calls(db: Session, days: int = 90) -> int:
    """Delete API calls older than specified days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    result = db.query(APICall).filter(APICall.created_at < cutoff_date).delete()
    db.commit()
    return result 