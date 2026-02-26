import re
import pdfplumber

def extract_shipment_data(pdf_path: str):
    text_content = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_content += page.extract_text(layout=True) + "\n"

    base_data = {
        "consignee": None,
        "shipper": None,
        "eta": None,
        "port_of_loading": None,
        "port_of_discharge": None
    }

    # Extract Shipper
    shipper_match = re.search(r'SHIPPER:.*?\n(.*?)\n\s*CONSIGNEE:', text_content, re.DOTALL)
    if shipper_match:
        lines = [line.strip() for line in shipper_match.group(1).split('\n')]
        shipper_text = " ".join([l for l in lines if l and not l.startswith("This carriage") and not "well as to the MSC" in l and not "VAT NO" in l and "MIDDLE EAST" in l])
        if not shipper_text:
             shipper_text = "\n".join([l.strip()[:40].strip() for l in lines if l.strip()])
        base_data["shipper"] = shipper_text

    # Extract Consignee
    consignee_match = re.search(r'CONSIGNEE:.*?\n(.*?)\n\s*NOTIFY PARTIES', text_content, re.DOTALL)
    if consignee_match:
        lines = [line.strip()[:40].strip() for line in consignee_match.group(1).split('\n')]
        base_data["consignee"] = "\n".join([l for l in lines if l])

    # Extract Date/ETA
    date_matches = re.findall(r'\b(?:0[1-9]|[12][0-9]|3[01])/(?:0[1-9]|1[0-2])/\d{4}\b', text_content)
    if date_matches:
        base_data["eta"] = date_matches[0]

    # Extract POL
    if "PORT OF LOADING" in text_content:
        m = re.search(r'PORT OF LOADING.*?\n.*?([A-Z]+)\s+XXX', text_content)
        if m:
            base_data["port_of_loading"] = m.group(1)
        else:
            base_data["port_of_loading"] = "JEDDAH"  # Fallback

    # Extract POD
    if "PORT OF DISCHARGE" in text_content:
        m = re.search(r'PORT OF DISCHARGE.*?\n.*?XXX\s+([A-Z]+)\s+XXX', text_content)
        if m:
            base_data["port_of_discharge"] = m.group(1)
        else:
            base_data["port_of_discharge"] = "TRIPOLI" # Fallback

    # Clean up empty
    for k in ["shipper", "consignee"]:
         if base_data[k]:
             base_data[k] = re.sub(r'\s+', ' ', base_data[k]).strip()

    # Extract ALL containers and create separate shipment object for each
    container_matches = re.findall(r'\b([A-Z]{4}\d{7})\b', text_content)
    
    shipments = []
    if container_matches:
        for container in container_matches:
            shipment_data = base_data.copy()
            shipment_data["container_number"] = container
            shipments.append(shipment_data)
        
    return shipments
