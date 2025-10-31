from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
from typing import Dict

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class AttachmentRequest(BaseModel):
    attachments: Dict[str, str]

class MimeTypeResponse(BaseModel):
    type: str

@app.post("/file", response_model=MimeTypeResponse)
async def detect_mime_type(request: AttachmentRequest):
    """
    Detect MIME type from a data URI.
    
    Args:
        request: JSON with attachments containing a data URI
        
    Returns:
        JSON with the detected MIME type category
    """
    try:
        # Get the data URI from the attachments
        if "url" not in request.attachments:
            raise HTTPException(status_code=400, detail="Missing 'url' in attachments")
        
        data_uri = request.attachments["url"]
        
        # Parse the data URI to extract MIME type
        # Data URI format: data:[<mediatype>][;base64],<data>
        match = re.match(r'^data:([^;,]+)?(;base64)?,(.+)$', data_uri)
        
        if not match:
            return MimeTypeResponse(type="unknown")
        
        mime_type = match.group(1) if match.group(1) else ""
        
        # Determine the type category based on MIME type
        if mime_type.startswith("image/"):
            return MimeTypeResponse(type="image")
        elif mime_type.startswith("text/"):
            return MimeTypeResponse(type="text")
        elif mime_type.startswith("application/"):
            return MimeTypeResponse(type="application")
        else:
            # If no MIME type or unrecognized, return unknown
            return MimeTypeResponse(type="unknown")
            
    except Exception as e:
        # In case of any error, return unknown
        return MimeTypeResponse(type="unknown")

# Optional: Add a health check endpoint
@app.get("/")
async def health_check():
    return {"status": "healthy", "service": "MIME Type Detector API"}
