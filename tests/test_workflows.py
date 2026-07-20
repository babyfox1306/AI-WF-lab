"""Tests for the Workflows module."""


class TestCreateWorkflow:
    def test_create_success(self, registered_client):
        """Should create a workflow and return 201."""
        ws_resp = registered_client.post("/workspaces/", json={"name": "WS"})
        ws_id = ws_resp.json()["id"]

        response = registered_client.post(
            f"/workspaces/{ws_id}/workflows/",
            json={"name": "My Workflow", "description": "A test workflow"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Workflow"
        assert data["description"] == "A test workflow"
        assert data["status"] == "draft"
        assert data["workspace_id"] == ws_id

    def test_create_unauthorized(self, client, db, workspace):
        """Should return 401 without auth."""
        response = client.post(
            f"/workspaces/{workspace.id}/workflows/",
            json={"name": "Test"},
        )
        assert response.status_code == 401


class TestListWorkflows:
    def test_list_empty(self, registered_client):
        """Should return empty list when no workflows."""
        ws_resp = registered_client.post("/workspaces/", json={"name": "WS"})
        ws_id = ws_resp.json()["id"]

        response = registered_client.get(f"/workspaces/{ws_id}/workflows/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_multiple(self, registered_client):
        """Should return all workflows in workspace."""
        ws_resp = registered_client.post("/workspaces/", json={"name": "WS"})
        ws_id = ws_resp.json()["id"]

        registered_client.post(f"/workspaces/{ws_id}/workflows/", json={"name": "WF A"})
        registered_client.post(f"/workspaces/{ws_id}/workflows/", json={"name": "WF B"})
        response = registered_client.get(f"/workspaces/{ws_id}/workflows/")
        assert response.status_code == 200
        assert len(response.json()) == 2


class TestUpdateWorkflow:
    def test_update_status(self, registered_client):
        """Should update workflow status."""
        ws_resp = registered_client.post("/workspaces/", json={"name": "WS"})
        ws_id = ws_resp.json()["id"]
        wf_resp = registered_client.post(
            f"/workspaces/{ws_id}/workflows/", json={"name": "WF"}
        )
        wf_id = wf_resp.json()["id"]

        response = registered_client.patch(
            f"/workspaces/{ws_id}/workflows/{wf_id}",
            json={"status": "running"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "running"


class TestDeleteWorkflow:
    def test_delete_success(self, registered_client):
        """Should delete workflow and return 204."""
        ws_resp = registered_client.post("/workspaces/", json={"name": "WS"})
        ws_id = ws_resp.json()["id"]
        wf_resp = registered_client.post(
            f"/workspaces/{ws_id}/workflows/", json={"name": "WF"}
        )
        wf_id = wf_resp.json()["id"]

        response = registered_client.delete(f"/workspaces/{ws_id}/workflows/{wf_id}")
        assert response.status_code == 204
