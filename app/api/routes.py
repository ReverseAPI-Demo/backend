from fastapi import APIRouter, UploadFile, Depends, Form

from .dependancies import (
    validate_har,
    get_har_parser,
    get_llm_service,
    HarParserService,
    LLMService,
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
):
    content = await file.read()
    requests = har_parser.extract_requests(content)

    if not requests:
        return {"message": "No API Requests found in the har file."}

    matched_request = llm_service.identify_request(requests, api_description)

    return {
        "message": f"Found matching API request",
        "matched_request": matched_request,
    }
