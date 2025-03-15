from fastapi import UploadFile, File, HTTPException
from app.services import HarParserService, LLMService

# defining outside in global scope so we only have 1 instance of the singleton
_har_parser = None
_llm_service = None


def get_har_parser():
    global _har_parser
    if _har_parser is None:
        _har_parser = HarParserService()
    return _har_parser


def get_llm_service():
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def validate_har(file: UploadFile = File(...)):
    if not file.filename.endswith(".har"):
        raise HTTPException(status_code=400, detail="File must be a .har file")
    return file
