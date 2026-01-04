from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

# --- ALGORITM ---
TARGET_INVENTORY = 15
CORRECTION_FACTOR = 0.6


def calculate_order(role: str, weeks: List[Dict]) -> int:
    if not weeks: return 4

    last_week = weeks[-1]
    role_data = last_week["roles"][role]

    inventory = role_data["inventory"]
    backlog = role_data["backlog"]
    incoming = role_data["incoming_orders"]

    # Lihtne oodatava nõudluse arvutus (viimase 3 nädala keskmine)
    relevant_weeks = weeks[-3:]
    avg_demand = sum(w["roles"][role]["incoming_orders"] for w in relevant_weeks) / len(relevant_weeks)

    net_inventory = inventory - backlog
    order = avg_demand + (TARGET_INVENTORY - net_inventory) * CORRECTION_FACTOR

    return max(0, int(round(order)))


# --- ENDPOINTID ---

@app.get("/")
def root():
    return {"status": "BeerBot is running"}


@app.post("/api/decision")
async def decision(request: Request):
    data = await request.json()

    # 1. Handshake
    if data.get("handshake") is True:
        return {
            "ok": True,
            "student_email": "madjar@taltech.ee",
            "algorithm_name": "VercelBeerBot",
            "version": "v1.2",
            "supports": {"blackbox": True, "glassbox": True},
            "message": "BeerBot ready"
        }

    # 2. Simulation Step
    weeks = data.get("weeks", [])

    orders = {
        "retailer": calculate_order("retailer", weeks),
        "wholesaler": calculate_order("wholesaler", weeks),
        "distributor": calculate_order("distributor", weeks),
        "factory": calculate_order("factory", weeks)
    }

    return {"orders": orders}
