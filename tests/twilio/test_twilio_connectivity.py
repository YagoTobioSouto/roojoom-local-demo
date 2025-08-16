#!/usr/bin/env python3
"""
Test script to verify Twilio API connectivity
Based on Twilio Voice Quickstart: https://www.twilio.com/docs/voice/quickstart/server
"""

import os
import sys
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


def test_twilio_connectivity():
    """Test basic Twilio API connectivity and configuration."""

    # Load environment variables
    load_dotenv()

    # Get Twilio credentials from environment
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")

    print("🔍 Testing Twilio API Connectivity...")
    print("=" * 50)

    # Validate required credentials
    if not account_sid:
        print("❌ TWILIO_ACCOUNT_SID not found in environment")
        return False

    if not auth_token:
        print("❌ TWILIO_AUTH_TOKEN not found in environment")
        return False

    if not phone_number:
        print("❌ TWILIO_PHONE_NUMBER not found in environment")
        return False

    print(f"✅ Account SID: {account_sid[:8]}...")
    print(f"✅ Auth Token: {'*' * 8}...")
    print(f"✅ Phone Number: {phone_number}")
    print()

    try:
        # Initialize Twilio client
        client = Client(account_sid, auth_token)

        # Test 1: Verify account information
        print("📋 Test 1: Verifying account information...")
        account = client.api.accounts(account_sid).fetch()
        print(f"   Account Status: {account.status}")
        print(f"   Account Type: {account.type}")
        print("   ✅ Account verification successful")
        print()

        # Test 2: List incoming phone numbers
        print("📞 Test 2: Verifying phone number ownership...")
        incoming_phone_numbers = client.incoming_phone_numbers.list()

        found_number = False
        for number in incoming_phone_numbers:
            if number.phone_number == phone_number:
                found_number = True
                print(f"   Phone Number: {number.phone_number}")
                print(f"   Friendly Name: {number.friendly_name}")
                print(
                    f"   Voice Capabilities: {number.capabilities.get('voice', False)}"
                )
                print(f"   SMS Capabilities: {number.capabilities.get('sms', False)}")
                break

        if not found_number:
            print(f"   ⚠️  Phone number {phone_number} not found in account")
            print("   Available numbers:")
            for number in incoming_phone_numbers[:3]:  # Show first 3
                print(f"     - {number.phone_number}")
        else:
            print("   ✅ Phone number verification successful")
        print()

        # Test 3: Test API key credentials (if using API keys)
        api_sid = os.getenv("TWILIO_SID")  # API Key SID
        api_secret = os.getenv("TWILIO_SECRET")  # API Key Secret

        if api_sid and api_secret:
            print("🔑 Test 3: Testing API Key credentials...")
            try:
                # Create client with API key instead of auth token
                api_client = Client(api_sid, api_secret, account_sid)
                api_account = api_client.api.accounts(account_sid).fetch()
                print(f"   API Key SID: {api_sid[:8]}...")
                print(f"   Account Status via API Key: {api_account.status}")
                print("   ✅ API Key authentication successful")
            except TwilioRestException as e:
                print(f"   ❌ API Key authentication failed: {e}")
        else:
            print("🔑 Test 3: API Key credentials not configured (using auth token)")
        print()

        # Test 4: Test webhook URL accessibility (basic validation)
        print("🌐 Test 4: Webhook URL validation...")
        webhook_url = os.getenv("TWILIO_WEBHOOK_URL")
        if webhook_url:
            print(f"   Configured webhook URL: {webhook_url}")
            print("   ✅ Webhook URL configured")
        else:
            print("   ⚠️  TWILIO_WEBHOOK_URL not configured")
            print("   This will be needed for incoming call handling")
        print()

        # Test 5: List recent calls (last 5)
        print("📊 Test 5: Checking recent call history...")
        try:
            calls = client.calls.list(limit=5)
            if calls:
                print(f"   Found {len(calls)} recent calls:")
                for call in calls:
                    print(
                        f"     - {call.sid[:8]}... | {call.status} | {call.direction}"
                    )
            else:
                print("   No recent calls found")
            print("   ✅ Call history access successful")
        except TwilioRestException as e:
            print(f"   ❌ Call history access failed: {e}")
        print()

        print("🎉 Twilio API connectivity test completed successfully!")
        print("=" * 50)
        print("Next steps:")
        print("1. Configure webhook URL for incoming calls")
        print("2. Test incoming call handling")
        print("3. Integrate with Pipecat voice agent")

        return True

    except TwilioRestException as e:
        print(f"❌ Twilio API Error: {e}")
        print(f"   Error Code: {e.code}")
        print(f"   Error Message: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_twilio_connectivity()
    sys.exit(0 if success else 1)
