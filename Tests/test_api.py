from fastapi.testclient import TestClient
from app import app  # your FastAPI app

client = TestClient(app)

def test_status():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_evaluate():
    payload = {
        "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
        "move": "f1c4"
    }
    response = client.post("/evaluate", json=payload)
    assert response.status_code == 200
    assert "blunder" in response.json()

if __name__ == "--main__":
    test_status()
    test_evaluate()
    print("All tests passed!")
    