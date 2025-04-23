
import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from urllib.parse import urljoin  # Added missing import for urljoin
from retell import Retell  # Import Retell SDK
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# API base URLs and keys from environment
VAPI_BASE_URL = os.getenv("VAPI_BASE_URL", "https://api.vapi.ai/")
RETELL_API_KEY = os.getenv("RETELL_API_KEY")
VAPI_API_KEY = os.getenv("VAPI_API_KEY")

# Initialize Retell client
retell_client = Retell(api_key=RETELL_API_KEY) if RETELL_API_KEY else None

# Common response format
def create_response(agent_id, name, status, details=None):
    response = {
        "agent_id": agent_id,
        "name": name,
        "status": status
    }
    if details:
        response["details"] = details
    return response

# Map common parameters to Vapi format
def map_to_vapi_params(params):
    vapi_params = {
        "name": params.get("name"),
        "model": {
            "provider": params.get("model", {}).get("provider", "openai"),
            "model": params.get("model", {}).get("model", "gpt-4")
        },
        "voice": {
            "provider": params.get("voice_provider", "11labs"),
            "voiceId": params.get("voice", "21m00Tcm4TlvDq8ikWAM")  # Default to working Vapi voice ID
        }
    }
    if params.get("webhook_url"):
        vapi_params["webhook"] = params.get("webhook_url")
    return {k: v for k, v in vapi_params.items() if v is not None}  # Remove None values

# Map common parameters to Retell format
def map_to_retell_params(params):
    voice_id = params.get("voice", "11labs-Adrian")  # Default to a valid Retell voice ID
    voice_provider = params.get("voice_provider", "11labs")
    retell_params = {
        "response_engine": {
            "type": params.get("model", {}).get("type", "retell-llm"),
            "llm_id": params.get("model", {}).get("llm_id", "llm_d16e07ac75c77c2101412f199ce5")
        },
        "agent_name": params.get("name"),
        "voice_id": voice_id if voice_provider == "11labs" else f"{voice_provider}-{voice_id}"
    }
    if params.get("webhook_url"):
        retell_params["webhook_url"] = params.get("webhook_url")
    return retell_params

# Call Vapi API
def call_vapi_api(params):
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    url = urljoin(VAPI_BASE_URL, "assistant")
    try:
        logger.info(f"Sending Vapi API request with payload: {params}")
        response = requests.post(url, json=params, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Vapi API response: {data}")
        return create_response(data.get("id"), data.get("name"), "created", data)
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_message = e.response.json().get("message", str(e))
            except ValueError:
                error_message = e.response.text
        logger.error(f"Vapi API call failed: {error_message}")
        raise Exception(f"Vapi API call failed: {error_message}")

# Call Retell API using SDK with keyword arguments
def call_retell_api(params):
    try:
        if not retell_client:
            raise Exception("Retell client not initialized. Please check RETELL_API_KEY.")

        logger.info(f"Sending Retell API request with payload: {params}")
        # Extract fields from params and pass as keyword arguments
        response = retell_client.agent.create(
            response_engine=params.get("response_engine"),
            agent_name=params.get("agent_name"),
            voice_id=params.get("voice_id"),
            webhook_url=params.get("webhook_url", None)
        )
        logger.info(f"Retell API response: {response}")
        # Convert response_engine to a JSON-serializable dictionary
        response_engine_dict = {
            "type": response.response_engine.type,
            "llm_id": response.response_engine.llm_id,
            "version": response.response_engine.version
        }
        return create_response(response.agent_id, response.agent_name, "created", {
            "agent_id": response.agent_id,
            "agent_name": response.agent_name,
            "response_engine": response_engine_dict,
            "voice_id": response.voice_id,
            "webhook_url": getattr(response, "webhook_url", None),
            "created_at": getattr(response, "last_modification_timestamp", None)
        })
    except Exception as e:
        error_message = str(e)
        logger.error(f"Retell API call failed: {error_message}")
        raise Exception(f"Retell API call failed: {error_message}")

@app.route("/create-agent", methods=["POST"])
def create_agent():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON payload"}), 400

        # Validate required fields
        if "provider" not in data or not data["provider"]:
            return jsonify({"error": "Missing required field: provider"}), 400
        if "params" not in data or not isinstance(data["params"], dict):
            return jsonify({"error": "Missing or invalid params object"}), 400
        if "name" not in data["params"] or not data["params"]["name"]:
            return jsonify({"error": "Missing required field: params.name"}), 400

        provider = data.get("provider").lower()
        if provider not in ["vapi", "retell"]:
            return jsonify({"error": "Invalid provider. Must be 'vapi' or 'retell'"}), 400

        # Map parameters and call appropriate API
        if provider == "vapi":
            if not VAPI_API_KEY:
                return jsonify({"error": "Vapi API key not configured"}), 500
            vapi_params = map_to_vapi_params(data["params"])
            result = call_vapi_api(vapi_params)
        else:  # retell
            if not RETELL_API_KEY:
                return jsonify({"error": "Retell API key not configured"}), 500
            retell_params = map_to_retell_params(data["params"])
            result = call_retell_api(retell_params)

        logger.info(f"Agent created successfully for provider {provider}")
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)





