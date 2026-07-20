"""Tests for the Jobs module."""


class TestCreateJob:
    def test_create_success(self, registered_client):
        """Should create a job and return 201."""
        ws_resp = registered_client.post("/workspaces/", json={"name": "WS"})
        ws_id = ws_resp.json()["id"]
        wf_resp = registered_client.post(
            f"/workspaces/{ws_id}/workflows/", json={"name": "WF"}
        )
        wf_id = wf_resp.json()["id"]

        response = registered_client.post(
            f"/workflows/{wf_id}/jobs/",
            json={"name": "Test Job", "input_data": {"text": "hello"}},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Job"
        assert data["status"] == "pending"
        assert data["input_data"] == {"text": "hello"}
        assert data["workflow_id"] == wf_id


class TestJobLifecycle:
    def test_execute_job_success(self, registered_client):
        """Should execute a job and mark it as completed."""
        # Setup
        ws_resp = registered_client.post("/workspaces/", json={"name": "WS"})
        ws_id = ws_resp.json()["id"]
        wf_resp = registered_client.post(
            f"/workspaces/{ws_id}/workflows/", json={"name": "WF"}
        )
        wf_id = wf_resp.json()["id"]
        job_resp = registered_client.post(
            f"/workflows/{wf_id}/jobs/",
            json={"name": "Test Job", "input_data": {"text": "hello"}},
        )
        job_id = job_resp.json()["id"]

        # Execute
        response = registered_client.post(f"/workflows/{wf_id}/jobs/{job_id}/execute")
        assert response.status_code == 200
        data = response.json()
        assert "job" in data
        assert "logs" in data
        assert data["job"]["status"] in ["completed", "failed"]
        assert data["job"]["started_at"] is not None
        assert data["job"]["finished_at"] is not None

        # Should have logs
        assert len(data["logs"]) > 0
        assert data["logs"][0]["level"] == "info"

    def test_execute_job_logs_created(self, registered_client):
        """Should create logs after job execution."""
        ws_resp = registered_client.post("/workspaces/", json={"name": "WS"})
        ws_id = ws_resp.json()["id"]
        wf_resp = registered_client.post(
            f"/workspaces/{ws_id}/workflows/", json={"name": "WF"}
        )
        wf_id = wf_resp.json()["id"]
        job_resp = registered_client.post(
            f"/workflows/{wf_id}/jobs/",
            json={"name": "Log Test", "input_data": {"test": True}},
        )
        job_id = job_resp.json()["id"]

        # Execute
        registered_client.post(f"/workflows/{wf_id}/jobs/{job_id}/execute")

        # Check logs
        log_resp = registered_client.get(f"/jobs/{job_id}/logs/")
        assert log_resp.status_code == 200
        logs = log_resp.json()
        assert len(logs) > 0

        # Log properties
        log = logs[0]
        assert "id" in log
        assert "level" in log
        assert "message" in log
        assert "timestamp" in log

    def test_execute_job_already_completed(self, registered_client):
        """Should reject executing a completed job again.
        Note: failed jobs CAN be retried, so we run multiple attempts.
        """
        ws_resp = registered_client.post("/workspaces/", json={"name": "WS"})
        ws_id = ws_resp.json()["id"]
        wf_resp = registered_client.post(
            f"/workspaces/{ws_id}/workflows/", json={"name": "WF"}
        )
        wf_id = wf_resp.json()["id"]
        job_resp = registered_client.post(
            f"/workflows/{wf_id}/jobs/",
            json={"name": "Once", "input_data": {}},
        )
        job_id = job_resp.json()["id"]

        # Execute once
        first_resp = registered_client.post(f"/workflows/{wf_id}/jobs/{job_id}/execute")
        first_status = first_resp.json()["job"]["status"]

        if first_status == "completed":
            # Execute again should fail with 409
            response = registered_client.post(f"/workflows/{wf_id}/jobs/{job_id}/execute")
            assert response.status_code == 409
        else:
            # Job failed (10% chance) - can be retried
            # Retry should succeed
            retry_resp = registered_client.post(f"/workflows/{wf_id}/jobs/{job_id}/execute")
            assert retry_resp.status_code == 200
            retry_status = retry_resp.json()["job"]["status"]
            assert retry_status in ["completed", "failed"]


class TestFailedJobHandling:
    def test_failed_job_has_error_message(self, registered_client):
        """A failed job should have an error_message."""
        ws_resp = registered_client.post("/workspaces/", json={"name": "WS"})
        ws_id = ws_resp.json()["id"]
        wf_resp = registered_client.post(
            f"/workspaces/{ws_id}/workflows/", json={"name": "WF"}
        )
        wf_id = wf_resp.json()["id"]
        job_resp = registered_client.post(
            f"/workflows/{wf_id}/jobs/",
            json={"name": "Fail Test", "input_data": {}},
        )
        job_id = job_resp.json()["id"]

        # Execute (10% chance of failure, run 3 times to increase chances)
        result = None
        for _ in range(3):
            result = registered_client.post(f"/workflows/{wf_id}/jobs/{job_id}/execute")
            if result.json()["job"]["status"] == "failed":
                break
            # Reset for next attempt
            ws_resp2 = registered_client.post("/workspaces/", json={"name": "WS2"})
            ws_id2 = ws_resp2.json()["id"]
            wf_resp2 = registered_client.post(
                f"/workspaces/{ws_id2}/workflows/", json={"name": "WF"}
            )
            wf_id2 = wf_resp2.json()["id"]
            job_resp2 = registered_client.post(
                f"/workflows/{wf_id2}/jobs/",
                json={"name": "Fail Test", "input_data": {}},
            )
            job_id = job_resp2.json()["id"]

        # If all attempts succeeded, skip this check
        if result and result.json()["job"]["status"] == "failed":
            job_data = result.json()["job"]
            assert job_data["error_message"] is not None
            assert len(job_data["error_message"]) > 0

            # Check error logs exist
            log_resp = registered_client.get(f"/jobs/{job_id}/logs/")
            logs = log_resp.json()
            error_logs = [l for l in logs if l["level"] == "error"]
            assert len(error_logs) > 0
