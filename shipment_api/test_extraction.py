import asyncio
from httpx import AsyncClient, ASGITransport
from main import app

async def test_upload():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        with open(r"d:\Glit\BL COPY.PDF", "rb") as f:
            response = await ac.post("/shipment/upload/", files={"file": ("BL COPY.PDF", f, "application/pdf")})
        print("Upload Response:", response.status_code)
        print(response.json())
        
        if response.status_code == 200:
            data = response.json()
            for item in data:
                container = item.get("container_number")
                if container:
                    get_resp = await ac.get(f"/shipment/{container}")
                    print(f"Get Response for {container}:", get_resp.status_code)
                    print(get_resp.json())

if __name__ == "__main__":
    asyncio.run(test_upload())
