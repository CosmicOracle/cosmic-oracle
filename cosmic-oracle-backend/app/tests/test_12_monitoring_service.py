# app/tests/test_12_monitoring_service.py
import pytest
import allure
import json # Used for allure.attach, response.json is preferred for data

# IMPORTANT: Do NOT import 'fastapi.testclient.TestClient'. Your project uses Flask.
# The 'client' fixture from conftest.py will provide the correct Flask test client.
# No need to import 'app.main' directly here, as 'client' fixture handles app setup.

@allure.epic("Administration")
@allure.feature("Monitoring Dashboard")
class TestMonitoringService:
    """Test cases for the Monitoring API endpoints."""

    @allure.story("Fetch Dashboard Metrics")
    @allure.title("Test the main metrics endpoint")
    @allure.description("This test verifies that the monitoring metrics API successfully returns key performance indicators and system health metrics.")
    def test_get_dashboard_metrics(self, client):
        with allure.step("Make GET request to the metrics endpoint"):
            # In a real test, you would first seed the database with mock subscription data
            # and other operational data for the metrics to reflect.
            # Assuming `/api/v1/admin/monitoring/metrics` is your endpoint
            response = client.get("/api/v1/admin/monitoring/metrics?days=30")

        with allure.step("Verify the structure of the metrics response"):
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            data = response.json
            allure.attach(
                json.dumps(data, indent=2),
                name="Metrics Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert "current_status" in data, "Response missing 'current_status'"
            assert "performance_metrics" in data, "Response missing 'performance_metrics'"
            assert "payment_health" in data, "Response missing 'payment_health'"
            assert "active_users" in data["current_status"], "Current status missing 'active_users'"
            assert "cpu_usage_percent" in data["performance_metrics"], "Performance metrics missing 'cpu_usage_percent'"
            assert "churn_rate_percent" in data["performance_metrics"], "Performance metrics missing 'churn_rate_percent'"
            assert "successful_payments_count" in data["payment_health"], "Payment health missing 'successful_payments_count'"

    @allure.story("Fetch System Alerts")
    @allure.title("Test the system health alerts endpoint")
    @allure.description("This test verifies that the system alerts API returns a list of active system health alerts.")
    def test_get_system_alerts(self, client):
        with allure.step("Make GET request to the alerts endpoint"):
            # This test would be more powerful if you could seed data that
            # specifically triggers an alert (e.g., create many failed payments or errors).
            # Assuming `/api/v1/admin/monitoring/alerts` is your endpoint
            response = client.get("/api/v1/admin/monitoring/alerts")

        with allure.step("Verify the structure of the alerts response"):
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            data = response.json
            allure.attach(
                json.dumps(data, indent=2),
                name="Alerts Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert "alerts" in data, "Response missing 'alerts'"
            assert "total_alerts" in data, "Response missing 'total_alerts'"
            assert isinstance(data["alerts"], list), "'alerts' should be a list"
            assert isinstance(data["total_alerts"], int), "'total_alerts' should be an integer"
            # If you expect no alerts by default, assert data["total_alerts"] == 0

    @allure.story("Invalid Days Parameter")
    @allure.title("Test Metrics endpoint with Invalid Days Parameter")
    @allure.description("This test ensures that providing an invalid 'days' parameter (e.g., negative) to the metrics endpoint results in a 400 Bad Request.")
    def test_get_dashboard_metrics_invalid_days(self, client):
        with allure.step("Make GET request with invalid 'days' parameter"):
            response = client.get("/api/v1/admin/monitoring/metrics?days=-10")
        
        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data
            assert "Days parameter must be a positive integer" in data["error"] or "invalid parameter" in data["error"]