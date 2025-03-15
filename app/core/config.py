HAR_ANALYSIS_PROMPT = """
I need to identify the most relevant API request from a HAR file based on this user description:
"{description}"

Below are the available API requests captured from a web browser session.
I need to find the API request that best matches the user's description.
Only consider actual API endpoints, not static resources or page loads.

Available API requests:
{requests}

Analyze these requests and return ONLY the ID of the most likely match and no other characters apart from it.
If user has extra requests, just ignore, only the id should ever be returned.
"""
