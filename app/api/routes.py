import json
from fastapi import APIRouter, UploadFile, Depends, Form, Response, HTTPException
import httpx

from .dependancies import (
    validate_har,
    get_har_parser,
    get_llm_service,
    get_curl_generator,
    HarParserService,
    LLMService,
    CurlGeneratorService,
)

from app.models import ExecuteRequestData

app = APIRouter()


@app.get("/api/health")
def health():
    return {"message": "Reverse API running.."}


@app.post("/api/process-har")
async def process_har(
    file: UploadFile = Depends(validate_har),
    api_description: str = Form(...),
    har_parser: HarParserService = Depends(get_har_parser),
    llm_service: LLMService = Depends(get_llm_service),
    curl_generator: CurlGeneratorService = Depends(get_curl_generator),
):
    content = await file.read()
    requests = har_parser.extract_requests(content)

    if not requests:
        return {"message": "No API Requests found in the har file."}

    matched_request = llm_service.identify_request(requests, api_description)

    if not matched_request:
        return {"message": "Could not find any requests matching the description."}

    curl_command = curl_generator.generate(matched_request)

    return Response(content=curl_command)


@app.post("/api/execute-request")
async def execute_request(request_data: ExecuteRequestData):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request_data.method,
                url=request_data.url,
                headers=request_data.headers,
                content=request_data.data,
            )

        headers_dict = dict(response.headers)

        custom_response = Response(
            content=response.content,
            status_code=response.status_code,
        )

        custom_response.headers["x-proxied-headers"] = json.dumps(headers_dict)

        return custom_response

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error executing request: {str(e)}"
        )
