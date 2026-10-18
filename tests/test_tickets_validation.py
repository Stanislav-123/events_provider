from fastapi.testclient import TestClient

from main import app


def test_create_ticket_invalid_body_returns_400() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/tickets",
            json={
                "event_id": "not-a-uuid",
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "email": "x",
                "seat": "A1",
            },
        )

    assert response.status_code == 400
    assert "detail" in response.json()
