from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime, date

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

    @field_validator('eta', mode='after')
    @classmethod
    def check_eta(cls, v: Optional[str]) -> Optional[str]:
        if v and v != "Delayed":
            try:
                eta_date = datetime.strptime(v, "%d/%m/%Y").date()
                if eta_date < date.today():
                    return "Delayed"
            except ValueError:
                pass
        return v

    class Config:
        from_attributes = True
