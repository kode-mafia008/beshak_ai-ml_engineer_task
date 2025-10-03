import os
import base64
from io import BytesIO
from typing import List
import fitz  # PyMuPDF
from PIL import Image
from openai import OpenAI
import docx
from dotenv import load_dotenv

load_dotenv()


def extract_text_from_pdf_with_openai(file_path: str) -> str:
    """
    Extract text from PDF using OpenAI Vision API
    Converts PDF pages to images and uses GPT-4o-mini vision to extract text
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(file_path)
        extracted_texts = []
        
        # Process each page
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            # Convert page to image (higher DPI for better quality)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
            img_data = pix.tobytes("png")
            
            # Convert to base64
            base64_image = base64.b64encode(img_data).decode('utf-8')
            
            # Call OpenAI Vision API
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts text from images. Extract ALL text from the image accurately, maintaining the structure and formatting as much as possible."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please extract all the text from this document image. Preserve the structure and formatting."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4096,
                temperature=0.0
            )
            
            page_text = response.choices[0].message.content
            extracted_texts.append(f"--- Page {page_num + 1} ---\n{page_text}")
        
        pdf_document.close()
        
        # Combine all pages
        return "\n\n".join(extracted_texts)
        
    except Exception as e:
        raise Exception(f"Error extracting text from PDF using OpenAI: {str(e)}")


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from DOCX: {str(e)}")


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from TXT: {str(e)}")


def extract_text_from_document(file_path: str, file_extension: str) -> str:
    """
    Extract text from document based on file type
    Uses OpenAI Vision API for PDFs, native libraries for other formats
    """
    try:
        if file_extension == '.pdf':
            return extract_text_from_pdf_with_openai(file_path)
        elif file_extension == '.txt':
            return extract_text_from_txt(file_path)
        elif file_extension in ['.docx', '.doc']:
            return extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    except Exception as e:
        raise Exception(f"Error extracting text from {file_extension} file: {str(e)}")


# Legacy functions for backward compatibility
def read_pdf(file_path: str) -> str:
    """Extract text from PDF file using OpenAI Vision API"""
    return extract_text_from_pdf_with_openai(file_path)


def read_txt(file_path: str) -> str:
    """Extract text from TXT file"""
    return extract_text_from_txt(file_path)


def read_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    return extract_text_from_docx(file_path)