AI Agent Wrapper API

This project provides a common wrapper API around Vapi and Retell AI's create-agent APIs. It allows users to call either Vapi or Retell API using a single endpoint with a standardized set of parameters.

Setup Instructions





Clone the Repository:

https://github.com/anshu1602/ai-agent-wrapper.git
cd ai-agent-wrapper



Create a Virtual Environment and Install Dependencies:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt



Set Environment Variables:





Copy .env.example to .env:

cp .env.example .env



Edit .env and add your Vapi and Retell API keys:

VAPI_BASE_URL=https://api.vapi.ai/
RETELL_BASE_URL=https://api.retellai.com/
VAPI_API_KEY=your_vapi_api_key
RETELL_API_KEY=your_retell_api_key



Run the Application:

python app.py

The API will be available at http://127.0.0.1:5000.

API Endpoint

POST /create-agent

Request Body





provider: String (required) - "vapi" or "retell".



params: Object (required)





name: String (required) - Agent name.



model: Object (required) - Model configuration.





provider: String (for Vapi, e.g., "openai", default: "openai").



model: String (for Vapi, e.g., "gpt-4", default: "gpt-4").



type: String (for Retell, e.g., "retell-llm", default: "retell-llm").



llm_id: String (for Retell, e.g., "llm_d16e07ac75c77c2101412f199ce5").



voice: String (required) - Voice identifier (e.g., "21m00Tcm4TlvDq8ikWAM" for Vapi, "11labs-Adrian" for Retell).



voice_provider: String (optional) - Voice provider (e.g., "11labs", default: "11labs").



webhook_url: String (optional) - Webhook URL.



instructions: String (optional) - Instructions for the agent (maps to Vapi's firstMessage and Retell's system_prompt).

Example Request for Vapi

{
    "provider": "vapi",
    "params": {
        "name": "Test Agent",
        "model": {
            "provider": "openai",
            "model": "gpt-4"
        },
        "voice": "21m00Tcm4TlvDq8ikWAM",
        "voice_provider": "11labs",
        "webhook_url": "https://example.com/webhook",
        "instructions": "Be helpful"
    }
}

Example Response for Vapi

{
    "agent_id": "b9b0292b-2f05-4439-92d6-638ba2752ce1",
    "name": "Test Agent",
    "status": "created",
    "details": {
        "agent_id": "b9b0292b-2f05-4439-92d6-638ba2752ce1",
        "created_at": "2025-04-23T17:12:04.371Z",
        "updated_at": "2025-04-23T17:12:04.371Z",
        "model": {
            "model": "gpt-4",
            "provider": "openai"
        },
        "voice": {
            "provider": "11labs",
            "voiceId": "21m00Tcm4TlvDq8ikWAM"
        },
        "organization_id": "6d584e73-3381-47ed-858a-67554c889925",
        "is_server_url_secret_set": false,
        "webhook_url": "https://example.com/webhook"
    }
}

Example Request for Retell

{
    "provider": "retell",
    "params": {
        "name": "Test Agent",
        "model": {
            "type": "retell-llm",
            "llm_id": "llm_d16e07ac75c77c2101412f199ce5"
        },
        "voice": "11labs-Adrian",
        "voice_provider": "11labs",
        "webhook_url": "https://example.com/webhook",
        "instructions": "Be helpful"
    }
}

Example Response for Retell

{
    "agent_id": "agent_e9fe25266e95fcdb228bc8a65d",
    "name": "Test Agent",
    "status": "created",
    "details": {
        "agent_id": "agent_e9fe25266e95fcdb228bc8a65d",
        "agent_name": "Test Agent",
        "created_at": "2025-04-23T17:39:42.706Z",
        "response_engine": {
            "type": "retell-llm",
            "llm_id": "llm_d16e07ac75c77c2101412f199ce5",
            "version": 0
        },
        "voice_id": "11labs-Adrian",
        "webhook_url": "https://example.com/webhook",
        "language": "en-US",
        "max_call_duration_ms": 3600000,
        "opt_out_sensitive_data_storage": false,
        "is_published": false
    }
}
