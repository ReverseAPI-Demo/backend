from fastapi import APIRouter, UploadFile, Depends, Form

from .dependancies import (
    validate_har,
    get_har_parser,
    get_llm_service,
    get_curl_generator,
    HarParserService,
    LLMService,
    CurlGeneratorService,
)

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

    return {
        "message": f"Found matching API request",
        "curl_command": curl_command,
    }
