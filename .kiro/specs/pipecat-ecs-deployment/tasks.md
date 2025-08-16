# Implementation Plan

## Prerequisites (Manual AWS Console Setup)

- [x] 0.1 Enable required AWS services and configure account

  - Enable Amazon Bedrock service in the target AWS region
  - Request access to Amazon Nova Sonic model in Bedrock console
  - Verify AWS CLI is configured with appropriate credentials and region
  - Ensure the AWS account has sufficient service limits for ECS Fargate tasks
  - _Requirements: 2.1, 5.2_

- [x] 0.2 Configure IAM permissions and roles

  - Create or verify IAM user/role has permissions for ECS, ECR, ALB, VPC, Secrets Manager, and CloudWatch
  - Ensure Bedrock permissions are granted for Nova Sonic model access
  - Verify permissions for CDK deployment (CloudFormation, IAM role creation)
  - _Requirements: 2.3, 6.3_

- [x] 0.3 Set up Daily.co account and API access

  - Verify Daily.co account is active and API key is available
  - Test Daily API key functionality from local environment
  - Ensure Daily.co service limits are sufficient for testing
  - _Requirements: 5.1_

- [x] 0.4 Choose target AWS region and verify service availability

  - Confirm Amazon Bedrock Nova Sonic is available in target region
  - Verify ECS Fargate is available in the chosen region
  - Check that all required AWS services are available in the target region
  - _Requirements: 2.1, 4.1_

- [x] 0.5 Network and security considerations
  - Decide whether to use default VPC or create new VPC for testing
  - Ensure NAT Gateway costs are acceptable for testing (or use public subnets for cost savings)
  - Verify outbound internet access requirements for Daily.co and external APIs
  - Consider security group rules for allowing traffic from ALB to ECS tasks
  - _Requirements: 2.2, 6.1, 6.2_

## Implementation Tasks

- [x] 0.6 Verify local Pipecat application functionality

  - Test the existing Pipecat application locally with current environment variables
  - Verify Daily WebRTC integration works with your Daily API key
  - Test Amazon Nova Sonic integration with your AWS credentials
  - Confirm weather function calling works as expected
  - Document any configuration issues or dependencies
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 1. Prepare the Pipecat application for containerization

  - Copy the existing Pipecat application files to a new deployment directory
  - Add health check endpoint to the FastAPI server for ECS monitoring
  - Update Dockerfile with security improvements and proper health checks
  - _Requirements: 1.1, 5.1, 5.2, 5.3_

- [x] 2. Create improved Dockerfile for ECS deployment

  - Modify existing Dockerfile to use non-root user for security
  - Add health check configuration for ECS monitoring
  - Optimize image layers and add proper signal handling
  - _Requirements: 1.1, 6.1_

- [x] 3. Set up AWS infrastructure with CDK

  - Create CDK project structure for infrastructure as code
  - Define VPC, subnets, and security groups for ECS deployment
  - Configure ECR repository for container image storage
  - _Requirements: 2.1, 2.2, 3.1_

- [x] 4. Implement ECS cluster and service configuration

  - Create ECS cluster definition using AWS Fargate
  - Define ECS task definition with proper resource allocation and IAM roles
  - Configure ECS service with auto-scaling and health check settings
  - _Requirements: 1.4, 2.1, 2.3_

- [x] 5. Configure Application Load Balancer

  - Create ALB with internet-facing configuration
  - Set up target group pointing to ECS tasks on port 7860
  - Configure health check routing to the new /health endpoint
  - _Requirements: 2.4, 1.3_

- [x] 6. Set up AWS Secrets Manager integration

  - Create secrets in AWS Secrets Manager for Daily API key and AWS credentials
  - Configure ECS task definition to inject secrets as environment variables
  - Update application to handle secrets from environment variables
  - _Requirements: 2.3, 6.4_

- [x] 6.1 Verify Bedrock model access and permissions

  - Test Amazon Nova Sonic model access from the deployment environment
  - Verify IAM roles have proper Bedrock permissions for the ECS tasks
  - Test model invocation with sample requests to ensure connectivity
  - _Requirements: 5.2, 6.3_

- [x] 7. Create deployment scripts and CI/CD pipeline

  - Write build script to create and push Docker image to ECR
  - Create deployment script to update ECS service with new image
  - Set up basic GitHub Actions workflow for automated deployment
  - _Requirements: 3.2, 3.3_

- [x] 8. Implement monitoring and logging

  - Configure CloudWatch log groups for ECS task logging
  - Set up basic CloudWatch metrics for ECS service monitoring
  - Add structured logging to the application for better observability
  - _Requirements: 3.4_

