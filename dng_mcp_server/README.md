# DNG MCP Server

## Overview
This server provides a set of read-only MCP (Machine Control Plane) tools for interacting with IBM DOORS Next Generation (DNG). It allows users to retrieve information about project areas, requirements, and their traceability links via a RESTful API.

## Prerequisites
- Python 3.x (3.7 or higher recommended)
- The following environment variables must be set:
    - `DNG_BASE_URL`: The base URL of your IBM DOORS Next Generation server.
        - Example: `export DNG_BASE_URL="https://your-dng-server.example.com/rm"`
    - `DNG_USERNAME`: Your username for authenticating with the DNG server.
        - Example: `export DNG_USERNAME="your_username"`
    - `DNG_API_KEY`: Your API key or password for authenticating with the DNG server.
        - Example: `export DNG_API_KEY="your_api_key_or_password"`

## Setup and Installation
1.  **Clone the repository** (if applicable):
    ```bash
    git clone <repository_url>
    cd dng_mcp_server
    ```
2.  **Create a virtual environment** (recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Server
To start the Flask development server:
```bash
python app/main.py
```
The server will start on `http://0.0.0.0:5000` by default and will be running in debug mode.

## API Endpoints (MCP Tools)

All DNG tool endpoints are prefixed with `/mcp/tools/dng`.

---

### 1. List Project Areas
-   **HTTP Method & Path:** `GET /mcp/tools/dng/project_areas`
-   **Description:** Retrieves a list of all accessible project areas from the DNG server.
-   **Parameters:** None.
-   **Example Successful Response (200 OK):**
    ```json
    [
        {
            "id": "pa1_id",
            "name": "Project Area 1 Title"
        },
        {
            "id": "pa2_id",
            "name": "Project Area 2 Title"
        }
    ]
    ```
-   **Example Error Responses:**
    -   **Authentication Error (401 Unauthorized):**
        ```json
        {
            "error": "AuthenticationError",
            "message": "Authentication failed for https://your-dng-server.example.com/rm/publish/project_areas: 401 Client Error: Unauthorized for url: ..."
        }
        ```
    -   **Configuration Error (500 Internal Server Error):**
        ```json
        {
            "error": "ConfigurationError",
            "message": "DNG server configuration is incomplete. Please set DNG_BASE_URL, DNG_USERNAME, and DNG_API_KEY environment variables."
        }
        ```
    -   **DNG API Error (500 Internal Server Error):**
        ```json
        {
            "error": "APIError",
            "message": "DNG API error for https://your-dng-server.example.com/rm/publish/project_areas: 500 Server Error: Internal Server Error for url: ..."
        }
        ```

---

### 2. List Requirements for a Project
-   **HTTP Method & Path:** `GET /mcp/tools/dng/projects/<project_id>/requirements`
-   **Description:** Retrieves a list of requirements for a specified project ID. Supports pagination.
-   **Parameters:**
    -   **Path:**
        -   `<project_id>` (string, required): The ID of the project.
    -   **Query:**
        -   `page_size` (integer, optional, default: 100): Number of requirements per page.
        -   `max_pages` (integer, optional, default: None): Maximum number of pages to fetch.
-   **Example Successful Response (200 OK):**
    ```json
    [
        {
            "id": "req1_id",
            "title": "Requirement 1 Title"
        },
        {
            "id": "req2_id",
            "title": "Requirement 2 Title"
        }
    ]
    ```
-   **Example Error Responses:**
    -   **Invalid Input (400 Bad Request):**
        ```json
        {
            "error": "InvalidInputError",
            "message": "page_size must be a positive integer."
        }
        ```
    -   **Not Found (404 Not Found):** (If the project ID is invalid or the endpoint doesn't exist)
        ```json
        {
            "error": "NotFoundError",
            "message": "Project or requirements not found at https://your-dng-server.example.com/rm/publish/projects/invalid_proj_id/requirements?pageSize=100: 404 Client Error: Not Found for url: ..."
        }
        ```
    -   **Authentication Error (401 Unauthorized):** (As above)
    -   **Configuration Error (500 Internal Server Error):** (As above)

---

### 3. Get Requirement Details
-   **HTTP Method & Path:** `GET /mcp/tools/dng/requirements/<requirement_id>`
-   **Description:** Retrieves detailed information for a specific requirement ID.
-   **Parameters:**
    -   **Path:**
        -   `<requirement_id>` (string, required): The ID of the requirement.
-   **Example Successful Response (200 OK):**
    ```json
    {
        "id": "req1_id",
        "title": "Requirement 1 Title",
        "description": "Detailed description of the requirement...",
        "creator": "user_x",
        "created_at": "2023-01-15T10:00:00Z",
        "custom_attribute_1": "Value 1",
        "oslc_rm:validatedBy": [
            { "rdf:resource": "https://your-dng-server.example.com/qm/oslc_qm/resources/_validation_test_case_id" }
        ]
        // ... other fields
    }
    ```
-   **Example Error Responses:**
    -   **Not Found (404 Not Found):** (If the requirement ID is invalid)
        ```json
        {
            "error": "NotFoundError",
            "message": "Requirement not found at https://your-dng-server.example.com/rm/publish/requirements/invalid_req_id: 404 Client Error: Not Found for url: ..."
        }
        ```
    -   **Authentication Error (401 Unauthorized):** (As above)
    -   **Configuration Error (500 Internal Server Error):** (As above)

---

### 4. Get Requirement Traceability Links
-   **HTTP Method & Path:** `GET /mcp/tools/dng/requirements/<requirement_id>/traceability`
-   **Description:** Retrieves traceability links (e.g., "validatedBy", "relatedChangeManagement") for a specific requirement ID.
-   **Parameters:**
    -   **Path:**
        -   `<requirement_id>` (string, required): The ID of the requirement.
-   **Example Successful Response (200 OK - with links):**
    ```json
    {
        "oslc_rm:validatedBy": [
            { "rdf:resource": "https://your-dng-server.example.com/qm/oslc_qm/resources/_test_case_id_1" }
        ],
        "oslc_cm:relatedChangeManagement": [
            { "rdf:resource": "https://your-dng-server.example.com/ccm/resource/itemName/com.ibm.team.workitem.WorkItem/123" }
        ]
        // ... other link types
    }
    ```
-   **Example Successful Response (200 OK - no links):**
    ```json
    {
        "message": "No traceability links found for this requirement.",
        "links": []
    }
    ```
-   **Example Error Responses:**
    -   **Not Found (404 Not Found):** (If the requirement ID is invalid, or the specific links endpoint for it is not found)
        ```json
        {
            "error": "NotFoundError",
            "message": "Requirement or its links endpoint not found for ID invalid_req_id: Requirement not found at https://your-dng-server.example.com/rm/publish/requirements/invalid_req_id: 404 Client Error: Not Found for url: ..."
        }
        ```
    -   **Authentication Error (401 Unauthorized):** (As above)
    -   **Configuration Error (500 Internal Server Error):** (As above)

---
