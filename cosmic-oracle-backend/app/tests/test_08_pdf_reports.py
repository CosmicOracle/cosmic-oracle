# app/tests/test_08_pdf_reports.py
import pytest
import allure
import time
import json # Used for allure.attach, response.json is preferred for data

# IMPORTANT: Do NOT import 'fastapi.testclient.TestClient'. Your project uses Flask.
# The 'client' fixture from conftest.py will provide the correct Flask test client.
# No need to import 'app.main' directly here, as 'client' fixture handles app setup.

@allure.epic("Report Generation")
@allure.feature("Asynchronous PDF Creation")
class TestReportGeneration:
    """Test cases for the Report Generation API endpoints."""

    @allure.story("Request and Download Year Ahead Report")
    @allure.title("Test the full asynchronous flow for a Year Ahead Report")
    @allure.description("This test simulates requesting a year-ahead report, polling for its status, and attempting to download the completed PDF, verifying the API's asynchronous behavior.")
    def test_year_ahead_report_flow(self, client):
        report_id = None
        with allure.step("1. Request a new 'Year Ahead' report"):
            test_data = {
                "natal_data": {
                    "full_name": "Test User for Report",
                    "datetime_str": "1990-01-01T12:00:00",
                    "timezone_str": "UTC",
                    "latitude": 0.0,
                    "longitude": 0.0,
                    "house_system": "Placidus"
                }
            }
            # Use json=test_data for Flask test clients
            response = client.post("/api/v1/reports/year-ahead", json=test_data)
            
            assert response.status_code == 202, f"Expected status code 202, got {response.status_code}" # 202 Accepted means background task started
            data = response.json
            assert "report_id" in data, "Response missing 'report_id'"
            report_id = data["report_id"]
            allure.attach(f"Report ID: {report_id}", name="Obtained Report ID")

        with allure.step("2. Poll for report status until 'completed'"):
            max_retries = 10
            poll_interval_seconds = 2 # Wait 2 seconds between polls
            for i in range(max_retries):
                time.sleep(poll_interval_seconds) # Wait for the background task to work
                response = client.get(f"/api/v1/reports/{report_id}/status")
                assert response.status_code == 200, f"Expected status code 200, got {response.status_code} during polling"
                status_data = response.json
                allure.attach(f"Poll {i+1}: {status_data}", name=f"Status Poll {i+1}", attachment_type=allure.attachment_type.JSON)

                if status_data.get("status") == "completed":
                    allure.attach(json.dumps(status_data, indent=2), name="Final Status Response", attachment_type=allure.attachment_type.JSON)
                    assert "download_url" in status_data, "Completed status missing 'download_url'"
                    break # Exit loop if completed
                elif status_data.get("status") == "failed":
                    pytest.fail(f"Report generation failed: {status_data.get('error_message', 'No error message provided')}")
                elif status_data.get("status") == "processing":
                    # Continue polling
                    pass
                else:
                    pytest.fail(f"Unexpected report status: {status_data.get('status')}")
            else: # This else block runs if the loop completes without a 'break'
                pytest.fail(f"Report generation timed out (did not complete in {max_retries * poll_interval_seconds} seconds). Last status: {status_data.get('status')}")
        
        with allure.step("3. Attempt to download the completed report"):
            # The Flask TestClient returns the response directly, including file content and headers.
            download_response = client.get(f"/api/v1/reports/{report_id}/download")
            assert download_response.status_code == 200, f"Expected status code 200 for download, got {download_response.status_code}"
            assert "application/pdf" in download_response.headers['Content-Type'], "Content-Type header mismatch (expected PDF)"
            # Check for a reasonable file size. PDF files are usually more than a few bytes.
            assert int(download_response.headers['Content-Length']) > 100, "Downloaded PDF is too small (possibly empty)"
            # Optional: Save the PDF content if you want to inspect it during debugging
            # with open(f"test_report_{report_id}.pdf", "wb") as f:
            #     f.write(download_response.data)