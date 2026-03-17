"""Tests for auth endpoints."""


def test_register(client):
    response = client.post("/api/auth/register", json={
        "email": "new@lab.com",
        "password": "securepass123",
        "full_name": "New Scientist",
        "organization_name": "New Lab",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client):
    payload = {
        "email": "dupe@lab.com",
        "password": "securepass123",
        "full_name": "Scientist",
        "organization_name": "Lab",
    }
    client.post("/api/auth/register", json=payload)
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409


def test_login(client):
    # Register first
    client.post("/api/auth/register", json={
        "email": "login@lab.com",
        "password": "securepass123",
        "full_name": "Login User",
        "organization_name": "Login Lab",
    })
    # Login
    response = client.post("/api/auth/login", json={
        "email": "login@lab.com",
        "password": "securepass123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "email": "wrong@lab.com",
        "password": "securepass123",
        "full_name": "User",
        "organization_name": "Lab",
    })
    response = client.post("/api/auth/login", json={
        "email": "wrong@lab.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_me(client):
    # Register and get token
    reg = client.post("/api/auth/register", json={
        "email": "me@lab.com",
        "password": "securepass123",
        "full_name": "Me User",
        "organization_name": "Me Lab",
    })
    token = reg.json()["access_token"]
    # Get me
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@lab.com"
    assert data["full_name"] == "Me User"
    assert data["role"] == "admin"


def test_me_no_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
