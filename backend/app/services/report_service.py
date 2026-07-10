from sqlalchemy.orm import Session
from ..database import crud


def get_reports(db: Session, limit: int = 20) -> list[dict]:
    reports = crud.get_ai_reports(db, limit)
    return [{"id": r.id, "report_type": r.report_type, "content": r.content,
             "generated_at": str(r.generated_at), "generated_by": r.generated_by} for r in reports]


def get_report_by_id(db: Session, report_id: int) -> dict | None:
    r = crud.get_ai_report_by_id(db, report_id)
    if not r:
        return None
    return {"id": r.id, "report_type": r.report_type, "content": r.content,
            "generated_at": str(r.generated_at), "generated_by": r.generated_by}
