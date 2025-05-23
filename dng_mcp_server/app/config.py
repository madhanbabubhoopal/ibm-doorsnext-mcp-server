import os

# DNG_BASE_URL: The base URL of the IBM DOORS Next Generation server.
# Example: export DNG_BASE_URL="https://your-dng-server.example.com/rm"
DNG_BASE_URL = os.getenv("DNG_BASE_URL")

# DNG_USERNAME: The username for authenticating with the DNG server.
# Example: export DNG_USERNAME="your_username"
DNG_USERNAME = os.getenv("DNG_USERNAME")

# DNG_API_KEY: The API key or password for authenticating with the DNG server.
# Example: export DNG_API_KEY="your_api_key_or_password"
DNG_API_KEY = os.getenv("DNG_API_KEY")
