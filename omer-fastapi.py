from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from datetime import date, datetime
from astral import LocationInfo
from astral.sun import sun
import pytz

app = FastAPI(
    title="Sonnenuntergang API für OMER ZÄHLER 5785",
    version="3.0.0",
    description="Selbst gehosteter Service zur präzise Berechnung des Sonnenuntergangs (Schkia) für Omer‑Zählung."
)

class SunsetResponse(BaseModel):
    date: date = Field(..., description="Gregorianisches Datum der Berechnung")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: str = Field(..., description="IANA‑Zeitzone, z.B. 'Europe/Brussels'")
    sunset_iso: str = Field(..., description="Sonnenuntergang in ISO‑8601 mit Zeitzone")

@app.get("/sunset", response_model=SunsetResponse, summary="Berechnet den Sonnenuntergang")
async def get_sunset(
    date: date = Query(None, description="YYYY‑MM‑DD. Default: heute"),
    latitude: float = Query(..., description="Breitengrad"),
    longitude: float = Query(..., description="Längengrad"),
    timezone: str = Query("UTC", description="IANA‑Zone")
):
    # 1) Datum default auf heute, wenn nicht übergeben
    if date is None:
        date = datetime.utcnow().date()
    # 2) Prüfen, ob Zone gültig
    try:
        tz = pytz.timezone(timezone)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Unbekannte Zeitzone: {timezone}")
    # 3) Astral‑Berechnung
    loc = LocationInfo(latitude=latitude, longitude=longitude, timezone=timezone)
    s = sun(loc.observer, date=date, tzinfo=tz)
    sunset = s["sunset"]
    return SunsetResponse(
        date=date,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        sunset_iso=sunset.isoformat()
    )
