import requests

# Error classes
class DNGError(Exception):
    """Base exception for DNG client issues."""
    pass

class DNGAuthenticationError(DNGError):
    """For authentication failures."""
    pass

class DNGNotFoundError(DNGError):
    """For resources not found."""
    pass

class DNGAPIError(DNGError):
    """For general DNG API errors."""
    pass

class DNGClient:
    """
    A client for interacting with the IBM DOORS Next Generation API.
    """
    def __init__(self, base_url, username, api_key):
        """
        Initializes the DNGClient.

        Args:
            base_url (str): The base URL of the DNG server (e.g., "https://your-dng-server.example.com/rm").
            username (str): The username for DNG authentication.
            api_key (str): The API key or password for DNG authentication.
        """
        self.base_url = base_url
        self.username = username
        self.api_key = api_key
        self.session = requests.Session()
        self.session.auth = (self.username, self.api_key)
        self.session.headers.update({
            "Accept": "application/json",
            "OSLC-Core-Version": "2.0"
        })

    def get_project_areas(self):
        """
        Retrieves a list of project areas from the DNG server.

        Assumes the DNG endpoint for listing project areas is `self.base_url + "/publish/project_areas"`.
        The expected response is a JSON object with a key (e.g., "project_areas", "items", "members")
        containing a list of project area objects. Each object in the list should have at least
        an "id" and a "name" (or "title").

        Returns:
            list: A list of project area objects.

        Raises:
            DNGAuthenticationError: If authentication fails (401 or 403).
            DNGNotFoundError: If the project areas endpoint is not found (404).
            DNGAPIError: For other 4xx or 5xx DNG API errors.
        """
        url = f"{self.base_url}/publish/project_areas"
        try:
            response = self.session.get(url)
            response.raise_for_status()  # Raises HTTPError for 4xx/5xx responses

            # Assuming the actual data is nested under a key like "project_areas" or "items"
            # This might need adjustment based on the actual DNG API response structure.
            return response.json().get("project_areas", [])

        except requests.exceptions.HTTPError as e:
            if e.response.status_code in (401, 403):
                raise DNGAuthenticationError(f"Authentication failed for {url}: {e.response.status_code} {e.response.text}")
            elif e.response.status_code == 404:
                raise DNGNotFoundError(f"Project areas endpoint not found at {url}: {e.response.status_code} {e.response.text}")
            else:
                raise DNGAPIError(f"DNG API error for {url}: {e.response.status_code} {e.response.text}")
        except requests.exceptions.RequestException as e:
            # Handle other request-related issues (e.g., network problems)
            raise DNGAPIError(f"Request failed for {url}: {e}")

    def get_requirements(self, project_id, page_size=100, max_pages=None):
        """
        Retrieves requirements for a specific project, handling pagination.

        Assumes the DNG endpoint for requirements is `self.base_url + f"/publish/projects/{project_id}/requirements"`.
        The method expects the DNG API to support pagination using a 'pageSize' query parameter.
        It will look for a 'nextPageUrl' in the response JSON or a 'Link' header with rel="next"
        to fetch subsequent pages. If neither is found, it will increment a 'page' parameter (1-indexed)
        as long as the number of items returned equals `page_size`.

        The expected response is a JSON object with a key (e.g., "requirements", "items", "members")
        containing a list of requirement objects. Each object in the list should have at least
        an "id" and a "title".

        Args:
            project_id (str): The ID of the project to retrieve requirements from.
            page_size (int): The number of requirements to retrieve per page.
            max_pages (int, optional): The maximum number of pages to retrieve.
                                       Defaults to None (all pages).

        Returns:
            list: A list of requirement objects (dictionaries with 'id' and 'title').

        Raises:
            DNGAuthenticationError: If authentication fails (401 or 403).
            DNGNotFoundError: If the project or requirements endpoint is not found (404).
            DNGAPIError: For other 4xx or 5xx DNG API errors or request issues.
        """
        all_requirements = []
        current_page = 1
        next_page_url = f"{self.base_url}/publish/projects/{project_id}/requirements?pageSize={page_size}"

        while next_page_url and (max_pages is None or current_page <= max_pages):
            try:
                response = self.session.get(next_page_url)
                response.raise_for_status()
                data = response.json()

                # Extract requirements - adjust the key based on actual API response
                requirements_on_page = data.get("requirements", data.get("items", data.get("members", [])))
                all_requirements.extend([{"id": req.get("id"), "title": req.get("title")} for req in requirements_on_page])

                # Determine next page URL
                # 1. Check for 'nextPageUrl' in JSON response
                next_page_url = data.get("nextPageUrl")

                # 2. Check for 'Link' header with rel="next"
                if not next_page_url and 'Link' in response.headers:
                    links = requests.utils.parse_header_links(response.headers['Link'])
                    for link in links:
                        if link.get('rel') == 'next':
                            next_page_url = link.get('url')
                            break
                
                # 3. If still no explicit next page URL, and we got a full page, try incrementing page param
                # This part assumes the API might support a `page` parameter if others are missing.
                # This is a fallback and might not be supported by all APIs.
                if not next_page_url and len(requirements_on_page) == page_size:
                    current_page += 1
                    # We need to reconstruct the URL carefully, avoiding adding page if it was already there from Link header
                    # For simplicity, if we reach here, we assume the initial URL structure and add/increment page.
                    base_req_url = f"{self.base_url}/publish/projects/{project_id}/requirements"
                    next_page_url = f"{base_req_url}?pageSize={page_size}&page={current_page}"

                elif not next_page_url: # No more pages indicated
                    break
                
                # If we used the fallback page increment, we don't want to also increment current_page again
                # unless we are *not* using the fallback.
                if next_page_url and not (len(requirements_on_page) == page_size and "page=" in next_page_url) :
                     current_page +=1


            except requests.exceptions.HTTPError as e:
                if e.response.status_code in (401, 403):
                    raise DNGAuthenticationError(f"Authentication failed for {next_page_url}: {e.response.status_code} {e.response.text}")
                elif e.response.status_code == 404:
                    raise DNGNotFoundError(f"Project or requirements not found at {next_page_url}: {e.response.status_code} {e.response.text}")
                else:
                    raise DNGAPIError(f"DNG API error for {next_page_url}: {e.response.status_code} {e.response.text}")
            except requests.exceptions.RequestException as e:
                raise DNGAPIError(f"Request failed for {next_page_url}: {e}")
            except ValueError as e: # Handles JSON decoding errors
                raise DNGAPIError(f"Failed to decode JSON response from {next_page_url}: {e}")

        return all_requirements

    def get_requirement_details(self, requirement_id):
        """
        Retrieves detailed information for a specific requirement.

        Assumes the DNG endpoint for fetching requirement details is
        `self.base_url + f"/publish/requirements/{requirement_id}"`.
        The expected response is a single JSON object representing the full details
        of the requirement.

        Args:
            requirement_id (str): The ID of the requirement.

        Returns:
            dict: A dictionary containing the detailed information of the requirement.

        Raises:
            DNGAuthenticationError: If authentication fails (401 or 403).
            DNGNotFoundError: If the requirement is not found (404).
            DNGAPIError: For other 4xx or 5xx DNG API errors or request issues.
        """
        url = f"{self.base_url}/publish/requirements/{requirement_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()  # Raises HTTPError for 4xx/5xx responses
            return response.json()  # Returns the full JSON object

        except requests.exceptions.HTTPError as e:
            if e.response.status_code in (401, 403):
                raise DNGAuthenticationError(f"Authentication failed for {url}: {e.response.status_code} {e.response.text}")
            elif e.response.status_code == 404:
                raise DNGNotFoundError(f"Requirement not found at {url}: {e.response.status_code} {e.response.text}")
            else:
                raise DNGAPIError(f"DNG API error for {url}: {e.response.status_code} {e.response.text}")
        except requests.exceptions.RequestException as e:
            # Handle other request-related issues (e.g., network problems)
            raise DNGAPIError(f"Request failed for {url}: {e}")
        except ValueError as e: # Handles JSON decoding errors
            raise DNGAPIError(f"Failed to decode JSON response from {url}: {e}")

    def get_requirement_traceability(self, requirement_id):
        """
        Retrieves traceability links for a specific requirement.

        This method first attempts to get the full requirement details and inspects
        common keys (e.g., "links", "oslc_cm:relatedChangeManagement", "oslc_rm:validatedBy",
        "dcterms:relation", or other "oslc:" prefixed keys) for link information.

        If no direct links are found in the requirement details, it falls back to
        querying a dedicated links endpoint:
        `self.base_url + f"/publish/requirements/{requirement_id}/links"`.

        Args:
            requirement_id (str): The ID of the requirement.

        Returns:
            dict or list: The found links information (e.g., a list of link objects/URLs,
                          or the relevant section of the requirement details). If no links
                          are found, returns an empty list.

        Raises:
            DNGAuthenticationError: If authentication fails (401 or 403).
            DNGNotFoundError: If the requirement or links endpoint is not found (404).
            DNGAPIError: For other 4xx or 5xx DNG API errors or request issues.
        """
        try:
            # Initial Approach: Get requirement details and inspect for links
            requirement_details = self.get_requirement_details(requirement_id)

            # Define common keys that might contain link information
            # This list can be expanded based on DNG's specific OSLC vocabulary
            link_keys = [
                "links", "oslc_cm:relatedChangeManagement", "oslc_rm:validatedBy",
                "oslc_qm:validatedByTestCase", "oslc_am:tracksRequirement", "dcterms:relation"
            ]
            # Also consider any key starting with "oslc:" or containing "Link"
            
            found_links = {}
            for key, value in requirement_details.items():
                if key in link_keys or key.startswith("oslc:") or "Link" in key:
                    if value: # If there's any data associated with the key
                        found_links[key] = value
            
            if found_links:
                return found_links

            # Fallback: Query a dedicated links endpoint if no links found in details
            # This URL is an assumption and might need adjustment
            links_url = f"{self.base_url}/publish/requirements/{requirement_id}/links"
            # The following request is made only if the initial inspection yields nothing.
            # Errors from get_requirement_details would have been raised already.
            
            response = self.session.get(links_url)
            response.raise_for_status()
            links_data = response.json()
            # If links_data is empty or indicates no links, that's fine, return it.
            return links_data if links_data else []

        except DNGNotFoundError as e:
            # This could be from get_requirement_details or the fallback links_url call
            raise DNGNotFoundError(f"Requirement or its links endpoint not found for ID {requirement_id}: {e}")
        except DNGAuthenticationError as e:
            # Propagate auth errors from get_requirement_details or the links_url call
            raise DNGAuthenticationError(f"Authentication failed while fetching traceability for {requirement_id}: {e}")
        except DNGAPIError as e:
            # Propagate API errors
            raise DNGAPIError(f"DNG API error while fetching traceability for {requirement_id}: {e}")
        except requests.exceptions.HTTPError as e: # For the fallback call
            if e.response.status_code in (401, 403):
                raise DNGAuthenticationError(f"Authentication failed for links endpoint {links_url}: {e.response.status_code} {e.response.text}")
            elif e.response.status_code == 404:
                # If the dedicated links endpoint is not found, return empty list,
                # as the primary source (requirement details) already yielded no links.
                return []
            else:
                raise DNGAPIError(f"DNG API error for links endpoint {links_url}: {e.response.status_code} {e.response.text}")
        except requests.exceptions.RequestException as e: # For the fallback call
            raise DNGAPIError(f"Request failed for links endpoint {links_url}: {e}")
        except ValueError as e: # For the fallback call JSON decoding
            raise DNGAPIError(f"Failed to decode JSON response from links endpoint {links_url}: {e}")
        
        return [] # Default return if all else fails to find links
