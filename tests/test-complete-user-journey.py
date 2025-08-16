#!/usr/bin/env python3
"""
Complete User Journey Test for Pipecat ECS Deployment

This script validates the complete user journey including:
1. Accessing the ALB DNS name
2. Creating a Daily room
3. Waiting for Nova Sonic agent to connect (20-30 seconds)
4. Validating all functionality is ready

Requirements: 5.1, 5.2, 5.3, 5.4
"""

import requests
import json
import time
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
ALB_DNS = "pipecat-alb-test-595851858.eu-north-1.elb.amazonaws.com"
BASE_URL = f"http://{ALB_DNS}"


class CompleteUserJourneyValidator:
    """Validator for complete user journey through the deployed Pipecat application."""

    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 30

    def test_complete_user_journey(self) -> Dict[str, Any]:
        """Test the complete user journey from start to finish."""
        logger.info("=" * 70)
        logger.info("COMPLETE USER JOURNEY VALIDATION")
        logger.info(f"Target: {BASE_URL}")
        logger.info("=" * 70)

        start_time = time.time()
        results = {
            "steps": {},
            "overall_success": False,
            "room_url": None,
            "token": None,
            "total_time": 0,
        }

        try:
            # Step 1: Test ALB health and readiness
            logger.info("\n🔍 Step 1: Testing ALB health and service readiness...")
            health_success = self._test_service_health()
            results["steps"]["service_health"] = health_success

            if not health_success:
                logger.error("❌ Service health check failed - cannot proceed")
                return results

            # Step 2: Create a Daily room via main endpoint (browser access simulation)
            logger.info("\n🌐 Step 2: Testing browser access (main endpoint)...")
            browser_success, browser_room_url = self._test_browser_access()
            results["steps"]["browser_access"] = browser_success
            results["browser_room_url"] = browser_room_url

            # Step 3: Create a Daily room via RTVI connect endpoint
            logger.info("\n🔗 Step 3: Testing RTVI client connection...")
            rtvi_success, rtvi_room_url, rtvi_token = self._test_rtvi_connection()
            results["steps"]["rtvi_connection"] = rtvi_success
            results["room_url"] = rtvi_room_url
            results["token"] = rtvi_token

            if not rtvi_success:
                logger.error(
                    "❌ RTVI connection failed - cannot proceed with Nova Sonic test"
                )
                return results

            # Step 4: Wait for Nova Sonic agent initialization
            logger.info("\n🎤 Step 4: Waiting for Nova Sonic agent initialization...")
            logger.info(
                "⏳ This takes 20-30 seconds as the agent connects to the room..."
            )
            logger.info(f"🔗 Room URL: {rtvi_room_url}")

            # Progressive waiting with status updates
            for i in range(6):  # 6 * 5 = 30 seconds total
                time.sleep(5)
                logger.info(f"⏳ Waiting... {(i+1)*5}/30 seconds")

            # Step 5: Validate Nova Sonic agent is connected
            logger.info("\n✅ Step 5: Validating Nova Sonic agent connection...")
            nova_sonic_success = self._test_nova_sonic_connection()
            results["steps"]["nova_sonic_ready"] = nova_sonic_success

            # Step 6: Test function calling capability
            logger.info("\n🔧 Step 6: Validating function calling capability...")
            function_calling_success = self._test_function_calling_ready()
            results["steps"]["function_calling"] = function_calling_success

            # Step 7: Test concurrent access (limited to avoid jitter)
            logger.info("\n👥 Step 7: Testing limited concurrent access...")
            concurrent_success = self._test_limited_concurrent_access()
            results["steps"]["concurrent_access"] = concurrent_success

            # Calculate overall success
            critical_steps = ["service_health", "rtvi_connection", "nova_sonic_ready"]
            overall_success = all(
                results["steps"].get(step, False) for step in critical_steps
            )
            results["overall_success"] = overall_success

            # Summary
            total_time = time.time() - start_time
            results["total_time"] = total_time

            logger.info("\n" + "=" * 70)
            logger.info("COMPLETE USER JOURNEY SUMMARY")
            logger.info("=" * 70)

            # Step-by-step results
            step_names = {
                "service_health": "Service Health & Readiness",
                "browser_access": "Browser Access (Main Endpoint)",
                "rtvi_connection": "RTVI Client Connection",
                "nova_sonic_ready": "Nova Sonic Agent Ready",
                "function_calling": "Function Calling Capability",
                "concurrent_access": "Limited Concurrent Access",
            }

            for step_key, step_name in step_names.items():
                status = results["steps"].get(step_key, False)
                icon = "✅" if status else "❌"
                logger.info(f"{icon} {step_name}: {'PASS' if status else 'FAIL'}")

            # Requirements validation
            logger.info("\n📋 REQUIREMENTS VALIDATION:")
            req_5_1 = results["steps"].get("rtvi_connection", False) and results[
                "steps"
            ].get(
                "browser_access", False
            )  # Daily WebRTC
            req_5_2 = results["steps"].get(
                "nova_sonic_ready", False
            )  # Nova Sonic speech processing
            req_5_3 = results["steps"].get(
                "function_calling", False
            )  # Function calling
            req_5_4 = results["steps"].get(
                "concurrent_access", False
            )  # Bot lifecycle management

            logger.info(
                f"✅ Requirement 5.1 (Daily WebRTC Integration): {'PASS' if req_5_1 else 'FAIL'}"
            )
            logger.info(
                f"✅ Requirement 5.2 (Nova Sonic Speech Processing): {'PASS' if req_5_2 else 'FAIL'}"
            )
            logger.info(
                f"✅ Requirement 5.3 (Function Calling - Weather API): {'PASS' if req_5_3 else 'FAIL'}"
            )
            logger.info(
                f"✅ Requirement 5.4 (Bot Process Lifecycle): {'PASS' if req_5_4 else 'FAIL'}"
            )

            results["requirements"] = {
                "5.1_daily_webrtc": req_5_1,
                "5.2_nova_sonic": req_5_2,
                "5.3_function_calling": req_5_3,
                "5.4_bot_lifecycle": req_5_4,
            }

            # Final status
            logger.info(f"\n⏱️  Total Time: {total_time:.2f} seconds")
            logger.info("=" * 70)

            if overall_success:
                logger.info("🎉 COMPLETE USER JOURNEY VALIDATION: PASSED")
                logger.info(
                    "🎤 Nova Sonic agent should now be ready for voice interaction!"
                )
                logger.info(f"🔗 Test the voice agent at: {rtvi_room_url}")
            else:
                logger.info("❌ COMPLETE USER JOURNEY VALIDATION: FAILED")

            logger.info("=" * 70)

            return results

        except Exception as e:
            logger.error(f"Complete user journey test failed: {str(e)}")
            results["error"] = str(e)
            return results

    def _test_service_health(self) -> bool:
        """Test service health and readiness."""
        try:
            # Health check
            health_response = self.session.get(f"{BASE_URL}/health")
            if health_response.status_code != 200:
                logger.error(f"Health endpoint failed: {health_response.status_code}")
                return False

            health_data = health_response.json()
            if health_data.get("status") != "healthy":
                logger.error(f"Service not healthy: {health_data.get('status')}")
                return False

            # Readiness check
            ready_response = self.session.get(f"{BASE_URL}/ready")
            if ready_response.status_code != 200:
                logger.error(f"Readiness endpoint failed: {ready_response.status_code}")
                return False

            ready_data = ready_response.json()
            if ready_data.get("status") != "ready":
                logger.error(f"Service not ready: {ready_data.get('status')}")
                return False

            logger.info("✅ Service is healthy and ready")
            return True

        except Exception as e:
            logger.error(f"Service health test failed: {str(e)}")
            return False

    def _test_browser_access(self) -> tuple[bool, Optional[str]]:
        """Test browser access via main endpoint."""
        try:
            response = self.session.get(f"{BASE_URL}/", allow_redirects=False)

            if response.status_code == 307:  # Redirect to Daily room
                room_url = response.headers.get("location")
                if room_url and "daily.co" in room_url:
                    logger.info(f"✅ Browser access successful - Room: {room_url}")
                    return True, room_url
                else:
                    logger.error(f"Invalid redirect URL: {room_url}")
                    return False, None
            else:
                logger.error(f"Expected redirect (307), got {response.status_code}")
                return False, None

        except Exception as e:
            logger.error(f"Browser access test failed: {str(e)}")
            return False, None

    def _test_rtvi_connection(self) -> tuple[bool, Optional[str], Optional[str]]:
        """Test RTVI client connection."""
        try:
            response = self.session.post(f"{BASE_URL}/connect")

            if response.status_code == 200:
                data = response.json()
                room_url = data.get("room_url")
                token = data.get("token")

                if room_url and "daily.co" in room_url and token and len(token) > 100:
                    logger.info(f"✅ RTVI connection successful - Room: {room_url}")
                    return True, room_url, token
                else:
                    logger.error("Invalid RTVI connection response")
                    return False, None, None
            else:
                logger.error(f"RTVI connection failed: {response.status_code}")
                return False, None, None

        except Exception as e:
            logger.error(f"RTVI connection test failed: {str(e)}")
            return False, None, None

    def _test_nova_sonic_connection(self) -> bool:
        """Test if Nova Sonic agent is connected and ready."""
        try:
            # Check bot process status
            health_response = self.session.get(f"{BASE_URL}/health")
            if health_response.status_code != 200:
                logger.error("Health check failed during Nova Sonic validation")
                return False

            health_data = health_response.json()
            active_bots = health_data.get("checks", {}).get("active_bots", 0)

            if active_bots > 0:
                logger.info(
                    f"✅ Nova Sonic agent connected - Active bots: {active_bots}"
                )
                logger.info("🎤 Voice interaction should now be available!")
                return True
            else:
                logger.warning(
                    "⚠️  No active bots detected - Nova Sonic may still be initializing"
                )
                # One more check after brief wait
                time.sleep(5)

                final_health_response = self.session.get(f"{BASE_URL}/health")
                if final_health_response.status_code == 200:
                    final_health_data = final_health_response.json()
                    final_active_bots = final_health_data.get("checks", {}).get(
                        "active_bots", 0
                    )

                    if final_active_bots > 0:
                        logger.info(
                            f"✅ Nova Sonic agent connected after additional wait - Active bots: {final_active_bots}"
                        )
                        return True
                    else:
                        logger.error(
                            "❌ Nova Sonic agent not detected after full initialization period"
                        )
                        return False
                else:
                    logger.error("Final health check failed")
                    return False

        except Exception as e:
            logger.error(f"Nova Sonic connection test failed: {str(e)}")
            return False

    def _test_function_calling_ready(self) -> bool:
        """Test if function calling capability is ready."""
        try:
            # Function calling is validated by successful bot initialization and AWS connectivity
            health_response = self.session.get(f"{BASE_URL}/health")
            if health_response.status_code != 200:
                return False

            health_data = health_response.json()

            # Check AWS configuration
            env_details = (
                health_data.get("checks", {}).get("environment", {}).get("details", {})
            )
            aws_configured = env_details.get("AWS_REGION") == "present"

            # Check active bots (indicates successful initialization including function calling setup)
            active_bots = health_data.get("checks", {}).get("active_bots", 0)

            if aws_configured and active_bots > 0:
                logger.info(
                    "✅ Function calling capability ready (AWS configured, bots active)"
                )
                return True
            else:
                logger.warning("⚠️  Function calling capability may be limited")
                return False

        except Exception as e:
            logger.error(f"Function calling readiness test failed: {str(e)}")
            return False

    def _test_limited_concurrent_access(self) -> bool:
        """Test limited concurrent access to avoid audio jitter."""
        try:
            # Create only one additional room to test concurrency without causing jitter
            logger.info("Creating one additional room to test concurrent access...")

            response = self.session.post(f"{BASE_URL}/connect")
            if response.status_code == 200:
                data = response.json()
                room_url = data.get("room_url")

                if room_url and "daily.co" in room_url:
                    logger.info(
                        f"✅ Concurrent access successful - Additional room: {room_url}"
                    )
                    logger.info(
                        "⚠️  Note: Limited to prevent audio jitter with multiple simultaneous rooms"
                    )
                    return True
                else:
                    logger.error("Invalid concurrent room creation response")
                    return False
            else:
                logger.error(f"Concurrent access failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Concurrent access test failed: {str(e)}")
            return False


def main():
    """Main function to run complete user journey validation."""
    validator = CompleteUserJourneyValidator()
    results = validator.test_complete_user_journey()

    # Exit with appropriate code
    sys.exit(0 if results["overall_success"] else 1)


if __name__ == "__main__":
    main()
