import streamlit as st
import sys
import os
import time
from PIL import Image
import io

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.model_utils import generate_with_ollama, generate_with_openai, analyze_image_with_vision_model
from utils.logging_utils import setup_logger, log_user_action

# Set up logging
logger = setup_logger(__name__)

# Set page config
st.set_page_config(
    page_title="Interactive Brainstorming",
    page_icon="💭",
    layout="wide",
    initial_sidebar_state="expanded"
)

logger.debug("Brainstorming page loaded")

# Check if we have the required session state
required_states = [
    "model_type", "selected_model", "idea_description", 
    "uploaded_image", "plan_type"
]

missing_states = [state for state in required_states if state not in st.session_state or not st.session_state[state]]

if missing_states:
    logger.warning(f"Missing required session state variables: {missing_states}")
    st.error(f"Missing required information. Please go back and complete previous steps.")
    if st.button("Return to Idea Input"):
        log_user_action(logger, "navigate_back_to_idea_input", {"reason": "missing_states"})
        logger.info("User returning to idea input page due to missing information")
        st.switch_page("pages/2_idea_Input.py")
    st.stop()

# Initialize session states for this page
if "brainstorm_context" not in st.session_state:
    st.session_state.brainstorm_context = []
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "brainstorming_complete" not in st.session_state:
    st.session_state.brainstorming_complete = False
if "image_analysis" not in st.session_state:
    st.session_state.image_analysis = None

# Title and description
st.title("💭 Interactive Brainstorming")
st.markdown("""
The AI will ask a few clarifying questions to better understand your idea 
before generating an implementation plan. This helps create a more tailored
and actionable plan for your specific needs.
""")

logger.info("User viewing brainstorming page")

# Display idea information summary
st.subheader("Your Idea Summary")
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"**Description:** {st.session_state.idea_description}")
    st.markdown(f"**Plan Type:** {st.session_state.plan_type}")
    st.markdown(f"**Model:** {st.session_state.selected_model} ({st.session_state.model_type})")

with col2:
    if st.session_state.uploaded_image:
        try:
            image = Image.open(io.BytesIO(st.session_state.uploaded_image))
            st.image(image, caption="Your Idea Visualization", width=300)
        except Exception:
            st.error("Unable to display the image")

# Function to analyze the image if not already done
def analyze_image():
    if st.session_state.image_analysis is None and st.session_state.uploaded_image:
        logger.info("Starting image analysis process")
        with st.spinner("Analyzing your drawing..."):
            if st.session_state.model_type == "cloud":
                # For cloud models with vision capability
                model_to_use = st.session_state.selected_model if "vision" in st.session_state.selected_model else "gpt-4o"
                logger.info(f"Using vision-capable model for image analysis: {model_to_use}")
                
                prompt = f"""
                Analyze this drawing related to the following idea: {st.session_state.idea_description}
                Describe what you see in the drawing and how it relates to the idea.
                Focus on identifying key elements, layout, functionality, and features shown in the drawing.
                """
                
                logger.debug("Sending image to vision model for analysis")
                analysis = analyze_image_with_vision_model(
                    st.session_state.api_key,
                    st.session_state.image_base64,
                    prompt,
                    model=model_to_use
                )
                st.session_state.image_analysis = analysis
                logger.info("Image analysis completed successfully")
            else:
                # For local models without vision capability
                logger.info("Skipping image analysis - not available with local model")
                st.session_state.image_analysis = "Image analysis not available with the selected local model."
        
        return st.session_state.image_analysis
    return st.session_state.image_analysis

# Start the brainstorming if no context exists yet
if not st.session_state.brainstorm_context:
    logger.info("Starting new brainstorming session")
    
    # First analyze the image
    logger.debug("Calling image analysis function")
    image_analysis = analyze_image()
    
    # Generate initial question based on idea description and image analysis
    logger.info("Generating initial brainstorming questions")
    with st.spinner("Preparing initial questions based on your idea..."):
        if st.session_state.model_type == "local":
            prompt = f"""
            You are an AI assistant helping brainstorm and develop an implementation plan for a user's idea.
            User Idea: {st.session_state.idea_description}
            Plan Type: {st.session_state.plan_type}
            
            Image Description: {image_analysis}
            
            Ask 1-3 key clarifying questions to better understand the idea and create a more detailed implementation plan.
            Focus on understanding the scope, target audience, key features, constraints, or resources available.
            Format your response as a numbered list of questions, without any preamble or additional text.
            """
            response = generate_with_ollama(
                st.session_state.selected_model, 
                prompt,
                system_prompt="You are a helpful assistant that asks clear, specific questions to understand the user's idea for creating an implementation plan."
            )
        else:  # Cloud model
            messages = [
                {"role": "system", "content": "You are a helpful assistant that asks clear, specific questions to understand the user's idea for creating an implementation plan."},
                {"role": "user", "content": f"""
                I need help brainstorming and developing an implementation plan for my idea.
                
                Idea Description: {st.session_state.idea_description}
                Plan Type: {st.session_state.plan_type}
                
                Image Description: {image_analysis}
                
                Ask 1-3 key clarifying questions to better understand my idea and create a more detailed implementation plan.
                Focus on understanding the scope, target audience, key features, constraints, or resources available.
                Format your response as a numbered list of questions, without any preamble or additional text.
                """}
            ]
            response = generate_with_openai(
                st.session_state.selected_model,
                messages,
                st.session_state.api_key
            )
        
        st.session_state.current_question = response
        st.session_state.brainstorm_context.append({"role": "assistant", "content": response})

