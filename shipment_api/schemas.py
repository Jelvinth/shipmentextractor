from pydantic import BaseModel
from typing import Optional

class ShipmentBase(BaseModel):
    container_number: Optional[str] = None
    consignee: Optional[str] = None
    shipper: Optional[str] = None
    eta: Optional[str] = None
    port_of_loading: Optional[str] = None
    port_of_discharge: Optional[str] = None

class ShipmentCreate(ShipmentBase):
    pass

class ShipmentResponse(ShipmentBase):
    id: int

    class Config:
        from_attributes = True
