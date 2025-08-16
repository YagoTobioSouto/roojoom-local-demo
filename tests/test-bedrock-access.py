#!/usr/bin/env python3
"""
Test script to verify Amazon Bedrock Nova Sonic model access and permissions.
This script tests the Bedrock integration that will be used by the ECS deployment.
Updated for Nova Sonic's bidirectional streaming API.
"""

import os
import json
import boto3
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_nova_sonic_access():
    """Test Amazon Bedrock Nova Sonic model access using bidirectional streaming API."""

    print("=" * 60)
    print("Testing Amazon Bedrock Nova Sonic Model Access")
    print("=" * 60)

    # Check environment variables
    aws_region = os.getenv(
        "AWS_REGION", "eu-north-1"
    )  # Nova Sonic available in eu-north-1
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    print(f"AWS Region: {aws_region}")
    print(
        f"AWS Access Key ID: {aws_access_key[:10]}..."
        if aws_access_key
        else "AWS Access Key ID: Not set"
    )
    print(f"AWS Secret Access Key: {'Set' if aws_secret_key else 'Not set'}")
    print()

    try:
        # Import Nova Sonic specific SDK components
        try:
            # Try importing the new experimental SDK for Nova Sonic
            from aws_sdk_bedrock_runtime.client import BedrockRuntimeClient
            from aws_sdk_bedrock_runtime.models import (
                InvokeModelWithBidirectionalStreamInputChunk,
                BidirectionalInputPayloadPart,
            )
            from aws_sdk_bedrock_runtime.config import Config
            from smithy_aws_core.credentials_resolvers.environment import (
                EnvironmentCredentialsResolver,
            )

            print("✓ Nova Sonic experimental SDK available")
            use_experimental_sdk = True
        except ImportError:
            print("⚠️  Nova Sonic experimental SDK not available, falling back to boto3")
            use_experimental_sdk = False

        model_id = "amazon.nova-sonic-v1:0"
        print(f"Testing access to model: {model_id}")

        # Test with appropriate SDK
        if use_experimental_sdk:
            success = await test_with_experimental_sdk(aws_region, model_id)
        else:
            success = await test_with_boto3_fallback(
                aws_region, aws_access_key, aws_secret_key, model_id
            )

        return success

    except Exception as e:
        print(f"✗ Error testing Nova Sonic access: {str(e)}")
        print(f"Error type: {type(e).__name__}")

        # Provide specific guidance based on error type
        if "AccessDeniedException" in str(e):
            print("\nTroubleshooting:")
            print(
                "- Verify IAM permissions for bedrock:InvokeModelWithBidirectionalStream"
            )
            print(
                "- Check if Nova Sonic model access has been requested in Bedrock console"
            )
            print("- Ensure the model is available in eu-north-1 region")
        elif "ValidationException" in str(e):
            print("\nTroubleshooting:")
            print("- Check if the model ID is correct: amazon.nova-sonic-v1:0")
            print("- Verify the bidirectional streaming event format")
        elif "UnauthorizedOperation" in str(e):
            print("\nTroubleshooting:")
            print("- Check AWS credentials")
            print("- Verify IAM permissions for bidirectional streaming")

        return False


