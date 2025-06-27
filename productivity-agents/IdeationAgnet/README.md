# Idea-to-Plan Generator Agent

## Overview

The Idea-to-Plan Generator Agent is an interactive AI assistant that transforms rough ideas into structured implementation plans. By combining text descriptions, visual input (drawings/sketches), and interactive brainstorming, the agent generates comprehensive, actionable plans across various domains.

## Features

- **Flexible Model Selection**: Choose between local Ollama models or cloud-based LLMs
- **Visual Input Support**: Upload drawings, sketches, or diagrams to illustrate your idea
- **Interactive Brainstorming**: AI asks clarifying questions to refine your concept
- **Structured Implementation Plans**: Get detailed plans with timelines, resources, and next steps
- **Feedback Loop**: Rate plans and provide feedback for continuous improvement
- **Plan History**: View and access previously generated plans

## Installation

1. Clone this repository or download the files to your local machine
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. If using local models, ensure [Ollama](https://ollama.ai) is installed and running

## Usage

1. Start the Streamlit app:

```bash
streamlit run Home.py
```

2. Follow the step-by-step workflow:
   - Select an AI model (local or cloud)
   - Describe your idea
   - Upload a drawing or sketch
   - Choose a plan type
   - Engage in interactive brainstorming (optional)
   - Generate and refine your implementation plan

## Application Structure

- **Home.py**: Main landing page and application entry point
- **pages/1_⚙️_Configuration.py**: Model selection and validation
- **pages/2_📝_Idea_Input.py**: Idea description, image upload, and plan type selection
- **pages/3_💭_Brainstorming.py**: Interactive Q&A session to refine the idea
- **pages/4_📋_Plan_Generator.py**: Plan generation and feedback
- **pages/5_📊_History.py**: Access to previously generated plans
- **utils/model_utils.py**: Utilities for model connection and generation

## Requirements

- Python 3.8+
- Streamlit
- Ollama (if using local models)
- OpenAI API key (if using cloud models)
- Internet connection (for cloud models)

## Notes

- Generated plans are saved locally in the `plans/` directory
- For image analysis, vision-capable models (e.g., GPT-4 Vision) provide the best results
- API keys are only stored in memory during the session and not saved to disk

## License

This project is open source and available under the MIT License.
