from db.repository import Repository
from db.session import SessionLocal
from db.models import Item


class ItemRepository(Repository):
    def __init__(self, session=None):
        self.session = session or SessionLocal()
        self.db = self.session

    def get_item(self, item_id: int):
        return self.db.query(Item).filter(Item.id == item_id).first()

    def list_items(self, show_id: int | None = None, status: str | None = None):
        query = self.db.query(Item)
        if show_id is not None:
            query = query.filter(Item.show_id == show_id)
        if status is not None:
            query = query.filter(Item.status == status)
        return query.order_by(Item.id.desc()).all()

    def create_item(self, show_id: int, title: str, description: str | None = None, image_url: str | None = None, start_price: float = 0, instant_buy_price: float | None = None, min_increment: float = 1, status: str = 'draft'):
        item = Item(
            show_id=show_id,
            title=title,
            description=description,
            image_url=image_url,
            start_price=start_price,
            instant_buy_price=instant_buy_price,
            min_increment=min_increment,
            status=status,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_item(self, item_id: int, **kwargs):
        item = self.get_item(item_id)
        if not item:
            return None
        for key, value in kwargs.items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item