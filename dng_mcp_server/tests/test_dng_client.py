import unittest
from unittest.mock import patch, MagicMock
import requests.exceptions

# Assuming the dng_mcp_server directory is in the PYTHONPATH
# If not, this might need adjustment (e.g., sys.path.append)
from app.dng_client import DNGClient, DNGError, DNGAuthenticationError, DNGNotFoundError, DNGAPIError

class TestDNGClient(unittest.TestCase):
    def setUp(self):
        self.client = DNGClient("http://fake-dng.com/rm", "user", "pass")

    def test_init_session_setup(self):
        self.assertIsNotNone(self.client.session)
        self.assertEqual(self.client.session.auth, ("user", "pass"))
        self.assertIn("Accept", self.client.session.headers)
        self.assertEqual(self.client.session.headers["Accept"], "application/json")
        self.assertIn("OSLC-Core-Version", self.client.session.headers)
        self.assertEqual(self.client.session.headers["OSLC-Core-Version"], "2.0")

    @patch.object(DNGClient, 'session', new_callable=MagicMock)
    def test_get_project_areas_success(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"project_areas": [{"id": "pa1", "name": "Project Alpha"}]}
        mock_session.get.return_value = mock_response

        result = self.client.get_project_areas()
        self.assertEqual(result, [{"id": "pa1", "name": "Project Alpha"}])
        mock_session.get.assert_called_once_with(f"{self.client.base_url}/publish/project_areas")

    @patch.object(DNGClient, 'session', new_callable=MagicMock)
    def test_get_project_areas_success_different_key(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"id": "pa2", "name": "Project Beta"}]}
        mock_session.get.return_value = mock_response

        result = self.client.get_project_areas()
        self.assertEqual(result, [{"id": "pa2", "name": "Project Beta"}])

    @patch.object(DNGClient, 'session', new_callable=MagicMock)
    def test_get_project_areas_empty(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"project_areas": []}
        mock_session.get.return_value = mock_response

        result = self.client.get_project_areas()
        self.assertEqual(result, [])

    @patch.object(DNGClient, 'session', new_callable=MagicMock)
    def test_get_project_areas_auth_error(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        # Mock raise_for_status to raise an HTTPError like requests would
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_session.get.return_value = mock_response
        
        with self.assertRaises(DNGAuthenticationError):
            self.client.get_project_areas()

    @patch.object(DNGClient, 'session', new_callable=MagicMock)
    def test_get_project_areas_not_found_error(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_session.get.return_value = mock_response

        with self.assertRaises(DNGNotFoundError):
            self.client.get_project_areas()

    @patch.object(DNGClient, 'session', new_callable=MagicMock)
    def test_get_project_areas_api_error(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_session.get.return_value = mock_response

        with self.assertRaises(DNGAPIError):
            self.client.get_project_areas()

    @patch.object(DNGClient, 'session', new_callable=MagicMock)
    def test_get_project_areas_request_exception(self, mock_session):
        mock_session.get.side_effect = requests.exceptions.RequestException("Connection error")

        with self.assertRaises(DNGAPIError):
            self.client.get_project_areas()

    # Tests for get_requirement_details
    @patch.object(DNGClient, 'session', new_callable=MagicMock)
    def test_get_requirement_details_success(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "req1", "title": "Detail"}
        mock_session.get.return_value = mock_response

        result = self.client.get_requirement_details("req1")
        self.assertEqual(result, {"id": "req1", "title": "Detail"})
        mock_session.get.assert_called_once_with(f"{self.client.base_url}/publish/requirements/req1")

    @patch.object(DNGClient, 'session', new_callable=MagicMock)
    def test_get_requirement_details_auth_error(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_session.get.return_value = mock_response
        with self.assertRaises(DNGAuthenticationError):
            self.client.get_requirement_details("req1")

    @patch.object(DNGClient, 'session', new_callable=MagicMock)
    def test_get_requirement_details_not_found_error(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_session.get.return_value = mock_response
        with self.assertRaises(DNGNotFoundError):
            self.client.get_requirement_details("req1")

    @patch.object(DNGClient, 'session', new_callable=MagicMock)
    def test_get_requirement_details_api_error(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_session.get.return_value = mock_response
        with self.assertRaises(DNGAPIError):
            self.client.get_requirement_details("req1")

    @patch.object(DNGClient, 'session', new_callable=MagicMock)
    def test_get_requirement_details_request_exception(self, mock_session):
        mock_session.get.side_effect = requests.exceptions.RequestException("Connection error")
        with self.assertRaises(DNGAPIError):
            self.client.get_requirement_details("req1")

    # Tests for get_requirements (Simplified)
    @patch.object(DNGClient, 'session', new_callable=MagicMock)
    def test_get_requirements_success_no_pagination(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"requirements": [{"id": "r1", "title": "Req 1"}]}
        # Simulate no next page: no 'nextPageUrl' in JSON, no 'Link' header, and items < page_size
        mock_response.headers = {} 
        mock_session.get.return_value = mock_response

        result = self.client.get_requirements("p1", page_size=10) # page_size > items returned
        self.assertEqual(result, [{"id": "r1", "title": "Req 1"}])
        mock_session.get.assert_called_once_with(f"{self.client.base_url}/publish/projects/p1/requirements?pageSize=10")

    @patch.object(DNGClient, 'session', new_callable=MagicMock)
    def test_get_requirements_auth_error(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_session.get.return_value = mock_response
        with self.assertRaises(DNGAuthenticationError):
            self.client.get_requirements("p1")

    @patch.object(DNGClient, 'session', new_callable=MagicMock)
    def test_get_requirements_not_found_error(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_session.get.return_value = mock_response
        with self.assertRaises(DNGNotFoundError):
            self.client.get_requirements("p1")

    @patch.object(DNGClient, 'session', new_callable=MagicMock)
    def test_get_requirements_api_error(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_session.get.return_value = mock_response
        with self.assertRaises(DNGAPIError):
            self.client.get_requirements("p1")

    @patch.object(DNGClient, 'session', new_callable=MagicMock)
    def test_get_requirements_request_exception(self, mock_session):
        mock_session.get.side_effect = requests.exceptions.RequestException("Connection error")
        with self.assertRaises(DNGAPIError):
            self.client.get_requirements("p1")
            
    # Tests for get_requirement_traceability (Simplified)
    @patch.object(DNGClient, 'session', new_callable=MagicMock) # For fallback call
    @patch.object(DNGClient, 'get_requirement_details')
    def test_get_requirement_traceability_links_in_details(self, mock_get_details, mock_session):
        mock_get_details.return_value = {"id": "r1", "oslc:links": [{"uri": "link1"}]}
        
        result = self.client.get_requirement_traceability("r1")
        self.assertEqual(result, {"oslc:links": [{"uri": "link1"}]})
        mock_get_details.assert_called_once_with("r1")
        mock_session.get.assert_not_called() # Fallback should not be called

    @patch.object(DNGClient, 'session', new_callable=MagicMock) # For fallback call
    @patch.object(DNGClient, 'get_requirement_details')
    def test_get_requirement_traceability_no_links_in_details_fallback_404(self, mock_get_details, mock_session):
        mock_get_details.return_value = {"id": "r1"} # No direct links
        
        mock_fallback_response = MagicMock()
        mock_fallback_response.status_code = 404
        mock_fallback_response.text = "Not Found"
        mock_fallback_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_fallback_response)
        mock_session.get.return_value = mock_fallback_response
        
        result = self.client.get_requirement_traceability("r1")
        self.assertEqual(result, [])
        mock_get_details.assert_called_once_with("r1")
        mock_session.get.assert_called_once_with(f"{self.client.base_url}/publish/requirements/r1/links")

    @patch.object(DNGClient, 'session', new_callable=MagicMock) # Not strictly needed here but good for consistency
    @patch.object(DNGClient, 'get_requirement_details')
    def test_get_requirement_traceability_details_not_found(self, mock_get_details, mock_session):
        mock_get_details.side_effect = DNGNotFoundError("Details not found")
        
        with self.assertRaises(DNGNotFoundError):
            self.client.get_requirement_traceability("r1")
        mock_get_details.assert_called_once_with("r1")
        mock_session.get.assert_not_called() # Fallback should not be attempted if details fail

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    # To run from command line:
    # Ensure dng_mcp_server parent directory is in PYTHONPATH
    # python -m unittest dng_mcp_server.tests.test_dng_client
