from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import List, Optional

app = FastAPI()

class StatusEnum(str, Enum):
    masuk = "masuk"
    keluar = "keluar"


class Item(BaseModel):
    name: str  
    email: str
    createdAt: datetime = datetime.now().timestamp()  
    createdTime: datetime
    location: str  
    status: StatusEnum  

    def __init__(self, **data):
        data['createdAt'] = datetime.now().timestamp()
        super().__init__(**data)

class ItemInDB(Item):
    id: int

items = []

def generate_unique_id():
    return len(items) + 1

@app.get("/presensi", response_model=dict)
async def read_items(email: Optional[str] = Query(None)):
    try:
        if email is None:
            filtered_items = items
        else:
            filtered_items = [item for item in items if item.email == email]
        metadata = {"status": "success"}
        if filtered_items:
            data = filtered_items
        else:
            metadata = {"status": "empty", "message": "No items available"}
            data = []

        return {"metadata": metadata, "data": data}
    except Exception as e:
        metadata = {"status": "error", "message": str(e)}
        return {"metadata": metadata}

@app.get("/presensi", response_model=dict)
async def read_items_today(search_date: str):
    try:
        today = datetime.fromisoformat(search_date)
        filtered_items = [item for item in items if item.createdAt.date() == today.date()]
        metadata = {"status": "success"}
        if filtered_items:
            data = filtered_items
        else:
            metadata = {"status": "empty", "message": "No items available"}
            data = []
        return {"metadata": metadata, "data": data}
    except Exception as e:
        metadata = {"status": "error", "message": str(e)}
        return {"metadata": metadata}

@app.post("/presensi", response_model=dict)
async def create_item(item: Item):  
    try:
        # today = datetime.today()
        # absen_today_masuk = any(i for i in items if i.name == item.name and i.createdAt.date() == today and i.status == StatusEnum.masuk)
        # absen_today_keluar = any(i for i in items if i.name == item.name and i.createdAt.date() == today and i.status == StatusEnum.keluar)

        # if item.status == StatusEnum.masuk:
        #     if absen_today_masuk or absen_today_keluar:
        #         return {"metadata": {"status": "error", "message": "Sudah absen hari ini"}}
        # elif item.status == StatusEnum.keluar:
        #     if not absen_today_masuk or absen_today_keluar:
        #         return {"metadata": {"status": "error", "message": "Belum absen masuk hari ini atau sudah absen keluar hari ini"}}

        unique_id = generate_unique_id()
        item_in_db = ItemInDB(**item.dict(), id=unique_id)
        items.append(item_in_db)
        metadata = {"status": "success"}
        return {"metadata": metadata, "data": item_in_db}
    except Exception as e:
        metadata = {"status": "error", "message": str(e)}
        return {"metadata": metadata}

@app.put("/presensi/{item_id}", response_model=dict)
async def update_item(item_id: int, item: Item):
    try:
        item_to_update = next((item_in_db for item_in_db in items if item_in_db.id == item_id), None)
        if item_to_update is None:
            raise HTTPException(status_code=404, detail="Item not found")
        item_data = item.dict()
        update_data = item_to_update.dict()
        update_data.update(item_data)
        updated_item = ItemInDB(**update_data)
        items[item_id - 1] = updated_item
        metadata = {"status": "success"}
        return {"metadata": metadata, "data": updated_item}
    except HTTPException as e:
        metadata = {"status": "error", "message": str(e.detail)}
        return {"metadata": metadata}
    except Exception as e:
        metadata = {"status": "error", "message": str(e)}
        return {"metadata": metadata}

@app.delete("/presensi/{item_id}", response_model=dict)
async def delete_item(item_id: int):
    try:
        item_to_delete = next((item_in_db for item_in_db in items if item_in_db.id == item_id), None)
        if item_to_delete is None:
            raise HTTPException(status_code=404, detail="Item not found")
        items.remove(item_to_delete)
        metadata = {"status": "success", "message": "Item deleted"}
        return {"metadata": metadata}
    except HTTPException as e:
        metadata = {"status": "error", "message": str(e.detail)}
        return {"metadata": metadata}
    except Exception as e:
        metadata = {"status": "error", "message": str(e)}
        return {"metadata": metadata}
