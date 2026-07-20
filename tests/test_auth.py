"""Tests for the Auth module."""

import pytest


class TestUserRegistration:
    def test_register_success(self, client):
        """Should register a user and return 201."""
        response = client.post("/auth/register", json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securepass123",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["is_active"] is True
        assert "id" in data
        assert "password" not in data

    def test_register_duplicate_email(self, client, test_user_data):
        """Should reject duplicate email registration."""
        client.post("/auth/register", json=test_user_data)
        response = client.post("/auth/register", json=test_user_data)
        assert response.status_code == 409
        assert "Email already registered" in response.json()["detail"]

    def test_register_duplicate_username(self, client):
        """Should reject duplicate username."""
        client.post("/auth/register", json={
            "email": "user1@example.com",
            "username": "sameuser",
            "password": "pass123",
        })
        response = client.post("/auth/register", json={
            "email": "user2@example.com",
            "username": "sameuser",
            "password": "pass456",
        })
        assert response.status_code == 409
        assert "Username already taken" in response.json()["detail"]

    def test_register_short_password(self, client):
        """Should reject passwords shorter than 6 characters."""
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "12345",
        })
        assert response.status_code == 422


class TestUserLogin:
    def test_login_success(self, client, test_user_data):
        """Should login and return a JWT token."""
        client.post("/auth/register", json=test_user_data)
        response = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user_data):
        """Should reject wrong password."""
        client.post("/auth/register", json=test_user_data)
        response = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Should reject login for non-existent user."""
        response = client.post("/auth/login", json={
            "email": "nobody@example.com",
            "password": "somepassword",
        })
        assert response.status_code == 401


class TestUserProfile:
    def test_get_profile(self, client, test_user_data):
        """Should return the authenticated user's profile."""
        # Register and login
        client.post("/auth/register", json=test_user_data)
        login_resp = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        })
        token = login_resp.json()["access_token"]

        response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]

    def test_get_profile_unauthorized(self, client):
        """Should return 401 without a valid token."""
        response = client.get("/users/me")
        assert response.status_code == 401

    def test_update_profile(self, client, test_user_data):
        """Should update the user's profile."""
        client.post("/auth/register", json=test_user_data)
        login_resp = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.patch("/users/me", json={"username": "updateduser"}, headers=headers)
        assert response.status_code == 200
        assert response.json()["username"] == "updateduser"
