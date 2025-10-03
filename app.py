from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from pathlib import Path

from models import InsuranceDataResponse, ErrorResponse
from mistral_parser import MistralDocumentParser
from openai_extractor import OpenAIExtractor
from config import settings

app = FastAPI(
    title="Insurance Document Data Extraction API",
    description="Extract structured data from insurance policy documents using Mistral AI + OpenAI",
    version="2.0.0"
)

# Initialize Mistral and OpenAI clients
try:
    mistralClient = MistralDocumentParser(api_key=settings.mistral_api_key)
except ValueError as e:
    print(f"Warning: Mistral - {str(e)}")
    mistralClient = None

try:
    openaiClient = OpenAIExtractor(api_key=settings.openai_api_key)
except ValueError as e:
    print(f"Warning: OpenAI - {str(e)}")
    openaiClient = None


@app.post(
    "/extract",
    response_model=InsuranceDataResponse,
    responses={
        401: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Extract insurance data from document",
    description="Upload an insurance document (PDF, DOC, DOCX, TXT, PNG, JPG) and extract structured data. Requires X-API-Key header."
)
async def extract_insurance_data(
    file: UploadFile = File(...),
    x_api_key: str = Header(..., alias="X-API-Key")
):
    """
    Extract insurance data from uploaded document

    Process:
    1. Validate API key
    2. Parse document using Mistral AI to extract text
    3. Extract structured data using OpenAI

    Args:
        file: Insurance document file (PDF, DOC, DOCX, TXT, PNG, JPG, JPEG)
        x_api_key: API authentication token (X-API-Key header)

    Returns:
        Extracted insurance data in JSON format
    """

    # Validate API key
    if x_api_key != settings.api_auth_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )

    # Check if services are initialized
    if mistralClient is None:
        raise HTTPException(
            status_code=500,
            detail="Mistral API key not configured. Please set MISTRAL_API_KEY environment variable."
        )

    if openaiClient is None:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
        )

    # Validate file format
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in MistralDocumentParser.SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_ext}. Supported formats: {', '.join(MistralDocumentParser.SUPPORTED_FORMATS)}"
        )

    try:
        # Read file content
        file_content = await file.read()

        # Validate file size
        if len(file_content) > MistralDocumentParser.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {MistralDocumentParser.MAX_FILE_SIZE // (1024*1024)}MB"
            )

        # Step 1: Parse document with Mistral AI to extract text
        document_text = mistralClient.parse_document(file_content, file.filename)

        # Step 2: Extract structured data using OpenAI
        result = openaiClient.extract_insurance_data(document_text)

        return InsuranceDataResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/", summary="Health check")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Insurance Document Data Extraction API",
        "version": "2.0.0"
    }


@app.get("/health", summary="Health check")
async def health_check():
    """Detailed health check"""
    mistral_configured = mistralClient is not None
    openai_configured = openaiClient is not None

    all_configured = mistral_configured and openai_configured

    return {
        "status": "healthy" if all_configured else "degraded",
        "mistral_configured": mistral_configured,
        "openai_configured": openai_configured,
        "supported_formats": list(MistralDocumentParser.SUPPORTED_FORMATS)
    }
