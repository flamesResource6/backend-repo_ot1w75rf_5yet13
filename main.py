import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents

app = FastAPI(title="Tidya Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Models for requests ----------
class CreateDeckRequest(BaseModel):
    title: str
    description: Optional[str] = None
    color: Optional[str] = None

class CreateItemRequest(BaseModel):
    deck_id: str
    content: str
    type: str = "note"  # note | task | journal | idea
    status: str = "none"  # todo | in_progress | done | none
    tags: List[str] = []
    due_date: Optional[str] = None  # ISO datetime string
    priority: Optional[str] = None  # low | medium | high


# ---------- Helpers ----------

def as_str_id(doc):
    if not doc:
        return doc
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d


# ---------- Routes ----------
@app.get("/")
def root():
    return {"message": "Tidya API is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


# Deck endpoints
@app.post("/api/decks")
def create_deck(req: CreateDeckRequest):
    from schemas import Deck
    deck = Deck(**req.model_dump())
    deck_id = create_document("deck", deck)
    return {"id": deck_id}

@app.get("/api/decks")
def list_decks():
    docs = get_documents("deck")
    return [as_str_id(d) for d in docs]


# Item endpoints
@app.post("/api/items")
def create_item(req: CreateItemRequest):
    from schemas import Item
    # Basic validation for deck id
    try:
        ObjectId(req.deck_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid deck_id")
    item = Item(**req.model_dump())
    item_id = create_document("item", item)
    return {"id": item_id}

@app.get("/api/items")
def list_items(deck_id: Optional[str] = None):
    filt = {"deck_id": deck_id} if deck_id else {}
    docs = get_documents("item", filt)
    return [as_str_id(d) for d in docs]


# Schema endpoint for viewer
@app.get("/schema")
def get_schema():
    try:
        from schemas import get_schema_definitions
        return get_schema_definitions()
    except Exception:
        return {}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
