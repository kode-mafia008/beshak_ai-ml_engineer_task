from dotenv import load_dotenv
import os
from typing import  List, Optional, Union
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableSequence
from .._llm import GeminiLLM, CustomPromptLoader

load_dotenv()

 
# Pydantic models (keeping the same as in your original code)
class InsurancePolicyData(BaseModel):
    """Structured output for insurance policy information"""
    name: Optional[str] = Field(description="Name of the policy holder")
    policy_number: Optional[str] = Field(description="Policy number")
    email: Optional[str] = Field(description="Email address")
    policy_name: Optional[str] = Field(description="Name of the insurance policy/plan")
    plan_type: Optional[str] = Field(description="Type of plan")
    sum_assured: Optional[str] = Field(description="Sum assured amount")
    room_rent_limit: Optional[str] = Field(description="Room rent limit")
    waiting_period: Optional[str] = Field(description="Waiting period")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "policy_number": "P/123456/01/2020/012345",
                "email": "john.doe@email.com",
                "policy_name": "Family Health Optima",
                "plan_type": "2A",
                "sum_assured": "Rs. 500000",
                "room_rent_limit": "Single Private AC",
                "waiting_period": "30 days"
            }
        }

 

class InsurancePDFProcessor:
    
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 model_name: str = "gemini-2.0-flash",
                 langsmith_api_key: Optional[str] = None,
                 prompt_repo: str = "insurance_pdf"):
        """
        Initialize the search mode system with LangChain and structured output
        
        Args:
            api_key: Google API key (optional, will use env var if not provided)
            model_name: Gemini model name to use
            langsmith_api_key: LangSmith API key (optional, will use env var if not provided)
            prompt_repo: LangSmith prompt repository name
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise RuntimeError("GOOGLE_API_KEY is required. Please set in environment variables.")
        
        # Store prompt_repo as instance variable
        self.prompt_repo = prompt_repo
        
        # Initialize Prompt Loader client
        self.prompt_client = CustomPromptLoader()
            
        # Initialize LangChain components
        self.llm = GeminiLLM(model_name=model_name)  
        
        # Set up Pydantic output parser
        self.output_parser = PydanticOutputParser(pydantic_object=InsurancePolicyData)
        
        # Load prompt template
        self.prompt_template = self._load_prompt_from_langsmith(prompt_repo)
         
        # Create the chain
        self.chain = RunnableSequence(self.prompt_template, self.llm, self.output_parser)
    
    def _load_prompt_from_langsmith(self, prompt_repo: str) -> Union[PromptTemplate, None]:
        """
        Load prompt from LangSmith hub or use fallback
        
        Args:
            prompt_repo: LangSmith prompt repository name
            
        Returns:
            PromptTemplate: Loaded or fallback prompt template
        """
        try:
            # Try to get prompt from custom loader
            prompt_template = self.prompt_client.get_prompt(prompt_repo,input_variables=["insurance_data", "format_instructions"])
            if prompt_template:
                return prompt_template
            # If the prompt_template is None, fall through to the fallback
        except Exception as e:
            raise RuntimeError(f"Failed to load prompt from LangSmith ({e}). Using fallback prompt.")
    
    def generate(self, document_text: str) -> InsurancePolicyData:
        """Generate insurance policy data based on name and location""" 

        response = self.chain.invoke({
            'document_text': document_text,
            'format_instructions': self.output_parser.get_format_instructions()
        })
        return response

 