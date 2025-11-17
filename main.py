import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from database import create_document, get_documents
from schemas import Booking as BookingSchema

app = FastAPI(title="SurfAura Beach Club API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BookingIn(BaseModel):
    name: str
    email: str
    phone: str
    package: str
    date: str
    participants: int = Field(1, ge=1, le=20)
    notes: Optional[str] = None

class BookingOut(BookingIn):
    id: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "SurfAura Beach Club API Running"}

@app.get("/api/packages")
def get_packages():
    packages = [
        {
            "id": "starter-surf",
            "title": "Starter Surf",
            "price": 59,
            "duration": "2 hrs",
            "features": ["Beginner-friendly", "Board + wetsuit included", "1:4 coach ratio"],
            "badge": "Popular"
        },
        {
            "id": "wave-master",
            "title": "Wave Master",
            "price": 149,
            "duration": "Full Day",
            "features": ["Intermediate drills", "Video analysis", "Pro equipment"],
            "badge": "Best Value"
        },
        {
            "id": "aura-elite",
            "title": "Aura Elite",
            "price": 299,
            "duration": "Weekend Camp",
            "features": ["Private coaching", "Sunrise yoga", "Beach club access"],
            "badge": "Premium"
        }
    ]
    return {"packages": packages}

@app.get("/api/events")
def get_events():
    events = [
        {"id": "sunrise-yoga", "title": "Sunrise Yoga by the Waves", "date": "2025-12-03", "type": "Wellness", "time": "6:00 AM"},
        {"id": "music-fest", "title": "Sunset Music Fest", "date": "2025-12-10", "type": "Festival", "time": "5:00 PM"},
        {"id": "beach-games", "title": "Beach Games & Surf Jam", "date": "2025-12-14", "type": "Sports", "time": "2:00 PM"},
        {"id": "night-surf", "title": "Full Moon Night Surf", "date": "2025-12-20", "type": "Experience", "time": "8:00 PM"}
    ]
    return {"events": events}

@app.post("/api/bookings")
def create_booking(booking: BookingIn):
    try:
        booking_id = create_document("booking", booking.dict())
        return {"status": "success", "id": booking_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bookings")
def list_bookings(limit: int = 10):
    try:
        docs = get_documents("booking", limit=limit)
        # Convert ObjectId to str if present
        out = []
        for d in docs:
            d["id"] = str(d.get("_id"))
            d.pop("_id", None)
            out.append(d)
        return {"bookings": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
