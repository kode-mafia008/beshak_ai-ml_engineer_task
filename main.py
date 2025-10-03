"""
Document Information Extractor using Google Generative AI
Extracts specific fields from insurance policy documents (PDF/TXT/DOCX)
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import os
from pathlib import Path
import tempfile
import uvicorn
import json
from ai_integration import InsurancePolicyData,InsurancePDFProcessor
from utils import extract_text_from_document

# Initialize FastAPI app
app = FastAPI(
    title="Document Information Extractor API",
    description="Extract structured information from insurance policy documents using LLM",
    version="1.0.0"
)

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Document Information Extractor API",
        "version": "1.0.0",
        "endpoints": {
            "/extract": "POST - Upload document to extract information",
            "/docs": "GET - API documentation (Swagger UI)",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if API key is set
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "message": "OPENAI_API_KEY not configured"}
            )
        return {"status": "healthy"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "message": str(e)}
        )

@app.post("/extract", response_model=InsurancePolicyData)
async def extract_document_info(file: UploadFile = File(...)):
    """
    Extract structured information from an uploaded document
    
    Supports: PDF, TXT, DOCX files
    
    Returns: JSON with extracted insurance policy information
    """
    
    # Validate file extension
    pdf_processor = InsurancePDFProcessor()
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ['.pdf', '.txt', '.docx']:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Please upload PDF, TXT, or DOCX files."
        )
    
    # Save uploaded file temporarily
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Extract text from document
        document_text = extract_text_from_document(temp_file_path, file_extension)

        with open("extract.txt", "w") as f:
            f.write(document_text)
        
        if not document_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the document"
            )
        
        # Extract structured information using LLM
        extracted_data = pdf_processor.generate(document_text)
        
        return extracted_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@app.post("/extract-text")
async def extract_from_text(text: str):
    """
    Extract structured information from provided text directly
    
    Useful for testing or when text is already extracted
    """
    pdf_processor = InsurancePDFProcessor()
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        extracted_data = pdf_processor.generate(text)
        return extracted_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

