"""Health endpoint and basic sanity test."""

import unittest
import asyncio

try:
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False


class TestHealth(unittest.TestCase):
    def test_health_endpoint(self):
        if not HAS_DEPS:
            self.skipTest("FastAPI / httpx dependencies not installed in host global python; runs in venv/Docker.")

        async def _run():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/health")
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["status"], "healthy")
                self.assertIn("version", data)

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
