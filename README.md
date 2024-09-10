### Introduction

For demonstration purposes, I have chosen to prompt the assistant to answer queries related to an imaginary product named **Chime**, which shares similar features with Slack. Here is a brief overview of Chime:

**Chime** is a unified communication platform that offers real-time messaging, video calls, and file sharing, similar to Slack. It enhances team collaboration with integrated tools and customizable notifications, ensuring that teams stay connected and productive.

### Current Capabilities

The voice assistant is designed to handle queries related to Chime and assist users in navigating the platform. It features three distinct voices, showcasing the variety of voices available for the assistant.

### Implemented Features

- Engage in conversations with three different voice assistants.
- Maintain conversation context and handle follow-up questions using an in-memory cache.
- Provide each user with a separate session to ensure private conversations.
- Include a debug mode, configurable via the `DEBUG_MODE` environment variable, which logs LLM outputs for troubleshooting.
- Optional Feature: Utilize voice activity detection (VAD) with the Silero VAD model to filter out silent audio and respond appropriately. This feature can be enabled by installing the `silero_vad` Python package. Due to deployment constraints, it is optional.

### Technical Details

- **Backend**: The project is built using FastAPI.
- **Frontend**: Utilizes Vanilla JavaScript, templates are rendered by the FastAPI backend.
- **Speech-to-Text**: Performed using [Google Text To Speech AI](https://cloud.google.com/text-to-speech?hl=en) APIs.
- **Text Generation**: Achieved through GroqAI APIs, utilizing the `llama3-8b-8192` model for chat completion.
- **Transcription**: Handled by [GroqAI](https://groq.com/) APIs using the `distil-whisper-large-v3-en` model.
- **Integration**: [Litellm](https://docs.litellm.ai/) is used to facilitate seamless connections with various LLM providers.

**Notes**:
- The `LLM_MODEL_NAME` can be adjusted in the `.env` file to switch the text generation model.
- The transcription model can be changed by specifying the desired model in the `TRANSCRIPT_MODEL_NAME` within the `.env` file.

#### Streaming and Latency Optimization
The transcription and chat completion features leverage streaming responses from the LLM provider to the backend. Additionally, user audio is streamed to the backend in chunks, enabling quicker and more efficient handling of input.

### Potential Improvements

If more time had been available, the following enhancements would be considered:

- **Redis for Conversation Cache**: Implement Redis to improve the efficiency and scalability of storing conversation context, replacing the current in-memory cache system.
- **Improving Assistant's Product Knowledge with RAG**: Integrate a Retrieval-Augmented Generation (RAG) approach to supplement the assistant's responses with relevant documents containing detailed product information.
- **Rate Limiting**: Introduce rate limiting for each user to prevent abuse and ensure fair use of the service.
- **Enhanced Retry and Timeout Mechanism**: Improve the retry and timeout mechanisms for interactions with LLM provider services to increase reliability and robustness.


### Setting Up and Running the Project Locally

To run the project locally, follow these steps:

1. **Ensure Python is Installed**: Make sure Python is installed on your system.

2. **Clone the Repository**: Clone the repository using `git clone <repository-url>`.

3. **Navigate to the Source Directory**: Run `cd src` to enter the source directory.

4. **Create a Virtual Environment**: Execute `python -m venv venv` to create a virtual environment.

5. **Activate the Virtual Environment**:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

6. **Install Dependencies**: Run `pip install -r requirements.txt` to install the required packages.

7. **Set Up Environment Variables**:
   - Copy the example environment file: `cp .env.example .env`
   - Open the `.env` file and set `DEBUG_MODE=true` to enable detailed logs about LLM responses.
   - Obtain the [GroqAI API](https://groq.com/) key by signing up for an account and creating one from the GroqAI console. Paste the API key into the `.env` file.
   - For text-to-speech functionality, create a Google Cloud service account, download the key, and paste the JSON value into the `.env` file. Wrap the JSON value in single quotes. This was done to ease the cloud deployment process on managed cloud services.
