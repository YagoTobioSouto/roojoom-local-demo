#!/usr/bin/env python3
"""
Test script to verify AWS Secrets Manager integration for the Pipecat ECS deployment.
This script simulates how the ECS task will retrieve and use secrets.
"""

import os
import json
import boto3
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_secrets_retrieval():
    """Test retrieving secrets from AWS Secrets Manager."""

    print("=" * 60)
    print("Testing AWS Secrets Manager Integration")
    print("=" * 60)

    aws_region = os.getenv("AWS_REGION", "eu-north-1")

    try:
        # Create Secrets Manager client
        secrets_client = boto3.client("secretsmanager", region_name=aws_region)

        print(f"Using AWS region: {aws_region}")
        print()

        # Test 1: Retrieve Daily API Key secret
        daily_secret_name = "pipecat/daily-api-key"
        print(f"Testing secret: {daily_secret_name}")

        try:
            daily_response = secrets_client.get_secret_value(SecretId=daily_secret_name)
            daily_data = json.loads(daily_response["SecretString"])

            print(f"✓ Successfully retrieved Daily API secret")
            print(f"  Keys found: {list(daily_data.keys())}")
            print(f"  DAILY_API_KEY: {daily_data.get('DAILY_API_KEY', 'N/A')[:10]}...")
            print(f"  DAILY_API_URL: {daily_data.get('DAILY_API_URL', 'N/A')}")

            # Simulate environment variable injection
            os.environ["DAILY_API_KEY"] = daily_data.get("DAILY_API_KEY", "")
            os.environ["DAILY_API_URL"] = daily_data.get("DAILY_API_URL", "")

        except Exception as e:
            print(f"✗ Error retrieving Daily API secret: {str(e)}")
            return False

        print()

        # Test 2: Retrieve AWS Credentials secret
        aws_secret_name = "pipecat/aws-credentials"
        print(f"Testing secret: {aws_secret_name}")

        try:
            aws_response = secrets_client.get_secret_value(SecretId=aws_secret_name)
            aws_data = json.loads(aws_response["SecretString"])

            print(f"✓ Successfully retrieved AWS credentials secret")
            print(f"  Keys found: {list(aws_data.keys())}")
            print(
                f"  AWS_ACCESS_KEY_ID: {aws_data.get('AWS_ACCESS_KEY_ID', 'N/A')[:10]}..."
            )
            print(f"  AWS_REGION: {aws_data.get('AWS_REGION', 'N/A')}")

            # Simulate environment variable injection (ECS would do this automatically)
            # Note: In real ECS deployment, these would be injected by ECS, not retrieved manually

        except Exception as e:
            print(f"✗ Error retrieving AWS credentials secret: {str(e)}")
            return False

        print()
        print("✓ All secrets retrieved successfully!")

        return True

    except Exception as e:
        print(f"✗ Error testing secrets: {str(e)}")
        return False


def test_application_with_secrets():
    """Test that the application can work with secrets from environment variables."""

    print("\n" + "=" * 60)
    print("Testing Application with Secrets")
    print("=" * 60)

    # Check if required environment variables are set
    required_vars = ["DAILY_API_KEY", "AWS_REGION"]

    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {'Set' if value else 'Not set'}")
            if var == "DAILY_API_KEY":
                print(f"  Value: {value[:10]}...")
        else:
            print(f"✗ {var}: Not set")
            return False

    # Test Daily API helper initialization (similar to what the app does)
    try:
        from pipecat.transports.services.helpers.daily_rest import DailyRESTHelper
        import aiohttp
        import asyncio

        async def test_daily_helper():
            async with aiohttp.ClientSession() as session:
                daily_helper = DailyRESTHelper(
                    daily_api_key=os.getenv("DAILY_API_KEY", ""),
                    daily_api_url=os.getenv("DAILY_API_URL", "https://api.daily.co/v1"),
                    aiohttp_session=session,
                )

                # Test basic functionality (without creating a room)
                print("✓ Daily API helper initialized successfully")
                return True

        # Run the async test
        result = asyncio.run(test_daily_helper())
        if not result:
            return False

    except ImportError:
        print("⚠️  Pipecat not installed - skipping Daily API helper test")
    except Exception as e:
        print(f"✗ Error testing Daily API helper: {str(e)}")
        return False

    # Test Bedrock access with secrets
    try:
        bedrock_client = boto3.client(
            "bedrock-runtime", region_name=os.getenv("AWS_REGION")
        )
        print("✓ Bedrock client initialized successfully")

    except Exception as e:
        print(f"✗ Error initializing Bedrock client: {str(e)}")
        return False

    print("\n✓ Application integration test passed!")
    return True


def simulate_ecs_environment():
    """Simulate how ECS would inject secrets as environment variables."""

    print("\n" + "=" * 60)
    print("Simulating ECS Environment Variable Injection")
    print("=" * 60)

    aws_region = os.getenv("AWS_REGION", "eu-north-1")

    try:
        secrets_client = boto3.client("secretsmanager", region_name=aws_region)

        # Retrieve secrets and set as environment variables
        # This simulates what ECS does automatically

        # Daily API secret
        daily_response = secrets_client.get_secret_value(
            SecretId="pipecat/daily-api-key"
        )
        daily_data = json.loads(daily_response["SecretString"])

        # AWS credentials secret
        aws_response = secrets_client.get_secret_value(
            SecretId="pipecat/aws-credentials"
        )
        aws_data = json.loads(aws_response["SecretString"])

        # Set environment variables (simulating ECS injection)
        env_vars = {
            "DAILY_API_KEY": daily_data.get("DAILY_API_KEY"),
            "DAILY_API_URL": daily_data.get("DAILY_API_URL"),
            "AWS_ACCESS_KEY_ID": aws_data.get("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": aws_data.get("AWS_SECRET_ACCESS_KEY"),
            "AWS_REGION": aws_data.get("AWS_REGION"),
            "HOST": "0.0.0.0",
            "FAST_API_PORT": "7860",
        }

        print("Environment variables that would be injected by ECS:")
        for key, value in env_vars.items():
            if value:
                os.environ[key] = value
                if "KEY" in key or "SECRET" in key:
                    print(f"  {key}: {value[:10]}...")
                else:
                    print(f"  {key}: {value}")
            else:
                print(f"  {key}: <not set>")

        print("\n✓ ECS environment simulation completed!")
        return True

    except Exception as e:
        print(f"✗ Error simulating ECS environment: {str(e)}")
        return False


def main():
    """Main test function."""

    print(f"Secrets Integration Test - {datetime.now().isoformat()}")

    # Test 1: Secrets retrieval
    secrets_success = test_secrets_retrieval()

    # Test 2: Application integration
    app_success = test_application_with_secrets()

    # Test 3: ECS environment simulation
    ecs_success = simulate_ecs_environment()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Secrets Retrieval: {'✓ PASS' if secrets_success else '✗ FAIL'}")
    print(f"Application Integration: {'✓ PASS' if app_success else '✗ FAIL'}")
    print(f"ECS Environment Simulation: {'✓ PASS' if ecs_success else '✗ FAIL'}")

    if secrets_success and app_success and ecs_success:
        print("\n🎉 All secrets integration tests passed!")
        print("\nThe ECS deployment should work correctly with AWS Secrets Manager.")
        print("\nNext steps:")
        print("1. Deploy the updated CDK infrastructure")
        print("2. Build and push the container image")
        print("3. Deploy the ECS service")
        print("4. Test the deployed application")
    else:
        print("\n⚠️  Some tests failed. Please address the issues before deploying.")

    return secrets_success and app_success and ecs_success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
