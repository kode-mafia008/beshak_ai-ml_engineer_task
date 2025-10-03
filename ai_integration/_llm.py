import os
from typing import List, Any, Optional
from pydantic import Field
from dotenv import load_dotenv
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.prompts import PromptTemplate
from openai import OpenAI
import yaml

load_dotenv()

class OpenAILLM(LLM):
    model_name: str = Field(default="gpt-4o-mini")
    client: OpenAI = Field(default=None, exclude=True)
    temperature: float = Field(default=0.0)

    @property
    def _llm_type(self) -> str:
        return "openai_custom"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key: 
            raise RuntimeError("OPENAI_API_KEY not found in environment variables.")
        self.client = OpenAI(api_key=api_key)

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured information from insurance documents."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            stop=stop
        )
        return response.choices[0].message.content


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