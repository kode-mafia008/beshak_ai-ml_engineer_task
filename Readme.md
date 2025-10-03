# Insurance Document Data Extraction API

FastAPI application that extracts structured data from insurance policy documents using **Mistral AI OCR** + **OpenAI**.

## Features

- Two-stage pipeline: Mistral AI (document parsing) → OpenAI (data extraction)
- Supports: PDF, DOC, DOCX, TXT, PNG, JPG, JPEG (up to 50MB, 1,000 pages)
- Intelligent extraction of 8 fields with contextual inference and legal compliance checks
- Handles label variations across different insurance companies

## Extracted Fields

1. **Name** - Policy holder name
2. **Policy Number** - Unique policy identifier
3. **Email** - Contact email address
4. **Policy Name** - Insurance product name (clean, without codes)
5. **Plan Type** - Plan code/category (e.g., SHAHLIP21211V042021 or "Family")
6. **Sum Assured** - Coverage amount
7. **Room Rent Limit** - Maximum room rent per day (with IRDAI inference if applicable)
8. **Waiting Period** - Initial or pre-existing disease waiting period (with IRDAI inference if applicable)

## Setup

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env`:

```
MISTRAL_API_KEY=your_mistral_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

Get your keys:

- Mistral AI: https://console.mistral.ai/api-keys
- OpenAI: https://platform.openai.com/api-keys

### 3. Run

**Development:**

```bash
fastapi dev app.py
```

**Production:**

```bash
fastapi run app.py
```

API: `http://localhost:8000` | Docs: `http://localhost:8000/docs`

## Usage

### Extract Data

**cURL:**

```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@insurance_policy.pdf"
```

**Python:**

```python
import requests

response = requests.post(
    "http://localhost:8000/extract",
    files={"file": open("insurance_policy.pdf", "rb")}
)
print(response.json())
```

**Response:**

```json
{
  "name": "John Doe",
  "policy_number": "POL123456",
  "email": "john.doe@example.com",
  "policy_name": "Health Plus Premium",
  "plan_type": "SHAHLIP21211V042021",
  "sum_assured": "500000",
  "room_rent_limit": "5000 per day",
  "waiting_period": "30 days"
}
```

## Architecture

### Process Flow

```
Document Upload → Mistral OCR → OpenAI Extraction → JSON Response
```

1. Mistral AI (`mistral-ocr-latest`) extracts markdown text from documents
2. OpenAI (`gpt-4o-mini`) extracts structured data with contextual inference
3. Returns JSON with 8 fields (null if not found)

### Project Structure

```
├── app.py                  # FastAPI application
├── config.py               # Settings (API keys)
├── models.py               # Response models
├── mistral_parser.py       # Mistral OCR integration
├── openai_extractor.py     # OpenAI extraction with smart prompts
├── requirements.txt        # Dependencies
└── .env.example           # Environment template
```

### Key Features

- **Contextual Inference**: Extracts plan_type from policy_name if not labeled separately
- **Legal Compliance**: Infers room_rent_limit and waiting_period based on IRDAI regulations (only when document references compliance and 100% certain)
- **Smart Parsing**: Separates clean policy names from plan codes
- **Error Handling**: Returns null for missing fields, proper HTTP error codes