# Display the conversation history
if st.session_state.brainstorm_context:
    st.subheader("Brainstorming Session")
    for i, message in enumerate(st.session_state.brainstorm_context):
        if message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(message["content"])
        else:  # user
            with st.chat_message("user"):
                st.markdown(message["content"])

# If there's no current question but we have context, we're waiting for user input
if not st.session_state.current_question and st.session_state.brainstorm_context:
    # Generate next questions based on conversation history
    with st.spinner("Analyzing your responses..."):
        if st.session_state.model_type == "local":
            # Combine context into a prompt
            context = "\n".join([
                f"{'AI' if msg['role'] == 'assistant' else 'User'}: {msg['content']}"
                for msg in st.session_state.brainstorm_context
            ])
            prompt = f"""
            Based on our conversation so far about the user's idea:
            
            User Idea: {st.session_state.idea_description}
            Plan Type: {st.session_state.plan_type}
            Image Analysis: {st.session_state.image_analysis}
            
            Conversation History:
            {context}
            
            Ask 1-2 more questions to deepen understanding of the idea, or say "BRAINSTORMING_COMPLETE" 
            if you have enough information to generate an implementation plan.
            
            If asking questions, format as a numbered list without preamble. If complete, just return the exact word "BRAINSTORMING_COMPLETE".
            """
            response = generate_with_ollama(st.session_state.selected_model, prompt)
        else:  # Cloud model
            messages = [
                {"role": "system", "content": "You are a helpful assistant gathering information to create an implementation plan for the user's idea."},
                {"role": "user", "content": f"My idea: {st.session_state.idea_description}\nPlan Type: {st.session_state.plan_type}\nImage Analysis: {st.session_state.image_analysis}"}
            ]
            # Add the conversation history
            for msg in st.session_state.brainstorm_context:
                messages.append(msg)
            
            messages.append({
                "role": "user", 
                "content": "Based on our conversation so far, ask 1-2 more questions to deepen understanding of my idea, or say 'BRAINSTORMING_COMPLETE' if you have enough information to generate an implementation plan."
            })
            
            response = generate_with_openai(
                st.session_state.selected_model,
                messages,
                st.session_state.api_key
            )
        
        if "BRAINSTORMING_COMPLETE" in response:
            st.session_state.brainstorming_complete = True
        else:
            st.session_state.current_question = response
            st.session_state.brainstorm_context.append({"role": "assistant", "content": response})
            st.rerun()

# Input area for user response
if st.session_state.current_question:
    # Display current question
    st.markdown("### AI Assistant Question")
    st.info(st.session_state.current_question)
    logger.debug(f"Displaying question to user: {st.session_state.current_question[:50]}...")
    
    # Response input
    user_response = st.text_area(
        "Your Response:", 
        key="user_response",
        height=100,
        placeholder="Type your answer here..."
    )
    
    # Submit button
    if st.button("Submit Response"):
        log_user_action(logger, "submitted_brainstorm_response")
        logger.info("User submitted response to brainstorming question")
        if user_response:
            st.session_state.brainstorm_context.append({"role": "user", "content": user_response})
            st.session_state.current_question = None
            st.rerun()
        else:
            st.error("Please enter a response before submitting.")

# If brainstorming is complete, show a success message and next button
if st.session_state.brainstorming_complete:
    st.success("✅ Brainstorming complete! The AI has gathered enough information to generate your implementation plan.")
    if st.button("Generate My Implementation Plan 📋", type="primary"):
        st.session_state.current_step = "plan_generator"
        st.switch_page("pages/4_Plan_Generator.py")

# Navigation buttons at the bottom
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("◀️ Back to Idea Input"):
        log_user_action(logger, "navigate_back_to_idea_input")
        logger.info("User navigating back to idea input page")
        st.session_state.current_step = "idea_input"
        st.switch_page("pages/2_idea_Input.py")

with col3:
    if st.button("Done & Generate Plan ▶️", disabled=not st.session_state.brainstorming_complete, type="primary"):
        log_user_action(logger, "navigate_to_plan_generation")
        logger.info("User proceeding to plan generation page")
        st.session_state.current_step = "plan_generation"
        st.switch_page("pages/4_Plan_Generator.py")
