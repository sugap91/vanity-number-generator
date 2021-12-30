# vanity-number-generator

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#provisioning-cloud-resources">Provisioning Cloud Resources</a></li>
        <li><a href="#amazon-connect-contact-flow">Amazon Connect Contact Flow</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This project is built to generate vanity numbers for the customer phone number using AWS resources.


### Built With

The project is built using,
* AWS resources
    - Amazon Connect
    - AWS Lambda
    - Amazon CloudWatch
    - DynamoDB
    - IAM Roles and Policies
    - CloudFormation
* Python 3.6.8


<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

1. AWS account with an Amazon Connect instance provisioned in it.
2. Create a S3 bucket in the same region as the connect instance and the Lambda function.
3. Clone the git repository and upload the /lambda-function/contacts.zip file to the created S3 bucket.

### Provisioning Cloud Resources

1. Navigate to the AWS CloudFormation section in the same region and create a new stack.
2. Use the /infrastructure/cf_template.yaml within the repository to create the stack.
3. Bucket name (where the contacts.zip file has been uploaded) has to be provided as the input.
4. The stack will provision the Lambda function, DynamoDB table and the required IAM role and policy.

### Amazon Connect Contact Flow

1. Navigate to the Amazon Connect instance and attach the newly created Lambda function (contacts_vanity-number-generator) to the contact flows. (This will add the required permissions for the connect instance to invoke the Lambda function).
2. Login to the Amazon Connect instance as Administrator and navigate to the contact flows section.
3. Import the contact flow (/contact-flow/VanityNumberGenerator). Before importing, replace the #REGION# and #ßACCOUNTID# strings with the account id and region of your AWS account.


<!-- USAGE EXAMPLES -->
## Usage

1. Claim a new phone number under the Manager Phone numbers section in the Amazon Connect instance.
2. Attach the Vanity Number Generator contact flow to the phone number.
3. Dial the number from your mobile to listen to the possible vanity numbers for your phone number.
