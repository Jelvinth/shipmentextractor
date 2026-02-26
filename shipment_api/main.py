import os
import shutil
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import database, models, schemas
from extractor import extract_shipment_data

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Shipment Extraction API")

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
def root():
    return FileResponse("static/index.html")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

from typing import List

@app.post("/shipment/upload/", response_model=List[schemas.ShipmentResponse])
def upload_shipment(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # save file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Extract data (returns list of dicts)
        extracted_shipments = extract_shipment_data(temp_path)
        
        if not extracted_shipments:
             # Clean up temp file before raising exception
             if os.path.exists(temp_path):
                 os.remove(temp_path)
             raise HTTPException(status_code=400, detail="No valid container details found in the uploaded PDF. Please upload a relevant Bill of Lading.")

        saved_shipments = []
        for data in extracted_shipments:
            # Check if exists
            db_shipment = db.query(models.Shipment).filter(models.Shipment.container_number == data["container_number"]).first()
            if db_shipment:
                for k, v in data.items():
                    setattr(db_shipment, k, v)
            else:
                db_shipment = models.Shipment(**data)
                db.add(db_shipment)
                 
            db.commit()
            db.refresh(db_shipment)
            saved_shipments.append(db_shipment)
            
        return saved_shipments
    except HTTPException as he:
        # Re-raise HTTP exceptions so they return directly
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/shipment/{container_number}", response_model=schemas.ShipmentResponse)
def get_shipment(container_number: str, db: Session = Depends(get_db)):
    shipment = db.query(models.Shipment).filter(models.Shipment.container_number == container_number).first()
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment
