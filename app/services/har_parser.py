import json
from typing import List, Dict, Any
from urllib.parse import urlparse


# Har parser service mainly does 1 job, to parse har files and return a formatted array of api requests
class HarParserService:
    def extract_requests(self, har_content: bytes) -> List[Dict[str, Any]]:
        """
        Function to extract the har requests from the content from file
        takes in the actual content of the har file in bytes from .read()
        returns the requests in a dict format
        """
        try:
            har_data = json.loads(har_content)
            entries = har_data.get("log", {}).get("entries", [])

            api_requests = []
            for entry in entries:
                request = entry.get("request", {})
                response = entry.get("response", {})

                # skip invalid
                if not self._is_valid_entry(request, response):
                    continue

                # skip things that are not an api so like fonts and stuff
                if self._should_filter_request(request, response):
                    continue

                api_request = self._extract_request_data(request, response)
                api_requests.append(api_request)

            return api_requests

        except Exception as e:
            raise ValueError(f"Error parsing HAR file: {str(e)}")

    def _is_valid_entry(self, request: Dict, response: Dict) -> bool:
        """
        checks if entry is a url and a valid api
        """
        return request and response and request.get("url") and response.get("status")

    def _should_filter_request(self, request: Dict, response: Dict) -> bool:
        """
        filters out some requests (this should ideally be configurable maybe)
        """
        url = request.get("url", "").lower()
        content_type = response.get("content", {}).get("mimeType", "").lower()

        # first filter for things that are for content like fonts
        if any(
            item in content_type
            for item in ["html", "font", "image", "css", "javascript"]
        ):
            return True

        # then for url patterns
        # (I saw a lot of requests that were not font but had font files, prob extentions)
        if any(
            pattern in url
            for pattern in [
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".svg",
                ".css",
                ".js",
                ".woff",
                ".woff2",
                ".ttf",
                ".eot",
                ".ico",
                "favicon",
                "analytics",
                "tracking",
                "pixel",
                "metrics",
                "beacon",
                "fonts.googleapis.com",
                "google-analytics",
                "doubleclick",
            ]
        ):
            return True

        # specific extension requests, should probably have more browsers supported
        # chrome is just what I use rn
        if "chrome-extension://" in url:
            return True

        return False

    def _extract_request_data(self, request: Dict, response: Dict) -> Dict[str, Any]:
        """
        extract the actual request data key-values
        """
        url = request.get("url", "")

        api_request = {
            "method": request.get("method"),
            "url": url,
            "headers": {
                h.get("name"): h.get("value") for h in request.get("headers", [])
            },
            "query_params": {
                p.get("name"): p.get("value") for p in request.get("queryString", [])
            },
            "response_status": response.get("status"),
            "response_type": response.get("content", {}).get("mimeType", ""),
        }

        parsed_url = urlparse(url)
        api_request["domain"] = parsed_url.netloc
        api_request["path"] = parsed_url.path

        self._add_post_data(api_request, request)

        return api_request

    def _add_post_data(self, api_request: Dict[str, Any], request: Dict) -> None:
        """
        if api request is POST, we should take the data as well
        """
        post_data = request.get("postData", {})
        if post_data:
            api_request["post_data"] = {
                "mime_type": post_data.get("mimeType", ""),
                "text": post_data.get("text", ""),
            }
            if "params" in post_data:
                api_request["post_params"] = {
                    p.get("name"): p.get("value") for p in post_data.get("params", [])
                }
