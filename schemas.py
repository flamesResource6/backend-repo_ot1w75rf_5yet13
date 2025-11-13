"""
Database Schemas for Tidya

Each Pydantic model represents a MongoDB collection. The collection name is
the lowercase of the class name (e.g., Deck -> "deck").
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

# Core app schemas

class Deck(BaseModel):
    """A workspace where users add and organize items."""
    title: str = Field(..., description="Deck title")
    description: Optional[str] = Field(None, description="Short description of this deck")
    color: Optional[str] = Field(None, description="Optional color theme (e.g., indigo, emerald)")

class Item(BaseModel):
    """An item inside a deck that can represent notes, tasks, ideas, or entries."""
    deck_id: str = Field(..., description="Reference to the deck this item belongs to")
    content: str = Field(..., description="Primary text content of the item")
    type: Literal["note", "task", "journal", "idea"] = Field("note", description="Item type")
    status: Literal["todo", "in_progress", "done", "none"] = Field("none", description="Workflow status")
    tags: List[str] = Field(default_factory=list, description="List of tags")
    due_date: Optional[datetime] = Field(None, description="Optional due date for tasks or timeline views")
    priority: Optional[Literal["low", "medium", "high"]] = Field(None, description="Optional priority for tasks")

# Optional examples kept for reference (not used by app)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True

# Utility to expose schemas to viewers/inspectors

def get_schema_definitions():
    """Return lightweight schema metadata for the viewer/UI."""
    return {
        "deck": {
            "fields": {
                "title": "str",
                "description": "Optional[str]",
                "color": "Optional[str]",
            }
        },
        "item": {
            "fields": {
                "deck_id": "str",
                "content": "str",
                "type": "'note'|'task'|'journal'|'idea'",
                "status": "'todo'|'in_progress'|'done'|'none'",
                "tags": "List[str]",
                "due_date": "Optional[datetime]",
                "priority": "Optional['low'|'medium'|'high']",
            }
        }
    }
