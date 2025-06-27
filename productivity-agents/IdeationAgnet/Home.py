import streamlit as st
import os
import sys
from PIL import Image
import base64

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import logging utilities
from utils.logging_utils import setup_logger, log_user_action

# Set up logging
logger = setup_logger(__name__)
logger.info("Starting Idea-to-Plan Generator application")

# Set page configuration
st.set_page_config(
    page_title="Idea-to-Plan Generator",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)
logger.debug("Streamlit page configuration set")

# Initialize session state variables if they don't exist
if "model_type" not in st.session_state:
    st.session_state.model_type = None
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "idea_description" not in st.session_state:
    st.session_state.idea_description = ""
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "plan_type" not in st.session_state:
    st.session_state.plan_type = None
if "brainstorm_context" not in st.session_state:
    st.session_state.brainstorm_context = []
if "generated_plan" not in st.session_state:
    st.session_state.generated_plan = ""
if "feedback_history" not in st.session_state:
    st.session_state.feedback_history = []
if "current_step" not in st.session_state:
    st.session_state.current_step = "home"

# Title and description
st.title("💡 Idea-to-Plan Generator")
st.markdown("""
Transform your rough ideas into structured implementation plans with the help of AI.
Upload a drawing, describe your idea, and get a detailed plan across various domains.
""")

# Create a two-column layout
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("How It Works")
    st.markdown("""
    1. **Select an AI Model** - Choose between local Ollama models or cloud-based LLMs
    2. **Describe Your Idea** - Provide a clear description of what you want to create
    3. **Upload a Drawing** - Share a sketch, diagram, or visualization of your concept
    4. **Select Plan Type** - Specify what kind of plan you need (Development, Business, etc.)
    5. **Interactive Refinement** - Work with the AI to clarify and improve your plan
    6. **Get Your Plan** - Receive a structured, actionable implementation roadmap
    """)
    
    # Get started button
    if st.button("Get Started", type="primary", use_container_width=True):
        log_user_action(logger, "clicked_get_started")
        st.session_state.current_step = "configuration"
        logger.info("Navigating to Configuration page")
        st.switch_page("pages/1_Configuration.py")

with col2:
    # Display an example image or icon
    st.image("https://via.placeholder.com/400x300.png?text=Idea+to+Plan+Generator", 
             caption="Transform your ideas into actionable plans",
             use_column_width=True)
    
    st.subheader("Benefits")
    st.markdown("""
    - **Save Time** - Get structured plans in minutes, not hours
    - **Improve Clarity** - Transform vague ideas into concrete steps
    - **Enhance Collaboration** - Share clear plans with teams or stakeholders
    - **Flexible Domains** - Works for software, content, business, research and more
    """)

# Add a footer
st.markdown("---")
st.markdown("© 2025 Idea-to-Plan Generator | Powered by AI")
