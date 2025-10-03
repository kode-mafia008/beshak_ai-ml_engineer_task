import os
from typing import List, Any, Optional
from pydantic import Field
from dotenv import load_dotenv
from langchain_core.language_models.llms import LLM
from google.generativeai import GenerativeModel
from google import generativeai as genai
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.prompts import PromptTemplate
import yaml

load_dotenv()

class GeminiLLM(LLM):
    model_name: str = Field(default="gemini-2.0-flash")
    model: GenerativeModel = Field(default=None, exclude=True)

    @property
    def _llm_type(self) -> str:
        return "gemini_custom"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key: 
            raise RuntimeError("GOOGLE_API_KEY not found in environment variables.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        response = self.model.generate_content(prompt)
        return response.text if hasattr(response, 'text') else response.parts[0].text



# Custom Prompt Loader class
class CustomPromptLoader:
    def __init__(self):
        self.base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prompts')
    
    def get_prompt(self, name: str, input_variables: List[str]) -> PromptTemplate:
        """Load prompt from YAML file and return as PromptTemplate"""
        prompt_path = os.path.join(self.base_path, f'{name}.yaml') 
        
        # Try to load from file if it exists
        if os.path.exists(prompt_path):
            try:
                with open(prompt_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Try to parse as YAML first
                try:
                    yaml_data = yaml.safe_load(content)
                    if isinstance(yaml_data, dict) and 'template' in yaml_data:
                        template_text = yaml_data['template']
                    else:
                        # If not structured YAML, use raw content
                        template_text = content
                except yaml.YAMLError:
                    # If YAML parsing fails, use raw content
                    template_text = content
                
                # Create PromptTemplate with expected input variables
                return PromptTemplate(
                    template=template_text,
                    input_variables=input_variables
                )
            except Exception as e:
                raise RuntimeError(f"Error loading prompt from {prompt_path}: {e}")
        
 
    
 