- [x] 9. Test containerized application locally

  - Build Docker image locally and test functionality
  - Verify health check endpoint responds correctly
  - Test complete user flow including Daily WebRTC and Nova Sonic integration
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 10. Deploy and test in AWS ECS

  - Deploy infrastructure using CDK to AWS account
  - Build and push container image to ECR
  - Deploy ECS service and verify tasks start successfully
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 11. Validate end-to-end functionality

  - Test complete user journey through ALB DNS name
  - Verify Daily WebRTC connections work from cloud deployment
  - Test Nova Sonic speech processing functionality
  - Validate function calling (weather API) works correctly
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 12. Create documentation and cleanup
  - Document deployment process and configuration
  - Create troubleshooting guide for common issues
  - Add cleanup scripts for tearing down test infrastructure
  - _Requirements: 3.1, 4.4_

## Twilio Phone Integration Tasks

- [x] 13. Set up Twilio account and phone number (MANUAL CONFIGURATION REQUIRED)

  - **YOU NEED TO DO**: Create Twilio account at https://www.twilio.com/try-twilio
  - **YOU NEED TO DO**: Purchase Twilio phone number with voice capabilities
  - **YOU NEED TO DO**: Generate API keys in Twilio console (Account SID, API SID, API Secret)
  - **YOU NEED TO DO**: Note down your Twilio phone number for testing
  - Test basic Twilio API connectivity from local environment
  - _Requirements: 7.1, 9.1_

- [x] 14. Implement Twilio webhook endpoints

  - Add `/incoming-call` POST endpoint to handle inbound call webhooks
  - Implement TwiML response generation for media stream connection
  - Remove webhook signature validation (simplified for testing)
  - _Requirements: 8.1, 8.2_

- [x] 16. Integrate Twilio SDK and configuration

  - Add Twilio Python SDK to requirements.txt
  - Implement Twilio client initialization with credentials from Secrets Manager
  - Add environment variable handling for Twilio configuration
  - Create helper functions for TwiML generation (inbound calls only)
  - _Requirements: 9.2, 9.3_

- [x] 17. Create separate container image for server_clean.py

  - Create new Dockerfile specifically for server_clean.py phone service
  - Add all required dependencies including Twilio SDK to requirements.txt
  - Build and test container locally with server_clean.py
  - _Requirements: 1.1, 7.1_

- [x] 18. Add Twilio credentials to AWS Secrets Manager

  - Create new secret for Twilio credentials (Account SID, Auth Token, Phone Number)
  - Store credentials securely for the phone service to access
  - Test secret creation and access permissions
  - _Requirements: 9.1, 9.2_

- [x] 19. Create separate ECS service for phone calls

  - Create new ECS task definition for server_clean.py phone service
  - Configure separate ECS service with appropriate scaling settings
  - Set up IAM roles with Bedrock, Secrets Manager, and Daily.co permissions
  - _Requirements: 1.4, 2.1, 7.4_

- [x] 20. Create separate ALB for phone service

  - Deploy new Application Load Balancer for phone service
  - Configure target group pointing to phone service ECS tasks
  - Set up security groups to allow HTTP traffic from Twilio webhooks
  - _Requirements: 2.4, 8.1, 9.4_

- [ ] 21. Deploy phone service to separate ECS infrastructure

  - Push phone service container image to separate ECR repository
  - Deploy new ECS service with server_clean.py
  - Verify phone service starts successfully and passes health checks
  - Test that both web service and phone service run independently
  - _Requirements: 1.1, 1.2, 7.4_

- [ ] 22. Implement comprehensive phone call testing

  - Test inbound call flow from Twilio number to Nova Sonic
  - Test error handling for failed calls and network issues
  - Validate weather function calling through voice commands
  - _Requirements: 7.1, 10.4_

- [ ] 23. Configure Twilio webhook URL (MANUAL CONFIGURATION REQUIRED)

  - **YOU NEED TO DO**: Get phone service ALB DNS name after deployment
  - **YOU NEED TO DO**: In Twilio console, configure phone number webhook URL to `http://YOUR-PHONE-ALB-DNS/incoming-call`
  - **YOU NEED TO DO**: Set webhook method to POST
  - Test webhook delivery from Twilio to your phone service
  - _Requirements: 9.3, 9.4_

- [ ] 24. Create Twilio integration documentation
  - Document Twilio setup and configuration process
  - Create troubleshooting guide for phone call issues
  - Add monitoring and logging guidance for phone calls
  - _Requirements: 3.1, 11.1, 11.2_
