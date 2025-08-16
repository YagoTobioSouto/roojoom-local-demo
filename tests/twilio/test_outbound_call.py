#!/usr/bin/env python3
"""
Test outbound Twilio calls using the reference code pattern
Based on: https://www.twilio.com/docs/voice/quickstart/server
"""

import os
import sys
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


def make_test_call(to_number: str, webhook_url: str = None):
    """
    Make a test outbound call using Twilio

    Args:
        to_number: Phone number to call (e.g., "+1234567890")
        webhook_url: Optional webhook URL for call handling
    """

    # Load environment variables
    load_dotenv()

    # Get Twilio credentials
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_PHONE_NUMBER")

    if not all([account_sid, auth_token, from_number]):
        print("❌ Missing required Twilio credentials in environment")
        print("Required: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER")
        return False

    print("📞 Making test outbound call...")
    print(f"From: {from_number}")
    print(f"To: {to_number}")

    try:
        client = Client(account_sid, auth_token)

        # Default to Twilio demo URL if no webhook provided
        if not webhook_url:
            webhook_url = "http://demo.twilio.com/docs/voice.xml"
            print(f"Using demo webhook: {webhook_url}")
        else:
            print(f"Using custom webhook: {webhook_url}")

        # Make the call
        call = client.calls.create(
            url=webhook_url,
            to=to_number,
            from_=from_number,
        )

        print(f"✅ Call initiated successfully!")
        print(f"Call SID: {call.sid}")
        print(f"Call Status: {call.status}")
        print(f"Call Direction: {call.direction}")

        # Wait a moment and check call status
        import time

        time.sleep(2)

        # Fetch updated call status
        updated_call = client.calls(call.sid).fetch()
        print(f"Updated Status: {updated_call.status}")

        return True

    except TwilioRestException as e:
        print(f"❌ Twilio API Error: {e}")
        print(f"Error Code: {e.code}")
        print(f"Error Message: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def list_recent_calls():
    """List recent calls for debugging"""
    load_dotenv()

    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

    if not all([account_sid, auth_token]):
        print("❌ Missing Twilio credentials")
        return

    try:
        client = Client(account_sid, auth_token)
        calls = client.calls.list(limit=5)

        print("\n📊 Recent Calls:")
        print("-" * 60)

        if not calls:
            print("No recent calls found")
            return

        for call in calls:
            print(f"SID: {call.sid}")
            print(f"From: {call.from_} → To: {call.to}")
            print(f"Status: {call.status}")
            print(f"Direction: {call.direction}")
            print(f"Duration: {call.duration}s" if call.duration else "Duration: N/A")
            print(f"Date: {call.date_created}")
            print("-" * 60)

    except Exception as e:
        print(f"❌ Error fetching calls: {e}")


if __name__ == "__main__":
    print("🔍 Twilio Outbound Call Test")
    print("=" * 50)

    if len(sys.argv) < 2:
        print("Usage: python3 test_outbound_call.py <phone_number> [webhook_url]")
        print("\nExamples:")
        print("  # Call with demo webhook")
        print("  python3 test_outbound_call.py +1234567890")
        print("")
        print("  # Call with your local webhook (via ngrok)")
        print(
            "  python3 test_outbound_call.py +1234567890 https://abc123.ngrok.io/incoming-call"
        )
        print("")
        print("  # List recent calls")
        print("  python3 test_outbound_call.py --list")

        sys.exit(1)

    if sys.argv[1] == "--list":
        list_recent_calls()
        sys.exit(0)

    to_number = sys.argv[1]
    webhook_url = sys.argv[2] if len(sys.argv) > 2 else None

    # Validate phone number format
    if not to_number.startswith("+"):
        print("⚠️  Phone number should include country code (e.g., +1234567890)")
        to_number = "+" + to_number.lstrip("+")
        print(f"Using: {to_number}")

    success = make_test_call(to_number, webhook_url)

    if success:
        print("\n🎉 Test call completed!")
        print("\nNext steps:")
        print("1. Answer the call on your phone")
        print("2. Listen to the voice response")
        print("3. Check your server logs for webhook activity")

        # Show recent calls
        print("\n" + "=" * 50)
        list_recent_calls()
    else:
        print("\n❌ Test call failed!")
        sys.exit(1)
