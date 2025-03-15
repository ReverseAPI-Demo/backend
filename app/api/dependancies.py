from fastapi import UploadFile, File, HTTPException


def validate_har(file: UploadFile = File(...)):
    if not file.filename.endswith(".har"):
        raise HTTPException(status_code=400, detail="File must be a .har file")
    return file
