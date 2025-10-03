import base64
from mistralai import Mistral


class MistralDocumentParser:
    """Handles document parsing using Mistral AI OCR"""

    SUPPORTED_FORMATS = {'.pdf', '.doc', '.docx', '.txt', '.png', '.jpg', '.jpeg'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB (Mistral OCR limit)

    def __init__(self, api_key: str):
        """Initialize Mistral client"""
        if not api_key:
            raise ValueError("Mistral API key not provided")

        self.api_key = api_key
        self.client = Mistral(api_key=self.api_key)

    def parse_document(self, file_content: bytes, filename: str) -> str:
        """
        Parse document using Mistral AI OCR and extract text content

        Args:
            file_content: Binary content of the file
            filename: Name of the file

        Returns:
            Extracted text content from the document
        """
        try:
            # Encode file as base64
            base64_content = base64.b64encode(file_content).decode('utf-8')

            # Determine file type
            file_ext = filename.lower().split('.')[-1]

            # Map file extensions to MIME types
            mime_types = {
                'pdf': 'application/pdf',
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'txt': 'text/plain',
                'doc': 'application/msword',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }

            mime_type = mime_types.get(file_ext, 'application/octet-stream')

            # Create data URL for the document
            data_url = f"data:{mime_type};base64,{base64_content}"

            # Use Mistral's OCR API with correct document format
            ocr_response = self.client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": data_url
                },
                include_image_base64=True
            )

            # Extract text from OCR response pages
            extracted_text = []

            # The response contains pages with markdown content
            if hasattr(ocr_response, 'pages') and ocr_response.pages:
                for page in ocr_response.pages:
                    if hasattr(page, 'markdown') and page.markdown:
                        extracted_text.append(page.markdown)

            if not extracted_text:
                raise ValueError("No text content found in OCR response")

            # Join all pages with double newlines
            return '\n\n'.join(extracted_text)

        except Exception as e:
            raise RuntimeError(f"Mistral OCR error: {str(e)}")
