#!/usr/bin/env python3
"""
Test webhook integration for Twilio Voice with FastAPI
Based on Twilio Voice Quickstart: https://www.twilio.com/docs/voice/quickstart/server
"""

import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
from twilio.request_validator import RequestValidator

# Load environment variables
load_dotenv()

app = FastAPI()

# Twilio configuration
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


def validate_twilio_request(request: Request, body: str) -> bool:
    """Validate Twilio webhook signature for security."""
    if not TWILIO_AUTH_TOKEN:
        print("⚠️  TWILIO_AUTH_TOKEN not configured - skipping validation")
        return True

    validator = RequestValidator(TWILIO_AUTH_TOKEN)
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)

    return validator.validate(url, body, signature)


@app.post("/incoming-call")
async def handle_incoming_call(request: Request):
    """
    Handle incoming Twilio calls and return TwiML response.
    This endpoint will be called by Twilio when someone calls your number.
    """
    print("📞 Incoming call received!")

    # Get request body for signature validation
    body = await request.body()
    form_data = await request.form()

    print(f"Call from: {form_data.get('From', 'Unknown')}")
    print(f"Call to: {form_data.get('To', 'Unknown')}")
    print(f"Call SID: {form_data.get('CallSid', 'Unknown')}")

    # Validate request (optional but recommended for production)
    if not validate_twilio_request(request, body.decode()):
        print("❌ Invalid Twilio signature")
        return Response(status_code=403)

    # Create TwiML response
    response = VoiceResponse()

    # Option 1: Simple voice response (for testing)
    if os.getenv("SIMPLE_VOICE_TEST", "false").lower() == "true":
        response.say(
            "Hello! This is your Pipecat AI agent. The webhook integration is working correctly."
        )
        response.say("You can now integrate this with your voice AI system.")
    else:
        # Option 2: Connect to media stream (for AI integration)
        response.say("Connecting you to the AI agent. Please wait a moment.")

        # Get the base URL for WebSocket connection
        base_url = (
            str(request.base_url)
            .replace("http://", "ws://")
            .replace("https://", "wss://")
        )
        websocket_url = f"{base_url}media-stream"

        # Start media stream
        start = response.start()
        stream = start.stream(url=websocket_url)

        # Keep call alive during streaming
        response.pause(length=3600)  # 1 hour max

    print("✅ TwiML response generated")
    return Response(content=str(response), media_type="application/xml")


@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """
    Handle Twilio media stream WebSocket connection.
    This is where audio will be processed with the AI agent.
    """
    await websocket.accept()
    print("🔄 Media stream WebSocket connected")

    try:
        while True:
            # Receive message from Twilio
            message = await websocket.receive_text()
            data = json.loads(message)

            event = data.get("event")

            if event == "connected":
                print("📡 Media stream connected")

            elif event == "start":
                print("🎤 Media stream started")
                stream_sid = data.get("start", {}).get("streamSid")
                print(f"Stream SID: {stream_sid}")

            elif event == "media":
                # This is where audio data comes in
                # In real implementation, this would go to Pipecat/Nova Sonic
                payload = data.get("media", {}).get("payload")
                print(f"🎵 Received audio data: {len(payload) if payload else 0} bytes")

                # Echo back some audio (for testing)
                # In real implementation, this would be AI-generated audio
                response_audio = {
                    "event": "media",
                    "streamSid": data.get("streamSid"),
                    "media": {"payload": payload},  # Echo for now
                }
                await websocket.send_text(json.dumps(response_audio))

            elif event == "stop":
                print("🛑 Media stream stopped")
                break

    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        print("🔌 Media stream WebSocket disconnected")


@app.get("/health")
async def health_check():
    """Health check endpoint for ECS monitoring."""
    return {
        "status": "healthy",
        "twilio_configured": bool(TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER),
        "phone_number": TWILIO_PHONE_NUMBER,
    }


@app.get("/")
async def root():
    """Root endpoint with integration status."""
    return {
        "message": "Twilio Voice Integration Test Server",
        "endpoints": {
            "incoming_call": "/incoming-call",
            "media_stream": "/media-stream",
            "health": "/health",
        },
        "twilio_phone": TWILIO_PHONE_NUMBER,
        "status": "ready",
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Twilio Voice Integration Test Server...")
    print(f"📞 Twilio Phone Number: {TWILIO_PHONE_NUMBER}")
    print("🌐 Webhook endpoints:")
    print("   - POST /incoming-call (for Twilio webhooks)")
    print("   - WS /media-stream (for audio streaming)")
    print("   - GET /health (for health checks)")
    print("\n💡 To test:")
    print("1. Run this server locally")
    print("2. Use ngrok to expose it: ngrok http 8000")
    print(
        "3. Configure Twilio webhook URL to: https://your-ngrok-url.ngrok.io/incoming-call"
    )
    print("4. Call your Twilio number")

    uvicorn.run(app, host="0.0.0.0", port=8000)
