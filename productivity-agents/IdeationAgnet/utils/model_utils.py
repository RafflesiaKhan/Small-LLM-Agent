import requests
import json
import os
import sys
import openai
from dotenv import load_dotenv
import time

# Add parent directory to path for direct imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 
from utils.logging_utils import get_logger, log_api_request, log_api_response, log_error, log_function_call, log_function_return

# Set up logger for this module
logger = get_logger(__name__)

# Load environment variables
load_dotenv()
logger.debug("Environment variables loaded")

def get_available_ollama_models():
    """
    Check for available Ollama models on localhost:11434
    Returns a list of model names or empty list if Ollama is not running
    """
    log_function_call(logger, "get_available_ollama_models")
    try:
        log_api_request(logger, "http://localhost:11434/api/tags")
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        log_api_response(logger, "http://localhost:11434/api/tags", response.status_code)
        
        if response.status_code == 200:
            models = response.json()
            model_list = [model["name"] for model in models["models"]]
            logger.info(f"Found {len(model_list)} available Ollama models")
            log_function_return(logger, "get_available_ollama_models", model_list)
            return model_list
        logger.warning(f"Failed to get Ollama models: status code {response.status_code}")
        log_function_return(logger, "get_available_ollama_models", [])
        return []
    except requests.exceptions.RequestException as e:
        log_error(logger, e, "Failed to connect to Ollama server")
        log_function_return(logger, "get_available_ollama_models", [])
        return []

def test_ollama_connection(model_name):
    """
    Test if connection to Ollama is working with the specified model
    """
    log_function_call(logger, "test_ollama_connection", args=[model_name])
    try:
        request_data = {"model": model_name, "prompt": "Hello", "stream": False}
        log_api_request(logger, "http://localhost:11434/api/generate", params=request_data)
        start_time = time.time()
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=request_data,
            timeout=5
        )
        elapsed_time = time.time() - start_time
        log_api_response(logger, "http://localhost:11434/api/generate", response.status_code)
        logger.debug(f"Ollama response time: {elapsed_time:.2f}s")
        
        success = response.status_code == 200
        log_function_return(logger, "test_ollama_connection", success)
        return success
    except requests.exceptions.RequestException as e:
        log_error(logger, e, f"Connection test failed for model {model_name}")
        log_function_return(logger, "test_ollama_connection", False)
        return False

def get_available_cloud_models():
    """
    Return a list of available cloud-based LLM models
    """
    return [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "claude-3-opus",
        "claude-3-sonnet",
        "claude-3-haiku",
        "gemini-1.5-pro",
        "gemini-1.0-pro"
    ]

def test_openai_connection(api_key):
    """
    Test if OpenAI API connection works with the provided key
    """
    log_function_call(logger, "test_openai_connection")
    try:
        logger.debug("Testing OpenAI API connection")
        # Create a fresh client instance without any proxy settings
        client = openai.OpenAI(api_key=api_key)
        start_time = time.time()
        log_api_request(logger, "OpenAI chat.completions")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        elapsed_time = time.time() - start_time
        logger.debug(f"OpenAI response time: {elapsed_time:.2f}s")
        log_api_response(logger, "OpenAI chat.completions", 200, "Connection successful")
        log_function_return(logger, "test_openai_connection", True)
        return True
    except Exception as e:
        log_error(logger, e, "OpenAI connection test failed")
        log_function_return(logger, "test_openai_connection", False)
        return False

def generate_with_ollama(model, prompt, system_prompt=None):
    """
    Generate response using local Ollama model
    """
    log_function_call(logger, "generate_with_ollama", args=[model], kwargs={"system_prompt": system_prompt is not None})
    prompt_short = prompt[:50] + "..." if len(prompt) > 50 else prompt
    logger.info(f"Generating with Ollama model: {model}, prompt: {prompt_short}")
    
    try:
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            data["system"] = system_prompt
            logger.debug("Using system prompt with Ollama")
            
        log_api_request(logger, "http://localhost:11434/api/generate")
        start_time = time.time()
        response = requests.post("http://localhost:11434/api/generate", json=data)
        elapsed_time = time.time() - start_time
        logger.debug(f"Ollama generation time: {elapsed_time:.2f}s")
        log_api_response(logger, "http://localhost:11434/api/generate", response.status_code)
        
        if response.status_code == 200:
            result = response.json().get("response", "")
            result_short = result[:50] + "..." if len(result) > 50 else result
            logger.info(f"Ollama generation successful: {result_short}")
            log_function_return(logger, "generate_with_ollama", "<response_content>")
            return result
        
        error_msg = f"Error: {response.status_code}"
        log_error(logger, error_msg, "Ollama API error")
        log_function_return(logger, "generate_with_ollama", error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        log_error(logger, e, "Exception in generate_with_ollama")
        log_function_return(logger, "generate_with_ollama", error_msg)
        return error_msg

def generate_with_openai(model, messages, api_key):
    """
    Generate response using OpenAI API
    """
    log_function_call(logger, "generate_with_openai", args=[model])
    last_msg = messages[-1]["content"] if messages else "<no message>"
    last_msg_short = last_msg[:50] + "..." if len(last_msg) > 50 else last_msg
    logger.info(f"Generating with OpenAI model: {model}, last message: {last_msg_short}")
    
    try:
        # Create a fresh client instance with the API key
        client = openai.OpenAI(api_key=api_key)
        log_api_request(logger, f"OpenAI chat.completions with model {model}")
        start_time = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=2000
        )
        elapsed_time = time.time() - start_time
        logger.debug(f"OpenAI generation time: {elapsed_time:.2f}s")
        log_api_response(logger, "OpenAI chat.completions", 200)
        
        result = response.choices[0].message.content
        result_short = result[:50] + "..." if len(result) > 50 else result
        logger.info(f"OpenAI generation successful: {result_short}")
        log_function_return(logger, "generate_with_openai", "<response_content>")
        return result
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        log_error(logger, e, f"Exception in generate_with_openai with model {model}")
        log_function_return(logger, "generate_with_openai", error_msg)
        return error_msg

def analyze_image_with_vision_model(api_key, image_data, prompt, model="gpt-4o"):
    """
    Analyze an image using a vision-capable model
    """
    log_function_call(logger, "analyze_image_with_vision_model", args=[model])
    prompt_short = prompt[:50] + "..." if len(prompt) > 50 else prompt
    logger.info(f"Analyzing image with vision model: {model}, prompt: {prompt_short}")
    
    try:
        # Create a fresh client instance with the API key
        client = openai.OpenAI(api_key=api_key)
        logger.debug("Converting image data for analysis")
        
        # Convert image data to base64 if it's not already
        if isinstance(image_data, bytes):
            import base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            logger.debug("Converted raw bytes to base64 encoding")
        else:
            image_base64 = image_data
            logger.debug("Using provided base64 image data")
        
        log_api_request(logger, f"OpenAI chat.completions with vision model {model}")
        start_time = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        elapsed_time = time.time() - start_time
        logger.debug(f"Vision analysis time: {elapsed_time:.2f}s")
        log_api_response(logger, "OpenAI chat.completions vision", 200)
        
        result = response.choices[0].message.content
        result_short = result[:50] + "..." if len(result) > 50 else result
        logger.info(f"Image analysis successful: {result_short}")
        log_function_return(logger, "analyze_image_with_vision_model", "<image_analysis_content>")
        return result
    except Exception as e:
        error_msg = f"Error analyzing image: {str(e)}"
        log_error(logger, e, f"Exception in analyze_image_with_vision_model with model {model}")
        log_function_return(logger, "analyze_image_with_vision_model", error_msg)
        return error_msg
