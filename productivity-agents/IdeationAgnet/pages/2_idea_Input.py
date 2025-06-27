import streamlit as st
import sys
import os
import base64
from PIL import Image
import io

# Add parent directory to path to import from utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logging_utils import setup_logger, log_user_action

# Set up logging
logger = setup_logger(__name__)

# Set page config
st.set_page_config(
    page_title="Describe Your Idea",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

logger.debug("Idea Input page loaded")

# Title and description
st.title("📝 Describe Your Idea")
st.markdown("""
Share your idea by providing a description, uploading a drawing or sketch, 
and selecting what type of implementation plan you need.
""")

logger.info("User viewing idea input page")

# Initialize session state if needed
if "idea_description" not in st.session_state:
    st.session_state.idea_description = ""
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "plan_type" not in st.session_state:
    st.session_state.plan_type = None
if "current_step" not in st.session_state:
    st.session_state.current_step = "idea_input"
if "image_base64" not in st.session_state:
    st.session_state.image_base64 = None

# Function to convert uploaded image to base64
def get_image_base64(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")

# Step 1: Idea Description
st.header("Step 1: Describe your idea")
idea_description = st.text_area(
    "Provide a clear and concise description of your idea:",
    value=st.session_state.idea_description,
    height=150,
    placeholder="Example: A mobile app that helps people track their daily water intake with reminders and visualizations of their progress..."
)

if idea_description:
    st.session_state.idea_description = idea_description

# Step 2: Upload a drawing or sketch
st.header("Step 2: Upload a drawing or sketch")
st.markdown("""
Upload a drawing, sketch, diagram, or any visual representation of your idea.
This can be a hand-drawn sketch, a digital mockup, or any image that helps illustrate your concept.
""")

uploaded_file = st.file_uploader(
    "Upload your drawing or sketch (JPG, PNG, or PDF)", 
    type=["jpg", "jpeg", "png", "pdf"]
)
    
# Plan type selection
plan_types = [
    "Software Development",
    "App Development",
    "Website Creation",
    "Business Plan",
    "Research Project",
    "Content Creation",
    "Marketing Campaign",
    "Product Design",
    "Educational Course",
    "Other (Please specify)"
]

plan_type = st.selectbox(
    "Select the type of plan you need:",
    options=plan_types,
    index=plan_types.index(st.session_state.plan_type) if st.session_state.plan_type in plan_types else 0
)

# Save and process form inputs
if st.button("Save Details"):
    log_user_action(logger, "save_idea_details")
    logger.info("User saving idea details")
    
    # Save idea description
    if idea_description:
        logger.debug(f"Saving idea description (length: {len(idea_description)} chars)")
        st.session_state.idea_description = idea_description

    # Process uploaded image if available
    if uploaded_file is not None:
        logger.info(f"Processing uploaded image: {uploaded_file.name}")
        # Store the image in session state
        image_bytes = uploaded_file.getvalue()
        st.session_state.uploaded_image = image_bytes
        st.session_state.image_base64 = get_image_base64(image_bytes)
        logger.debug(f"Image converted to base64 and saved to session state")
        
        st.success("Image uploaded successfully!")

    # Save plan type
    st.session_state.plan_type = plan_type
    logger.info(f"Plan type selected: {plan_type}")
    
    st.success("All details saved successfully!")

# Display the image if available
if st.session_state.uploaded_image is not None:
    try:
        logger.debug("Displaying uploaded image")
        image = Image.open(io.BytesIO(st.session_state.uploaded_image))
        st.image(image, caption="Your uploaded image", width=400)
    except Exception as e:
        logger.error(f"Error displaying image: {str(e)}")
        st.error(f"Error displaying image: {str(e)}")

    # If "Other" is selected, show a text field
    if plan_type == "Other (Please specify)":
        custom_plan_type = st.text_input(
            "Please specify the plan type:",
            value="" if st.session_state.plan_type == "Other (Please specify)" else st.session_state.plan_type
        )
        if custom_plan_type:
            logger.debug(f"Custom plan type specified: {custom_plan_type}")
            st.session_state.plan_type = custom_plan_type

# Validate inputs before proceeding
can_proceed = (
    st.session_state.idea_description.strip() != "" and
    st.session_state.uploaded_image is not None and
    st.session_state.plan_type is not None and
    st.session_state.plan_type != "Other (Please specify)"
)

# Navigation buttons
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("◀️ Back to Configuration"):
        log_user_action(logger, "navigate_back_to_configuration")
        logger.info("User navigating back to configuration page")
        st.session_state.current_step = "configuration"
        st.switch_page("pages/1_Configuration.py")

with col3:
    if st.button("Next: Brainstorming ▶️", disabled=not can_proceed, type="primary"):
        log_user_action(logger, "navigate_to_brainstorming")
        logger.info("User proceeding to brainstorming page")
        st.session_state.current_step = "brainstorming"
        st.switch_page("pages/3_Brainstorming.py")

if not can_proceed:
    logger.debug("Displaying requirements info message to user")
    st.info("""
    Please ensure you have:
    1. Provided an idea description
    2. Uploaded an image
    3. Selected a valid plan type
    """)
