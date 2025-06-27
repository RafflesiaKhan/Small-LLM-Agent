import streamlit as st
import sys
import os
import time
import base64
import json
from datetime import datetime
from PIL import Image
import io

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.model_utils import generate_with_ollama, generate_with_openai
from utils.logging_utils import setup_logger, log_user_action

# Set up logging
logger = setup_logger(__name__)

# Set page config
st.set_page_config(
    page_title="Implementation Plan Generator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

logger.debug("Plan Generator page loaded")

# Check for required session state
required_states = [
    "model_type", "selected_model", "idea_description", 
    "uploaded_image", "plan_type"
]

missing_states = [state for state in required_states if state not in st.session_state or not st.session_state[state]]

if missing_states:
    logger.warning(f"Missing required session states: {missing_states}")
    st.error(f"Missing required information. Please go back and complete previous steps.")
    if st.button("Return to Idea Input"):
        log_user_action(logger, "navigate_back_to_idea_input", {"reason": "missing_states"})
        logger.info("User returning to idea input page due to missing information")
        st.switch_page("pages/2_idea_Input.py")
    st.stop()

# Initialize session states for this page
if "generated_plan" not in st.session_state:
    st.session_state.generated_plan = ""
if "feedback_history" not in st.session_state:
    st.session_state.feedback_history = []
if "plan_iteration" not in st.session_state:
    st.session_state.plan_iteration = 0
if "current_step" not in st.session_state:
    st.session_state.current_step = "plan_generator"
if "image_analysis" not in st.session_state:
    st.session_state.image_analysis = None
if "generation_complete" not in st.session_state:
    st.session_state.generation_complete = False

# Title and description
st.title("📋 Implementation Plan Generator")
st.markdown("""
Generate a detailed implementation plan for your idea. You can provide feedback
and regenerate the plan to make it more tailored to your needs.
""")
logger.info("User viewing plan generator page")

# Function to create a downloadable link for the plan
def get_download_link(plan_text, filename="implementation_plan.md"):
    """Generate a link to download the plan as a markdown file"""
    logger.debug(f"Creating download link for plan, filename: {filename}")
    b64 = base64.b64encode(plan_text.encode()).decode()
    href = f'<a href="data:file/markdown;base64,{b64}" download="{filename}" onclick="logDownload()">Download Plan as Markdown</a>'
    # Add JavaScript to log download action
    js = f"""
    <script>
    function logDownload() {{
        const data = new FormData();
        data.append('action', 'download_plan');
        data.append('filename', '{filename}');
        navigator.sendBeacon('/log_action', data);
        console.log('Plan download logged');
    }}
    </script>
    """
    return js + href

# Function to generate the implementation plan
def generate_plan():
    logger.info(f"Starting plan generation (iteration {st.session_state.plan_iteration + 1})")
    with st.spinner("Generating your implementation plan... This may take a minute."):
        # Prepare conversation context from brainstorming if available
        context = ""
        if "brainstorm_context" in st.session_state and st.session_state.brainstorm_context:
            logger.debug(f"Including {len(st.session_state.brainstorm_context)} brainstorming exchanges in context")
            context = "\n".join([
                f"{'AI' if msg['role'] == 'assistant' else 'User'}: {msg['content']}"
                for msg in st.session_state.brainstorm_context
            ])
        
        # Get image analysis if available
        image_analysis = st.session_state.image_analysis if st.session_state.image_analysis else "No image analysis available."
        
        # Feedback context if this is not the first iteration
        feedback_context = ""
        if st.session_state.feedback_history:
            feedback_context = "\nPrevious feedback:\n" + "\n".join([
                f"- {feedback}" for feedback in st.session_state.feedback_history
            ])
        
        # Generate plan based on the model type
        logger.info(f"Generating plan using {st.session_state.model_type} model: {st.session_state.selected_model}")
        if st.session_state.model_type == "local":
            # For local Ollama models
            prompt = f"""
            Create a detailed implementation plan for the following idea:
            
            IDEA DESCRIPTION: {st.session_state.idea_description}
            
            PLAN TYPE: {st.session_state.plan_type}
            
            IMAGE ANALYSIS: {image_analysis}
            
            ADDITIONAL CONTEXT FROM BRAINSTORMING:
            {context}
            {feedback_context}
            
            Generate a comprehensive implementation plan with the following sections:
            1. Executive Summary - A brief overview of the idea and implementation approach
            2. Project Scope - Define what's included and not included
            3. Key Features and Components - Detailed breakdown of all major components
            4. Implementation Timeline - Phases of development with estimated timeframes
            5. Required Resources - People, technologies, tools, and costs
            6. Success Metrics - How to measure the implementation's success
            7. Potential Challenges and Mitigations - Identify risks and how to address them
            8. Next Steps - Immediate actions to get started
            
            Format the plan in Markdown with clear headers, bullet points, and sections. Be specific, actionable, and thorough.
            """
            
            system_prompt = """
            You are an expert implementation planner specializing in turning ideas into actionable plans.
            Your plans are comprehensive, well-structured, and tailored to the specific type of project.
            Provide detailed, practical guidance that someone could follow to implement the idea.
            Format your response in clean Markdown with clear sections and bullet points.
            """
            
            plan = generate_with_ollama(
                st.session_state.selected_model, 
                prompt,
                system_prompt=system_prompt
            )
        else:
            # For cloud-based models (OpenAI)
            messages = [
                {
                    "role": "system", 
                    "content": "You are an expert implementation planner specializing in turning ideas into actionable plans. Your plans are comprehensive, well-structured, and tailored to the specific type of project. Provide detailed, practical guidance that someone could follow to implement the idea. Format your response in clean Markdown with clear sections and bullet points."
                },
                {
                    "role": "user", 
                    "content": f"""
                    Create a detailed implementation plan for the following idea:
                    
                    IDEA DESCRIPTION: {st.session_state.idea_description}
                    
                    PLAN TYPE: {st.session_state.plan_type}
                    
                    IMAGE ANALYSIS: {image_analysis}
                    
                    ADDITIONAL CONTEXT FROM BRAINSTORMING:
                    {context}
                    {feedback_context}
                    
                    Generate a comprehensive implementation plan with the following sections:
                    1. Executive Summary - A brief overview of the idea and implementation approach
                    2. Project Scope - Define what's included and not included
                    3. Key Features and Components - Detailed breakdown of all major components
                    4. Implementation Timeline - Phases of development with estimated timeframes
                    5. Required Resources - People, technologies, tools, and costs
                    6. Success Metrics - How to measure the implementation's success
                    7. Potential Challenges and Mitigations - Identify risks and how to address them
                    8. Next Steps - Immediate actions to get started
                    
                    Format the plan in Markdown with clear headers, bullet points, and sections. Be specific, actionable, and thorough.
                    """
                }
            ]
            
            plan = generate_with_openai(
                st.session_state.selected_model,
                messages,
                st.session_state.api_key
            )
        
        # Increment plan iteration counter
        st.session_state.plan_iteration += 1
        
        # Store the generated plan
        st.session_state.generated_plan = plan
        st.session_state.generation_complete = True
        
        logger.info(f"Plan generation completed successfully (length: {len(plan)} chars)")
        return plan

# Display idea summary
st.subheader("Your Idea Summary")
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown(f"**Description:** {st.session_state.idea_description}")
    st.markdown(f"**Plan Type:** {st.session_state.plan_type}")
    if "brainstorm_context" in st.session_state and len(st.session_state.brainstorm_context) > 0:
        st.markdown(f"**Brainstorming:** {len(st.session_state.brainstorm_context) // 2} question-answer pairs")

with col2:
    if st.session_state.uploaded_image:
        try:
            image = Image.open(io.BytesIO(st.session_state.uploaded_image))
            st.image(image, caption="Your Idea Visualization", width=250)
        except Exception:
            st.error("Unable to display the image")

# Generate plan if not yet generated
if not st.session_state.generated_plan:
    if st.button("Generate Implementation Plan", type="primary"):
        log_user_action(logger, "initiate_plan_generation")
        logger.info("User initiated plan generation")
        generated_plan = generate_plan()
        st.rerun()

# If plan is generated, display it
if st.session_state.generated_plan and st.session_state.generation_complete:
    st.header(f"Your Implementation Plan (Iteration {st.session_state.plan_iteration})")
    
    # Display the generated plan content
    st.markdown(st.session_state.generated_plan)
    
    # Add download link
    if st.session_state.generated_plan:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"implementation_plan_{timestamp}.md"
        st.markdown(get_download_link(st.session_state.generated_plan, filename), unsafe_allow_html=True)
    
# Handle feedback form if user selected "Needs Improvement"
if "current_feedback" in st.session_state and st.session_state.current_feedback:
    st.subheader("Please provide specific feedback")
    feedback = st.text_area(
        "What aspects of the plan would you like to improve?",
        placeholder="E.g., 'The timeline is too vague', 'Need more detail on resources', 'Missing key features'..."
    )
    
    if st.button("Submit Feedback & Regenerate Plan", type="primary"):
        if feedback:
            log_user_action(logger, "submitted_plan_feedback", {"feedback_length": len(feedback)})
            logger.info(f"User submitted feedback for plan iteration {st.session_state.plan_iteration}")
            
            # Store the feedback
            st.session_state.feedback_history.append(feedback)
            logger.debug(f"Added feedback to history (now {len(st.session_state.feedback_history)} feedback items)")
            
            # Clear the current plan to trigger regeneration
            st.session_state.generated_plan = ""
            st.session_state.generation_complete = False
            
            st.success("Feedback recorded! Regenerating plan...")
            st.rerun()
        else:
            st.error("Please provide feedback before submitting.")

# Feedback and regeneration section
st.markdown("---")
st.subheader("Feedback and Regeneration")
st.markdown("If you'd like to modify the plan, provide specific feedback below and regenerate it.")

feedback = st.text_area(
    "What would you like to change or improve about this plan?",
    placeholder="Example: Add more detail about the budget, focus less on marketing, include more technical specifications, etc.",
    height=100
)

if st.button("Regenerate Plan with Feedback", disabled=not st.session_state.generation_complete):
    if feedback.strip():
        log_user_action(logger, "submitted_plan_feedback", {"feedback_length": len(feedback)})
        logger.info(f"User submitted feedback for plan iteration {st.session_state.plan_iteration}")
        
        # Store the feedback
        st.session_state.feedback_history.append(feedback)
        logger.debug(f"Added feedback to history (now {len(st.session_state.feedback_history)} feedback items)")
        
        # Clear the current plan to trigger regeneration
        st.session_state.generated_plan = ""
        st.session_state.generation_complete = False
        
        st.success("Feedback recorded! Regenerating plan...")
        st.rerun()
    else:
        st.error("Please provide feedback before submitting.")

# Navigation buttons
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("◀️ Back to Brainstorming"):
        log_user_action(logger, "navigate_back_to_brainstorming")
        logger.info("User navigating back to brainstorming page")
        st.session_state.current_step = "brainstorming"
        st.switch_page("pages/3_Brainstorming.py")

with col3:
    if st.button("Save to History ▶️", disabled=not st.session_state.generation_complete, type="primary"):
        log_user_action(logger, "save_plan_to_history")
        logger.info("User saving plan to history")
        
        if "plan_history" not in st.session_state:
            st.session_state.plan_history = []
        
        # Save the current plan to history with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        plan_entry = {
            "timestamp": timestamp,
            "idea": st.session_state.idea_description,
            "plan_type": st.session_state.plan_type,
            "plan": st.session_state.generated_plan,
            "iteration": st.session_state.plan_iteration
        }
        
        st.session_state.plan_history.append(plan_entry)
        logger.debug(f"Plan saved to history (now {len(st.session_state.plan_history)} plans in history)")
        
        st.session_state.current_step = "history"
        st.switch_page("pages/5_History.py")
