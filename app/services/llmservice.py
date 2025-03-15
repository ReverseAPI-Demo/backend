import os
import json
import dotenv
from typing import List, Dict, Any
from urllib.parse import urlparse

import openai

dotenv.load_dotenv()


# llm service uses openai to find best requests
class LLMService:
    _instance = None

    # make sure singleton internally so that we only have 1 instance of the api client
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
            cls._instance._init_resources()
        return cls._instance

    def _init_resources(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        openai.api_key = self.api_key
        self.model = os.getenv("LLM_MODEL", "gpt-4o-2024-08-06")

    def identify_request(
        self, api_requests: List[Dict[str, Any]], description: str
    ) -> Dict[str, Any]:
        """
        this will use the llm ot find the best request
        """
        if not api_requests:
            raise ValueError("No API requests provided for analysis")

        request_summaries = []
        for i, req in enumerate(api_requests):
            url = req.get("url", "")
            method = req.get("method", "")
            status = req.get("response_status")
            content_type = req.get("response_type", "")

            domain = urlparse(url).netloc if url else ""

            query_sample = ""
            if req.get("query_params"):
                params = list(req.get("query_params", {}).items())[:3]
                if params:
                    query_sample = f"Query params: {dict(params)}"
                    if len(req.get("query_params", {})) > 3:
                        query_sample += " (and more...)"

            body_hint = ""
            if req.get("post_data"):
                mime = req.get("post_data", {}).get("mime_type", "")
                body_hint = f"Has {mime} body data"

            summary = {
                "id": i,
                "method": method,
                "domain": domain,
                "path": urlparse(url).path if url else "",
                "status": status,
                "content_type": content_type,
            }

            if query_sample:
                summary["query_sample"] = query_sample
            if body_hint:
                summary["body_hint"] = body_hint

            request_summaries.append(summary)

        prompt = f"""
        I need to identify the most relevant API request from a HAR file based on this user description:
        "{description}"
        
        Below are the available API requests captured from a web browser session.
        I need to find the API request that best matches the user's description.
        Only consider actual API endpoints, not static resources or page loads.
        
        Available API requests:
        {json.dumps(request_summaries, indent=2)}
        
        Analyze these requests and return ONLY the ID of the most likely match and no other characters in the output.
        """

        try:

            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )

            result_text = response.choices[0].message.content

            try:
                request_id = int(result_text)

                if request_id is not None and 0 <= request_id < len(api_requests):
                    return api_requests[request_id]
                else:

                    return api_requests[0]

            except json.JSONDecodeError:

                return api_requests[0]

        except Exception as e:
            raise Exception(f"Error calling LLM API: {str(e)}")
