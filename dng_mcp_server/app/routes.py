from flask import Blueprint, jsonify, request
from .config import DNG_BASE_URL, DNG_USERNAME, DNG_API_KEY
from .dng_client import DNGClient, DNGAuthenticationError, DNGNotFoundError, DNGAPIError

dng_bp = Blueprint('dng', __name__, url_prefix='/mcp/tools/dng')

@dng_bp.route('/project_areas', methods=['GET'])
def list_project_areas():
    """
    Retrieves and returns a list of project areas from the DNG server.

    Example Error Responses:
        - 401: `{"error": "AuthenticationError", "message": "Authentication failed..."}`
        - 404: `{"error": "NotFoundError", "message": "Resource not found..."}`
        - 500: `{"error": "APIError", "message": "DNG API error..."}`
        - 500: `{"error": "ConfigurationError", "message": "DNG server configuration is incomplete..."}`
        - 500: `{"error": "UnexpectedError", "message": "An unexpected error occurred..."}`
    """
    if not all([DNG_BASE_URL, DNG_USERNAME, DNG_API_KEY]):
        return jsonify({
            "error": "ConfigurationError",
            "message": "DNG server configuration is incomplete. "
                       "Please set DNG_BASE_URL, DNG_USERNAME, and DNG_API_KEY environment variables."
        }), 500

    dng_client = DNGClient(base_url=DNG_BASE_URL, username=DNG_USERNAME, api_key=DNG_API_KEY)

    try:
        project_areas = dng_client.get_project_areas()
        return jsonify(project_areas), 200
    except DNGAuthenticationError as e:
        return jsonify({"error": "AuthenticationError", "message": str(e)}), 401
    except DNGNotFoundError as e:
        return jsonify({"error": "NotFoundError", "message": str(e)}), 404
    except DNGAPIError as e:
        return jsonify({"error": "APIError", "message": str(e)}), 500
    except Exception as e:
        # Log the exception e for debugging
        return jsonify({"error": "UnexpectedError", "message": str(e)}), 500

@dng_bp.route('/requirements/<requirement_id>/traceability', methods=['GET'])
def get_requirement_traceability_route(requirement_id):
    """
    Retrieves and returns traceability links for a specific DNG requirement.

    Path Parameter:
        requirement_id (str): The ID of the requirement.

    Example Error Responses:
        - 401: `{"error": "AuthenticationError", "message": "Authentication failed..."}`
        - 404: `{"error": "NotFoundError", "message": "Resource not found..."}`
        - 500: `{"error": "APIError", "message": "DNG API error..."}`
        - 500: `{"error": "ConfigurationError", "message": "DNG server configuration is incomplete..."}`
        - 500: `{"error": "UnexpectedError", "message": "An unexpected error occurred..."}`
    """
    if not all([DNG_BASE_URL, DNG_USERNAME, DNG_API_KEY]):
        return jsonify({
            "error": "ConfigurationError",
            "message": "DNG server configuration is incomplete. "
                       "Please set DNG_BASE_URL, DNG_USERNAME, and DNG_API_KEY environment variables."
        }), 500

    dng_client = DNGClient(base_url=DNG_BASE_URL, username=DNG_USERNAME, api_key=DNG_API_KEY)

    try:
        traceability_info = dng_client.get_requirement_traceability(requirement_id)
        if not traceability_info: # Handles empty list or dict
            return jsonify({"message": "No traceability links found for this requirement.", "links": []}), 200
        return jsonify(traceability_info), 200
    except DNGAuthenticationError as e:
        return jsonify({"error": "Authentication failed", "message": str(e)}), 401
    except DNGNotFoundError as e:
        return jsonify({"error": "Resource not found (requirement or links endpoint)", "message": str(e)}), 404
    except DNGAPIError as e:
        return jsonify({"error": "DNG API error", "message": str(e)}), 500
    except Exception as e:
        # Log the exception e for debugging
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500

