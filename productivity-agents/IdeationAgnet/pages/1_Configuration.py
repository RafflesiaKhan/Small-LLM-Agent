import streamlit as st
import sys
import os

# Add parent directory to path to import from utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.model_utils import (
    get_available_ollama_models, 
    test_ollama_connection, 
    get_available_cloud_models,
    test_openai_connection
)
from utils.logging_utils import setup_logger, log_user_action

# Set up logging
logger = setup_logger(__name__)

# Set page config
st.set_page_config(
    page_title="Model Configuration",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

logger.debug("Configuration page loaded")

# Title and description
st.title("⚙️ Model Configuration")
st.markdown("""
Choose the AI model that will help generate your implementation plan. 
You can select a local model (Ollama) or a cloud-based model (OpenAI, Claude, etc.).
""")

logger.info("User viewing configuration page")

# Initialize session state variables if they don't exist
if "model_type" not in st.session_state:
    st.session_state.model_type = None
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "model_status" not in st.session_state:
    st.session_state.model_status = None
if "current_step" not in st.session_state:
    st.session_state.current_step = "configuration"

# Model selection section
st.header("Model Selection")

# Create two columns for the model type selection
col1, col2 = st.columns(2)

with col1:
    st.info("**Local Model (Ollama)**\n\nRuns on your computer. Offers privacy and zero cost, but may be less powerful.")
    if st.button("Use Local Model", use_container_width=True):
        log_user_action(logger, "selected_local_model")
        logger.info("User selected local model type")
        st.session_state.model_type = "local"
        # Reset other model-related state
        st.session_state.selected_model = None
        st.session_state.api_key = None
        st.session_state.model_status = None
        st.rerun()

with col2:
    st.info("**Cloud Model (OpenAI, Claude, etc.)**\n\nMore powerful, but requires API key and internet connection.")
    if st.button("Use Cloud Model", use_container_width=True):
        log_user_action(logger, "selected_cloud_model")
        logger.info("User selected cloud model type")
        st.session_state.model_type = "cloud"
        # Reset other model-related state
        st.session_state.selected_model = None
        st.session_state.api_key = None
        st.session_state.model_status = None
        st.rerun()

# Display configuration based on selected model type
if st.session_state.model_type == "local":
    st.subheader("Local Ollama Model Configuration")
    
    def check_ollama_models():
        """Check for available Ollama models"""
        logger.info("Checking for available Ollama models")
        with st.spinner("Checking for available Ollama models..."):
            available_models = get_available_ollama_models()
            st.session_state.available_ollama_models = available_models
            return available_models
    
    if not st.session_state.available_ollama_models:
        check_ollama_models()
    
    if not st.session_state.available_ollama_models:
        st.error("""
        Could not connect to Ollama server. Please ensure:
        1. Ollama is installed (https://ollama.ai)
        2. Ollama app is running
        3. Server is listening on localhost:11434
        """)
        if st.button("Retry Connection Check"):
            st.rerun()
    else:
        # Show dropdown to select a model
        st.success(f"Found {len(st.session_state.available_ollama_models)} available Ollama models")
        
        def handle_ollama_selection():
            """Handle local Ollama model selection"""
            st.session_state.selected_model = st.selectbox(
                "Select an Ollama model:",
                st.session_state.available_ollama_models,
                index=0 if st.session_state.available_ollama_models else None
            )
            
            if st.session_state.selected_model:
                logger.info(f"User selected Ollama model: {st.session_state.selected_model}")
            
            if st.session_state.selected_model and st.button("Test Connection"):
                log_user_action(logger, "test_ollama_connection", {"model": st.session_state.selected_model})
                with st.spinner(f"Testing connection to {st.session_state.selected_model}..."):
                    logger.info(f"Testing connection to Ollama model: {st.session_state.selected_model}")
                    is_connected = test_ollama_connection(st.session_state.selected_model)
                    if is_connected:
                        st.session_state.model_status = "success"
                        st.success("✅ Connection successful! Model is ready to use.")
                    else:
                        st.session_state.model_status = "error"
                        st.error("❌ Could not connect to the model. Make sure it's properly loaded in Ollama.")
        
        handle_ollama_selection()

elif st.session_state.model_type == "cloud":
    st.subheader("Cloud Model Configuration")
    
    def handle_cloud_selection():
        """Handle cloud-based model selection"""
        cloud_models = get_available_cloud_models()
        logger.debug(f"Loaded {len(cloud_models)} cloud models for selection")
        
        st.session_state.selected_model = st.selectbox(
            "Select a cloud model:",
            cloud_models
        )
        
        if st.session_state.selected_model:
            logger.info(f"User selected cloud model: {st.session_state.selected_model}")
        
        # API key input
        api_key = st.text_input("Enter your API Key:", type="password", value=st.session_state.api_key if st.session_state.api_key else "")
        
        if api_key:
            st.session_state.api_key = api_key
            logger.debug("API key updated")
        
        if st.session_state.api_key and st.button("Verify API Key"):
            log_user_action(logger, "verify_api_key", {"model": st.session_state.selected_model})
            with st.spinner("Verifying API Key..."):
                logger.info("Verifying OpenAI API key")
                is_valid = test_openai_connection(st.session_state.api_key)
                if is_valid:
                    st.session_state.model_status = "success"
                    st.success("✅ API key verified! Model is ready to use.")
                else:
                    st.session_state.model_status = "error"
                    st.error("❌ Invalid API key or connection error. Please check and try again.")
    
    handle_cloud_selection()

# Navigation buttons
st.markdown("---")

# Back button for navigation
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("◀️ Back to Home"):
        st.session_state.current_step = "home"
        st.switch_page("Home.py")

# Continue button - only enabled if model is selected and verified
with col3:
    # Display the next button if a model is selected and validated
    if st.session_state.model_status == "success":
        if st.button("Next: Define Your Idea", type="primary"):
            log_user_action(logger, "navigation_to_idea_input")
            logger.info("User proceeding to Idea Input page")
            st.session_state.current_step = "idea_input"
            st.switch_page("pages/2_idea_Input.py")

if st.session_state.model_type is not None and st.session_state.model_status != "success":
    st.info("Please select and verify a model before continuing.")
