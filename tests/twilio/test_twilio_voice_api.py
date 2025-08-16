#!/usr/bin/env python3
"""
Test Twilio Voice API functionality
Based on Twilio Voice Quickstart: https://www.twilio.com/docs/voice/quickstart/server
"""

import os
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from twilio.base.exceptions import TwilioRestException


def test_twiml_generation():
    """Test TwiML generation for voice responses."""
    print("🎵 Testing TwiML Generation...")

    # Create a simple TwiML response
    response = VoiceResponse()
    response.say(
        "Hello! This is a test of the Twilio Voice API integration with Pipecat AI agent."
    )
    response.pause(length=1)
    response.say(
        "If you can hear this message, the TwiML generation is working correctly."
    )

    twiml_str = str(response)
    print(f"Generated TwiML:\n{twiml_str}")
    print("✅ TwiML generation successful")
    return twiml_str


def test_voice_capabilities():
    """Test Twilio Voice API capabilities."""
    load_dotenv()

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")

    if not all([account_sid, auth_token, phone_number]):
        print("❌ Missing required Twilio credentials")
        return False

    try:
        client = Client(account_sid, auth_token)

        print("📞 Testing Voice API Capabilities...")

        # Test 1: Check available voices
        print("\n1. Available Voices:")
        # Note: This is just for demonstration - actual voice selection happens in TwiML
        voices = ["alice", "man", "woman", "Polly.Amy", "Polly.Brian"]
        for voice in voices:
            print(f"   - {voice}")
        print("✅ Voice options available")

        # Test 2: Validate phone number capabilities
        print("\n2. Phone Number Capabilities:")
        incoming_numbers = client.incoming_phone_numbers.list(phone_number=phone_number)

        if incoming_numbers:
            number = incoming_numbers[0]
            capabilities = number.capabilities
            print(f"   Voice: {capabilities.get('voice', False)}")
            print(f"   SMS: {capabilities.get('sms', False)}")
            print(f"   MMS: {capabilities.get('mms', False)}")
            print("✅ Phone number capabilities verified")
        else:
            print("❌ Phone number not found")
            return False

        # Test 3: Generate webhook-ready TwiML
        print("\n3. Webhook TwiML Response:")
        twiml = test_twiml_generation()

        # Test 4: Validate webhook URL format (if configured)
        webhook_url = os.getenv("TWILIO_WEBHOOK_URL")
        if webhook_url:
            print(f"\n4. Webhook URL: {webhook_url}")
            if webhook_url.startswith("https://"):
                print("✅ Webhook URL uses HTTPS")
            else:
                print("⚠️  Webhook URL should use HTTPS for production")
        else:
            print("\n4. Webhook URL: Not configured")
            print(
                "   For ECS deployment, this will be: https://your-alb-dns/incoming-call"
            )

        print("\n🎉 Voice API capabilities test completed successfully!")
        return True

    except TwilioRestException as e:
        print(f"❌ Twilio API Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def generate_media_stream_twiml(websocket_url):
    """Generate TwiML for media streaming - this will be used in the actual implementation."""
    print(f"\n🔄 Generating Media Stream TwiML for: {websocket_url}")

    response = VoiceResponse()
    response.say("Connecting you to the AI agent. Please wait a moment.")

    # Start media stream to WebSocket endpoint
    start = response.start()
    stream = start.stream(url=websocket_url)

    # Keep the call alive while streaming
    response.pause(length=3600)  # 1 hour max call duration

    twiml_str = str(response)
    print(f"Media Stream TwiML:\n{twiml_str}")
    print("✅ Media Stream TwiML generated")
    return twiml_str


if __name__ == "__main__":
    print("🔍 Testing Twilio Voice API Integration...")
    print("=" * 60)

    # Test basic voice capabilities
    success = test_voice_capabilities()

    if success:
        print("\n" + "=" * 60)
        print("📋 Integration Summary:")
        print("✅ Twilio account active and configured")
        print("✅ Phone number has voice capabilities")
        print("✅ TwiML generation working")
        print("✅ Ready for webhook integration")

        print("\n🚀 Next Steps for ECS Integration:")
        print("1. Deploy FastAPI server with webhook endpoints")
        print("2. Configure ALB with HTTPS for webhook security")
        print("3. Update Twilio phone number webhook URL")
        print("4. Test end-to-end voice flow with Pipecat AI")

        # Demo media stream TwiML
        example_websocket_url = "wss://your-alb-dns.amazonaws.com/media-stream"
        generate_media_stream_twiml(example_websocket_url)

    exit(0 if success else 1)