@dng_bp.route('/requirements/<requirement_id>', methods=['GET'])
def get_requirement_details_route(requirement_id):
    """
    Retrieves and returns detailed information for a specific DNG requirement.

    Path Parameter:
        requirement_id (str): The ID of the requirement.

    Example Error Responses:
        - 401: `{"error": "AuthenticationError", "message": "Authentication failed..."}`
        - 404: `{"error": "NotFoundError", "message": "Resource not found..."}`
        - 500: `{"error": "APIError", "message": "DNG API error..."}`
        - 500: `{"error": "ConfigurationError", "message": "DNG server configuration is incomplete..."}`
        - 500: `{"error": "UnexpectedError", "message": "An unexpected error occurred..."}`
    """
    if not all([DNG_BASE_URL, DNG_USERNAME, DNG_API_KEY]):
        return jsonify({
            "error": "ConfigurationError",
            "message": "DNG server configuration is incomplete. "
                       "Please set DNG_BASE_URL, DNG_USERNAME, and DNG_API_KEY environment variables."
        }), 500

    dng_client = DNGClient(base_url=DNG_BASE_URL, username=DNG_USERNAME, api_key=DNG_API_KEY)

    try:
        requirement_details = dng_client.get_requirement_details(requirement_id)
        return jsonify(requirement_details), 200
    except DNGAuthenticationError as e:
        return jsonify({"error": "AuthenticationError", "message": str(e)}), 401
    except DNGNotFoundError as e:
        return jsonify({"error": "NotFoundError", "message": str(e)}), 404
    except DNGAPIError as e:
        return jsonify({"error": "APIError", "message": str(e)}), 500
    except Exception as e:
        # Log the exception e for debugging
        return jsonify({"error": "UnexpectedError", "message": str(e)}), 500

@dng_bp.route('/projects/<project_id>/requirements', methods=['GET'])
def list_requirements(project_id):
    """
    Retrieves and returns a list of requirements for a specific DNG project.

    Path Parameter:
        project_id (str): The ID of the project.
    Query Parameters:
        page_size (int): Number of requirements per page. Defaults to 100.
        max_pages (int): Maximum number of pages to fetch. Defaults to None (all pages).

    Example Error Responses:
        - 400: `{"error": "InvalidInputError", "message": "page_size and max_pages must be integers."}`
        - 401: `{"error": "AuthenticationError", "message": "Authentication failed..."}`
        - 404: `{"error": "NotFoundError", "message": "Resource not found..."}`
        - 500: `{"error": "APIError", "message": "DNG API error..."}`
        - 500: `{"error": "ConfigurationError", "message": "DNG server configuration is incomplete..."}`
        - 500: `{"error": "UnexpectedError", "message": "An unexpected error occurred..."}`
    """
    if not all([DNG_BASE_URL, DNG_USERNAME, DNG_API_KEY]):
        return jsonify({
            "error": "ConfigurationError",
            "message": "DNG server configuration is incomplete. "
                       "Please set DNG_BASE_URL, DNG_USERNAME, and DNG_API_KEY environment variables."
        }), 500

    try:
        page_size = int(request.args.get('page_size', 100))
        if page_size <= 0:
            return jsonify({"error": "InvalidInputError", "message": "page_size must be a positive integer."}), 400
        max_pages_str = request.args.get('max_pages')
        max_pages = None
        if max_pages_str is not None:
            max_pages = int(max_pages_str)
            if max_pages <= 0:
                return jsonify({"error": "InvalidInputError", "message": "max_pages must be a positive integer if provided."}), 400
    except ValueError:
        return jsonify({"error": "InvalidInputError", "message": "page_size and max_pages must be integers."}), 400

    dng_client = DNGClient(base_url=DNG_BASE_URL, username=DNG_USERNAME, api_key=DNG_API_KEY)

    try:
        requirements = dng_client.get_requirements(project_id, page_size=page_size, max_pages=max_pages)
        return jsonify(requirements), 200
    except DNGAuthenticationError as e:
        return jsonify({"error": "AuthenticationError", "message": str(e)}), 401
    except DNGNotFoundError as e:
        return jsonify({"error": "NotFoundError", "message": str(e)}), 404
    except DNGAPIError as e:
        return jsonify({"error": "APIError", "message": str(e)}), 500
    except Exception as e:
        # Log the exception e for debugging
        return jsonify({"error": "UnexpectedError", "message": str(e)}), 500