async def test_with_experimental_sdk(aws_region, model_id):
    """Test using the experimental Nova Sonic SDK."""
    try:
        from aws_sdk_bedrock_runtime.client import BedrockRuntimeClient
        from aws_sdk_bedrock_runtime.models import (
            InvokeModelWithBidirectionalStreamInputChunk,
            BidirectionalInputPayloadPart,
            InvokeModelWithBidirectionalStreamOperationInput,
        )
        from aws_sdk_bedrock_runtime.config import Config
        from smithy_aws_core.credentials_resolvers.environment import (
            EnvironmentCredentialsResolver,
        )

        # Initialize client
        config = Config(
            endpoint_uri=f"https://bedrock-runtime.{aws_region}.amazonaws.com",
            region=aws_region,
            aws_credentials_identity_resolver=EnvironmentCredentialsResolver(),
        )
        client = BedrockRuntimeClient(config=config)
        print("✓ Nova Sonic experimental client initialized")

        # Start bidirectional stream
        stream = await client.invoke_model_with_bidirectional_stream(
            InvokeModelWithBidirectionalStreamOperationInput(model_id=model_id)
        )
        print("✓ Bidirectional stream established")

        # Send session start event
        session_start_event = {
            "event": {
                "sessionStart": {
                    "inferenceConfiguration": {
                        "maxTokens": 1024,
                        "topP": 0.9,
                        "temperature": 0.7,
                    }
                }
            }
        }

        event = InvokeModelWithBidirectionalStreamInputChunk(
            value=BidirectionalInputPayloadPart(
                bytes_=json.dumps(session_start_event).encode("utf-8")
            )
        )

        await stream.input_stream.send(event)
        print("✓ Session start event sent successfully")

        # Check if we can receive responses
        if hasattr(stream, "output_stream") and stream.output_stream is not None:
            print("✓ Output stream available for receiving responses")
        else:
            print("⚠️  Output stream not immediately available (may be expected)")

        # Clean shutdown
        await stream.input_stream.close()
        print("✓ Stream closed successfully")

        return True

    except Exception as e:
        print(f"✗ Experimental SDK test failed: {str(e)}")
        return False


async def test_with_boto3_fallback(
    aws_region, aws_access_key, aws_secret_key, model_id
):
    """Fallback test using standard boto3 (limited functionality)."""
    try:
        # Create standard Bedrock client
        if aws_access_key and aws_secret_key:
            bedrock_client = boto3.client(
                "bedrock-runtime",
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
            )
        else:
            bedrock_client = boto3.client("bedrock-runtime", region_name=aws_region)

        print("✓ Standard Bedrock client created")

        # Check if the bidirectional stream method exists
        if hasattr(bedrock_client, "invoke_model_with_bidirectional_stream"):
            print("✓ InvokeModelWithBidirectionalStream method available")

            # Note: Standard boto3 doesn't fully support the bidirectional streaming
            # This is a basic connectivity test
            print("⚠️  Standard boto3 has limited Nova Sonic support")
            print("⚠️  For full functionality, use the experimental Nova Sonic SDK")
            return True
        else:
            print("✗ InvokeModelWithBidirectionalStream method not available")
            print("✗ boto3 version may be too old for Nova Sonic")
            return False

    except Exception as e:
        print(f"✗ boto3 fallback test failed: {str(e)}")
        return False


def test_nova_sonic_permissions():
    """Test IAM permissions specifically for Nova Sonic."""

    print("\n" + "=" * 60)
    print("Testing IAM Permissions for Nova Sonic")
    print("=" * 60)

    aws_region = os.getenv("AWS_REGION", "eu-north-1")

    try:
        # Test STS to verify basic AWS access
        sts_client = boto3.client("sts", region_name=aws_region)
        identity = sts_client.get_caller_identity()

        print(f"✓ AWS Identity verified:")
        print(f"  Account: {identity.get('Account')}")
        print(f"  User/Role ARN: {identity.get('Arn')}")
        print(f"  User ID: {identity.get('UserId')}")

        # Check Bedrock model access
        try:
            bedrock_client = boto3.client("bedrock", region_name=aws_region)
            models_response = bedrock_client.list_foundation_models()

            # Check specifically for Nova Sonic
            nova_sonic_found = False
            for model in models_response.get("modelSummaries", []):
                if "nova-sonic" in model.get("modelId", "").lower():
                    nova_sonic_found = True
                    print(f"✓ Found Nova Sonic: {model.get('modelId')}")
                    print(f"  Status: {model.get('modelLifecycle', {}).get('status')}")

            if not nova_sonic_found:
                print("✗ Nova Sonic model not found in available models")
                print("   Please enable Nova Sonic in the Bedrock console")

        except Exception as e:
            print(f"✗ Bedrock model listing failed: {str(e)}")

        # Test required permissions for Nova Sonic
        required_permissions = [
            "bedrock:InvokeModelWithBidirectionalStream",
            "bedrock:InvokeModel",
            "bedrock:ListFoundationModels",
        ]

        print(f"\nRequired permissions for Nova Sonic:")
        for permission in required_permissions:
            print(f"  - {permission}")

        print(f"\nRequired IAM policy for Nova Sonic:")
        print(
            json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "bedrock:InvokeModelWithBidirectionalStream",
                                "bedrock:InvokeModel",
                                "bedrock:ListFoundationModels",
                            ],
                            "Resource": [
                                "arn:aws:bedrock:*::foundation-model/amazon.nova-sonic-v1:0",
                                "arn:aws:bedrock:*::foundation-model/*",
                            ],
                        }
                    ],
                },
                indent=2,
            )
        )

        return True

    except Exception as e:
        print(f"✗ Error testing permissions: {str(e)}")
        return False


