import textract

def extract_text_from_document(file_path: str, file_extension: str) -> str:
    """Extract text from document using textract - supports multiple formats"""
    try:
        # textract automatically handles different file types
        text = textract.process(file_path).decode('utf-8')
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from {file_extension} file: {str(e)}")

# Legacy functions for backward compatibility (all use textract internally)
def read_pdf(file_path: str) -> str:
    """Extract text from PDF file using textract"""
    return extract_text_from_document(file_path, '.pdf')

def read_txt(file_path: str) -> str:
    """Extract text from TXT file using textract"""
    return extract_text_from_document(file_path, '.txt')

def read_docx(file_path: str) -> str:
    """Extract text from DOCX file using textract"""
    return extract_text_from_document(file_path, '.docx')