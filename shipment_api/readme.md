* How to run the application:
  open command prompt and navigate to the project directory
  Create Python virtual environment  : python -m venv venv  
  Activate Python virtual environment : venv\Scripts\activate
  Install dependencies              : pip install fastapi uvicorn sqlalchemy pydantic pdfplumber python-multipart
  Run the FastAPI server            : uvicorn main:app --reload --port 8080
==============================================================================================

* In Browser go to : http://127.0.0.1:8000/

* Upload PDF file to extract shipment data

* API Endpoints:
  POST /shipment/upload/ : Upload a PDF file to extract shipment data
  GET /shipment/{container_number} : Get shipment data by container number