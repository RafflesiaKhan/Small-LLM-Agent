import streamlit as st
import sys
import os
import time
import json
import base64
from datetime import datetime
from PIL import Image
import io

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logging_utils import setup_logger, log_user_action

# Set up logging
logger = setup_logger(__name__)

# Set page config
st.set_page_config(
    page_title="Plan History",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

logger.debug("History page loaded")

st.title("📚 Plan History")
st.markdown("View and download your previously generated implementation plans.")

logger.info("User viewing plan history page")

# Create plans directory if it doesn't exist
plans_dir = "plans"
os.makedirs(plans_dir, exist_ok=True)

# Load available plans
def load_plans():
    logger.debug("Loading saved plans from file system")
    plans = []
    try:
        for filename in os.listdir(plans_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(plans_dir, filename), "r") as f:
                        plan_data = json.load(f)
                        # Add the filename to the data for reference
                        plan_data["filename"] = filename
                        plans.append(plan_data)
                except (json.JSONDecodeError, IOError) as e:
                    error_msg = f"Error loading plan {filename}: {str(e)}"
                    logger.error(error_msg)
                    st.error(error_msg)
    except Exception as e:
        error_msg = f"Error accessing plans directory: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
    
    # Sort plans by timestamp (newest first)
    plans.sort(key=lambda x: datetime.strptime(x.get("timestamp", "1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S"), reverse=True)
    logger.info(f"Loaded {len(plans)} plans from storage")
    return plans

plans = load_plans()

# Function to create a downloadable link for the plan
def get_download_link(plan_text, filename="implementation_plan.md"):
    """Generate a link to download the plan as a markdown file"""
    logger.debug(f"Creating download link for plan, filename: {filename}")
    b64 = base64.b64encode(plan_text.encode()).decode()
    href = f'<a href="data:file/markdown;base64,{b64}" download="{filename}" onclick="logPlanDownload(\'{filename}\')">Download Plan as Markdown</a>'
    
    # Add JavaScript to log download action
    js = f"""
    <script>
    function logPlanDownload(filename) {{
        console.log('Plan download: ' + filename);
        // Could add analytics tracking here
    }}
    </script>
    """
    
    return js + href

# Display available plans
if plans:
    st.subheader(f"You have {len(plans)} saved plans")
    
    # Create sidebar with plan selection
    with st.sidebar:
        st.header("Select a Plan")
        selected_plan_idx = st.radio(
            "Choose a plan to view:",
            range(len(plans)),
            format_func=lambda i: f"{plans[i].get('timestamp', 'Unknown date')} - {plans[i].get('idea_description', 'Unknown idea')[:50]}..."
        )
        
    # Log the plan selection
    selected_plan = plans[selected_plan_idx]
    log_user_action(logger, "viewed_history_plan", {
        "plan_id": selected_plan.get("filename", "unknown"),
        "timestamp": selected_plan.get("timestamp", "unknown")
    })
    logger.info(f"User selected plan from {selected_plan.get('timestamp', 'unknown date')} to view")
    
    # Display the selected plan
    selected_plan = plans[selected_plan_idx]
    
    st.header("Selected Plan")
    st.markdown(f"**Idea:** {selected_plan.get('idea_description', 'No description available')}")
    st.markdown(f"**Plan Type:** {selected_plan.get('plan_type', 'Not specified')}")
    st.markdown(f"**Created:** {selected_plan.get('timestamp', 'Unknown')}")
    st.markdown(f"**Iteration:** {selected_plan.get('iteration', 1)}")
    st.markdown(f"**Feedback:** {'Positive' if selected_plan.get('feedback') == 'positive' else 'Not specified'}")
    
    # Display the plan content
    st.markdown("---")
    st.subheader("Implementation Plan")
    plan_content = selected_plan.get('generated_plan', 'No plan content available')
    st.markdown(plan_content)
    
    # Provide download option
    st.markdown("---")
    st.subheader("Download Options")
    
    # Generate a default filename based on timestamp and a portion of the idea
    idea_snippet = ''.join(e for e in selected_plan.get('idea_description', 'plan')[:20] if e.isalnum() or e.isspace()).strip().replace(' ', '_')
    default_filename = f"plan_{idea_snippet}_{selected_plan.get('timestamp', 'unknown').split()[0]}.md"
    
    custom_filename = st.text_input("Filename for download:", value=default_filename)
    download_link = get_download_link(plan_content, filename=custom_filename)
    st.markdown(download_link, unsafe_allow_html=True)
    
    logger.debug(f"Created download link with filename: {custom_filename}")
    
    if st.button("Delete This Plan"):
        try:
            # Get the filename from the plan data and remove the file
            filename = selected_plan.get("filename")
            if filename:
                log_user_action(logger, "delete_plan", {"filename": filename})
                logger.info(f"User deleting plan: {filename}")
                
                file_path = os.path.join(plans_dir, filename)
                os.remove(file_path)
                
                st.success(f"Plan deleted successfully!")
                logger.info(f"Plan deleted successfully: {filename}")
                
                time.sleep(1)  # Give a moment for the success message to be seen
                st.rerun()  # Refresh the page
            else:
                error_msg = "Could not delete plan: filename not found in plan data."
                logger.error(error_msg)
                st.error(error_msg)
        except Exception as e:
            error_msg = f"Error deleting plan: {str(e)}"
            logger.error(error_msg)
            st.error(error_msg)
else:
    st.info("You don't have any saved plans yet. Generate a plan first!")
    logger.info("No saved plans found to display")
    
    # Provide a button to create the first plan
    if st.button("Create Your First Plan"):
        log_user_action(logger, "create_first_plan")
        logger.info("User starting to create their first plan")
        st.switch_page("pages/2_idea_Input.py")

# Navigation
st.markdown("---")
if st.button("← Back to Plan Generator"):
    log_user_action(logger, "navigate_back_to_plan_generator")
    logger.info("User navigating back to plan generator page")
    st.switch_page("pages/4_Plan_Generator.py")

if st.button("Start New Idea"):
    log_user_action(logger, "start_new_idea_from_history")
    logger.info("User starting a new idea from history page")
    
    # Clear all session state except model information and plan history
    if "model_type" in st.session_state:
        model_type = st.session_state.model_type
    else:
        model_type = None
        
    if "selected_model" in st.session_state:
        selected_model = st.session_state.selected_model
    else:
        selected_model = None
        
    if "api_key" in st.session_state:
        api_key = st.session_state.api_key
    else:
        api_key = None
        
    # Preserve plan history
    if "plan_history" in st.session_state:
        plan_history = st.session_state.plan_history
    else:
        plan_history = []
    
    logger.debug("Clearing session state while preserving model settings and plan history")
    
    # Reset session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Restore preserved values
    st.session_state.model_type = model_type
    st.session_state.selected_model = selected_model
    if api_key is not None:
        st.session_state.api_key = api_key
    st.session_state.plan_history = plan_history
    
    logger.info("Redirecting to idea input page")
    st.switch_page("pages/2_idea_Input.py")
