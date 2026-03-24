from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.user import *
from app.models.team import *
from app.models.team_members import *
from app.models.task import *
from app.models.task_status import *
