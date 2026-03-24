from uuid import UUID, uuid4
import random
from datetime import datetime

from sqlalchemy import DDL, String, DateTime, event, func
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column


def _random_color() -> str:
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


class TaskStatus(Base):
    __tablename__ = "task_statuses"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(20), nullable=False)
    color_hash: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default=_random_color,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )


_create_prevent_delete_fn = DDL(
    """
    CREATE OR REPLACE FUNCTION prevent_system_status_delete()
    RETURNS TRIGGER AS $$
    BEGIN
        IF OLD.id IN (
            '00000000-0000-0000-0000-000000000001',
            '00000000-0000-0000-0000-000000000002',
            '00000000-0000-0000-0000-000000000003',
            '00000000-0000-0000-0000-000000000004'
        ) THEN
            RAISE EXCEPTION 'Cannot delete system status: %', OLD.title;
        END IF;
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
"""
)

_create_prevent_delete_trigger = DDL(
    """
    CREATE TRIGGER prevent_system_status_delete
    BEFORE DELETE ON task_statuses
    FOR EACH ROW
    EXECUTE FUNCTION prevent_system_status_delete();
"""
)

_seed_statuses = DDL(
    """
    INSERT INTO task_statuses (id, title, color_hash) VALUES
        ('00000000-0000-0000-0000-000000000001', 'To Do',        '#6b7280'),
        ('00000000-0000-0000-0000-000000000002', 'In Progress',  '#3b82f6'),
        ('00000000-0000-0000-0000-000000000003', 'Review',       '#f59e0b'),
        ('00000000-0000-0000-0000-000000000004', 'Done',         '#22c55e')
    ON CONFLICT DO NOTHING;
"""
)

event.listen(TaskStatus.__table__, "after_create", _create_prevent_delete_fn)
event.listen(TaskStatus.__table__, "after_create", _create_prevent_delete_trigger)
event.listen(TaskStatus.__table__, "after_create", _seed_statuses)
