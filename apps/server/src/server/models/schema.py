from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    """Telegram user that interacts with the bot."""

    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # relationships
    tracked_items: Mapped[list["TrackedItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Provider(Base):
    """
    Available data providers.
    Seeded on startup: mercadolibre, ebay, scraperapi.
    """

    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # relationships
    tracked_items: Mapped[list["TrackedItem"]] = relationship(back_populates="provider")


class TrackedItem(Base):
    """
    Item tracked by a user. Can be:
    - type='product': a specific product identified by URL or external_id
    - type='list':    a search query that returns up to list_limit products
    """

    __tablename__ = "tracked_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("providers.id"), nullable=False)

    # 'product' | 'list'
    type: Mapped[str] = mapped_column(String(16), nullable=False)

    # shared
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    last_checked: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # only for type='product'
    url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    target_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # only for type='list'
    query: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    list_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5

    # relationships
    user: Mapped["User"] = relationship(back_populates="tracked_items")
    provider: Mapped["Provider"] = relationship(back_populates="tracked_items")
    list_products: Mapped[list["ListProduct"]] = relationship(
        back_populates="tracked_item", cascade="all, delete-orphan"
    )
    price_history: Mapped[list["PriceHistory"]] = relationship(
        back_populates="tracked_item", cascade="all, delete-orphan"
    )


class ListProduct(Base):
    """
    Individual products captured on the first search of a type='list' TrackedItem.
    These are fixed after the first fetch and tracked individually from that point on.
    """

    __tablename__ = "list_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("tracked_items.id"), nullable=False)
    external_id: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)

    # relationships
    tracked_item: Mapped["TrackedItem"] = relationship(back_populates="list_products")
    price_history: Mapped[list["PriceHistory"]] = relationship(
        back_populates="list_product", cascade="all, delete-orphan"
    )


class PriceHistory(Base):
    """
    Price record for a tracked item or a specific product within a list.
    Used to calculate weekly and last-week averages.

    - For type='product': list_product_id is null, item_id points to the TrackedItem
    - For type='list':    list_product_id points to the specific ListProduct
    """

    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("tracked_items.id"), nullable=False)
    list_product_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("list_products.id"), nullable=True
    )
    price: Mapped[float] = mapped_column(Float, nullable=False)
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # relationships
    tracked_item: Mapped["TrackedItem"] = relationship(back_populates="price_history")
    list_product: Mapped[Optional["ListProduct"]] = relationship(back_populates="price_history")