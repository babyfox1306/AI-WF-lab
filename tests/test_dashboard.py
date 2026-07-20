"""Tests for the Dashboard module."""


class TestDashboard:
    def test_dashboard_empty(self, registered_client):
        """Should return zero counts for a new user."""
        response = registered_client.get("/dashboard/")
        assert response.status_code == 200
        data = response.json()
        assert data["total_workflows"] == 0
        assert data["running_jobs"] == 0
        assert data["completed_jobs"] == 0
        assert data["failed_jobs"] == 0
        assert data["recent_activity"] == []

    def test_dashboard_with_data(self, registered_client):
        """Should return correct counts after creating workflows and jobs."""
        # Create workspace
        ws_resp = registered_client.post("/workspaces/", json={"name": "My WS"})
        ws_id = ws_resp.json()["id"]

        # Create workflow
        wf_resp = registered_client.post(
            f"/workspaces/{ws_id}/workflows/",
            json={"name": "My WF", "description": "Test"},
        )
        wf_id = wf_resp.json()["id"]

        # Create and execute a job
        job_resp = registered_client.post(
            f"/workflows/{wf_id}/jobs/",
            json={"name": "Job 1", "input_data": {"x": 1}},
        )
        job_id = job_resp.json()["id"]
        registered_client.post(f"/workflows/{wf_id}/jobs/{job_id}/execute")

        # Check dashboard
        response = registered_client.get("/dashboard/")
        assert response.status_code == 200
        data = response.json()
        assert data["total_workflows"] == 1
        assert data["running_jobs"] == 0  # Job already finished
        assert data["completed_jobs"] + data["failed_jobs"] == 1  # Either completed or failed
        assert len(data["recent_activity"]) > 0

        # Recent activity entries have required fields
        for entry in data["recent_activity"]:
            assert "id" in entry
            assert "level" in entry
            assert "message" in entry

    def test_dashboard_isolated(self, registered_client, client, test_user_data):
        """Dashboard should only show data for the authenticated user."""
        # First user creates data
        ws_resp = registered_client.post("/workspaces/", json={"name": "User1 WS"})
        ws_id = ws_resp.json()["id"]
        wf_resp = registered_client.post(
            f"/workspaces/{ws_id}/workflows/", json={"name": "User1 WF"}
        )
        wf_id = wf_resp.json()["id"]

        # Second user registers and checks dashboard
        client.post("/auth/register", json={
            "email": "user2@example.com",
            "username": "user2",
            "password": "pass123",
        })
        login_resp = client.post("/auth/login", json={
            "email": "user2@example.com",
            "password": "pass123",
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/dashboard/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_workflows"] == 0  # User2 has no workflows