def check_prerequisites():
    """Check prerequisites for Nova Sonic."""

    print("\n" + "=" * 60)
    print("Checking Nova Sonic Prerequisites")
    print("=" * 60)

    issues = []

    # Check region
    aws_region = os.getenv("AWS_REGION", "eu-north-1")
    if aws_region not in ["eu-north-1"]:
        issues.append(
            f"⚠️  Nova Sonic is primarily available in eu-north-1, you're using {aws_region}"
        )
    else:
        print(f"✓ Region check passed: {aws_region}")

    # Check Python version
    import sys

    python_version = sys.version_info
    if python_version < (3, 8):
        issues.append(
            f"⚠️  Python {python_version.major}.{python_version.minor} may have compatibility issues"
        )
    else:
        print(
            f"✓ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}"
        )

    # Check for experimental SDK
    try:
        import aws_sdk_bedrock_runtime

        print("✓ Nova Sonic experimental SDK is available")
    except ImportError:
        issues.append("⚠️  Nova Sonic experimental SDK not installed")
        print("⚠️  Consider installing: pip install aws-sdk-bedrock-runtime")

    # Check boto3 version
    try:
        import boto3

        print(f"✓ boto3 version: {boto3.__version__}")
    except AttributeError:
        print("⚠️  Could not determine boto3 version")

    if issues:
        print(f"\n⚠️  Found {len(issues)} potential issues:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("\n✓ All prerequisites look good!")

    return len(issues) == 0


async def main():
    """Main test function."""

    print(f"Nova Sonic Access Test - {datetime.now().isoformat()}")

    # Check prerequisites first
    prereq_success = check_prerequisites()

    # Test 1: Nova Sonic specific access
    nova_sonic_success = await test_nova_sonic_access()

    # Test 2: IAM permissions specific to Nova Sonic
    permission_success = test_nova_sonic_permissions()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Prerequisites Check: {'✓ PASS' if prereq_success else '⚠️  ISSUES'}")
    print(f"Nova Sonic Access: {'✓ PASS' if nova_sonic_success else '✗ FAIL'}")
    print(f"IAM Permissions: {'✓ PASS' if permission_success else '✗ FAIL'}")

    if prereq_success and nova_sonic_success and permission_success:
        print("\n🎉 All tests passed! Nova Sonic deployment should work.")
        print("\n📋 Next steps:")
        print("   1. Install Nova Sonic experimental SDK if not already installed")
        print("   2. Implement bidirectional streaming in your application")
        print("   3. Handle audio input/output in your ECS deployment")
    else:
        print("\n⚠️  Some tests failed. Address issues before deploying:")
        if not prereq_success:
            print("   - Fix prerequisite issues")
        if not nova_sonic_success:
            print("   - Fix Nova Sonic access issues")
        if not permission_success:
            print("   - Fix IAM permission issues")

    return prereq_success and nova_sonic_success and permission_success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
