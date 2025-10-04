

import asyncio
import httpx

API_URL = "http://localhost:8088"


async def test_health():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_URL}/health")
        print("GET /health ->", resp.status_code, resp.json())


async def test_query():
    payload = {
        "lat": -34.905,
        "lon": -56.191,
        "date_iso": "2025-10-05",
        "profile": "default",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_URL}/query", json=payload)
        print("POST /query ->", resp.status_code)
        print(resp.json())


if __name__ == "__main__":
    asyncio.run(test_health())
    asyncio.run(test_query())