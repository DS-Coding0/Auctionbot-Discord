from db.repository import Repository
from db.session import SessionLocal
from db.models import Show


class ShowRepository(Repository):
    def __init__(self, session=None):
        self.session = session or SessionLocal()
        self.db = self.session

    def get_show(self, show_id: int):
        return self.db.query(Show).filter(Show.id == show_id).first()

    def list_shows(self, server_id: int | None = None, seller_id: int | None = None, status: str | None = None):
        query = self.db.query(Show)
        if server_id is not None:
            query = query.filter(Show.server_id == server_id)
        if seller_id is not None:
            query = query.filter(Show.seller_id == seller_id)
        if status is not None:
            query = query.filter(Show.status == status)
        return query.order_by(Show.id.desc()).all()

    def create_show(self, server_id: int, seller_id: int, name: str, description: str | None = None, status: str = 'draft', starts_at=None, ends_at=None):
        show = Show(
            server_id=server_id,
            seller_id=seller_id,
            name=name,
            description=description,
            status=status,
            starts_at=starts_at,
            ends_at=ends_at,
        )
        self.db.add(show)
        self.db.commit()
        self.db.refresh(show)
        return show

    def update_show(self, show_id: int, **kwargs):
        show = self.get_show(show_id)
        if not show:
            return None
        for key, value in kwargs.items():
            setattr(show, key, value)
        self.db.commit()
        self.db.refresh(show)
        return show