"""Tests for the Workspaces module."""


class TestCreateWorkspace:
    def test_create_success(self, registered_client):
        """Should create a workspace and return 201."""
        response = registered_client.post("/workspaces/", json={"name": "My Workspace"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Workspace"
        assert "id" in data
        assert "owner_id" in data

    def test_create_empty_name(self, registered_client):
        """Should reject workspace with empty name."""
        response = registered_client.post("/workspaces/", json={"name": ""})
        assert response.status_code == 422

    def test_create_unauthorized(self, client):
        """Should return 401 without auth."""
        response = client.post("/workspaces/", json={"name": "My Workspace"})
        assert response.status_code == 401


class TestListWorkspaces:
    def test_list_empty(self, registered_client):
        """Should return empty list when no workspaces."""
        response = registered_client.get("/workspaces/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_multiple(self, registered_client):
        """Should return all user's workspaces."""
        registered_client.post("/workspaces/", json={"name": "Workspace A"})
        registered_client.post("/workspaces/", json={"name": "Workspace B"})
        response = registered_client.get("/workspaces/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestGetWorkspace:
    def test_get_by_id(self, registered_client):
        """Should return the correct workspace."""
        create_resp = registered_client.post("/workspaces/", json={"name": "My WS"})
        ws_id = create_resp.json()["id"]

        response = registered_client.get(f"/workspaces/{ws_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "My WS"

    def test_get_not_found(self, registered_client):
        """Should return 404 for non-existent workspace."""
        response = registered_client.get("/workspaces/9999")
        assert response.status_code == 404


class TestUpdateWorkspace:
    def test_update_name(self, registered_client):
        """Should update workspace name."""
        create_resp = registered_client.post("/workspaces/", json={"name": "Old Name"})
        ws_id = create_resp.json()["id"]

        response = registered_client.patch(f"/workspaces/{ws_id}", json={"name": "New Name"})
        assert response.status_code == 200
        assert response.json()["name"] == "New Name"


class TestDeleteWorkspace:
    def test_delete_success(self, registered_client):
        """Should delete workspace and return 204."""
        create_resp = registered_client.post("/workspaces/", json={"name": "To Delete"})
        ws_id = create_resp.json()["id"]

        response = registered_client.delete(f"/workspaces/{ws_id}")
        assert response.status_code == 204

        # Verify it's gone
        get_resp = registered_client.get(f"/workspaces/{ws_id}")
        assert get_resp.status_code == 404

    def test_delete_not_found(self, registered_client):
        """Should return 404 when deleting non-existent workspace."""
        response = registered_client.delete("/workspaces/9999")
        assert response.status_code == 404
