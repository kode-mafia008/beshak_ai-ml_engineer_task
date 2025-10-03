# Document Information Extractor - Setup Guide

A Python-based document information extractor that uses Google's Gemini LLM to extract structured data from insurance policy documents (PDF/TXT/DOCX).

## Features

- ✅ Supports PDF, TXT, and DOCX formats
- ✅ Extracts 8 key fields from insurance documents
- ✅ Uses Google Gemini (free tier) via LangChain
- ✅ FastAPI REST API endpoints
- ✅ Structured JSON output using Pydantic
- ✅ Interactive API documentation (Swagger UI)

## Prerequisites

- Python 3.8 or higher
- Google API Key (free from Google AI Studio)

## Installation

### Step 1: Clone or Download the Project

Save the provided Python script as `main.py` and `requirements.txt` in your project directory.

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Get Google Gemini API Key (Free)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key" or "Create API Key"
3. Copy your API key

### Step 5: Set Environment Variable

**On Windows (Command Prompt):**
```cmd
set GOOGLE_API_KEY=your_api_key_here
```

**On Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY="your_api_key_here"
```

**On macOS/Linux:**
```bash
export GOOGLE_API_KEY=your_api_key_here
```

**Permanent setup (recommended):**

Create a `.env` file in your project directory:
```
GOOGLE_API_KEY=your_api_key_here
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

Add to the top of `main.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Usage

### Start the Server

```bash
python main.py
```

The API will be available at: `http://localhost:8000`

### API Endpoints

1. **Root Endpoint**: `GET /`
   - Returns API information

2. **Health Check**: `GET /health`
   - Check if API is running and configured correctly

3. **Extract from File**: `POST /extract`
   - Upload a document file (PDF/TXT/DOCX)
   - Returns extracted information as JSON

4. **Extract from Text**: `POST /extract-text`
   - Send text directly
   - Returns extracted information as JSON

5. **API Documentation**: `GET /docs`
   - Interactive Swagger UI documentation

### Testing the API

#### Option 1: Using the Interactive Docs (Easiest)

1. Open browser: `http://localhost:8000/docs`
2. Click on `/extract` endpoint
3. Click "Try it out"
4. Upload your document
5. Click "Execute"
6. View the extracted JSON response

#### Option 2: Using cURL

```bash
curl -X POST "http://localhost:8000/extract" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_insurance_doc.pdf"
```

#### Option 3: Using Python Requests

```python
import requests

url = "http://localhost:8000/extract"
files = {"file": open("sample_insurance_doc.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

#### Option 4: Using Postman

1. Create new POST request to `http://localhost:8000/extract`
2. Go to Body → form-data
3. Add key `file` (change type to File)
4. Upload your document
5. Send request

### Example Response

```json
{
  "name": "Anurag Upadhyay",
  "policy_number": "P/189270/01/2020/0668166",
  "email": "anuraobmas07@gmail.com",
  "policy_name": "Family Health Optima Insurance Plan",
  "plan_type": "2A",
  "sum_assured": "Rs. 300000",
  "room_rent_limit": "Single Private AC",
  "waiting_period": "30 days"
}
```

## Project Structure

```
project/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
└── README.md           # This file
```

## Extracted Fields

The system extracts the following fields from insurance documents:

1. **Name**: Policy holder's name
2. **Policy Number**: Insurance policy number
3. **Email**: Email address
4. **Policy Name**: Name of the insurance plan
5. **Plan Type**: Type/category of plan
6. **Sum Assured**: Coverage amount
7. **Room Rent Limit**: Room rent limitations
8. **Waiting Period**: Waiting period details

## Troubleshooting

### API Key Not Set
```
Error: GOOGLE_API_KEY environment variable not set
```
**Solution**: Set the GOOGLE_API_KEY environment variable as described in Step 5.

### ModuleNotFoundError
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: Ensure virtual environment is activated and run `pip install -r requirements.txt`

### PDF Reading Issues
```
Error reading PDF
```
**Solution**: Ensure the PDF is not encrypted or password-protected. Try converting to TXT/DOCX.

### Port Already in Use
```
Error: [Errno 48] Address already in use
```
**Solution**: Change the port in `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Changed to 8001
```

## Free Tier Limits

**Google Gemini Free Tier:**
- 60 requests per minute
- 1,500 requests per day
- Sufficient for development and testing

## Customization

### Add More Fields

1. Update the `InsurancePolicyData` model in `main.py`:
```python
class InsurancePolicyData(BaseModel):
    # ... existing fields ...
    premium_amount: Optional[str] = Field(description="Premium amount")
```

2. Update the prompt to include the new field

### Change LLM Model

Replace `gemini-1.5-flash` with another model:
```python
ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",  # More powerful but slower
    temperature=0,
    google_api_key=api_key
)
```

### Adjust Temperature

For more creative/varied outputs, increase temperature (0.0 to 1.0):
```python
ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,  # More creative
    google_api_key=api_key
)
```

## Production Deployment

For production use:

1. Use environment variables management (e.g., python-dotenv, AWS Secrets Manager)
2. Add authentication/authorization
3. Implement rate limiting
4. Add logging and monitoring
5. Use production ASGI server (Gunicorn + Uvicorn)
6. Set up HTTPS

## License

This project is for educational purposes as part of the AI/ML Assignment.

## Support

For issues or questions:
- Check the `/docs` endpoint for API documentation
- Review the error messages in the API response
- Verify your Google API key is valid and has quota available