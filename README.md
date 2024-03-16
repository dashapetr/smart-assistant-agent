# AI Telegram Chat assistant with Amazon Bedrock agent.

Welcome to building GenAI Telegram Chat assistant using Amazon Bedrock Agents. 


![Agent Architecture Diagram](/images/agent_architecture.jpg)

## What Chat Assistant Can Do

Demo gif here

### 1- Get latest chat updates:

### 2 - Translate messages:

### 3 - Summarize messages and extract action points:

### 4 - Query chats based on a custom prompt:

## What is Bedrock Agent?

Agents for Amazon Bedrock helps you accelerate generative artificial intelligence (AI) application development by orchestrating multistep tasks.
They can make different API calls. 
Agents extend FMs to understand user requests, break down complex tasks into multiple steps, carry on a conversation to collect additional information, and take actions to fulfill the request.

- AWS News Blog: [Enable Foundation Models to Complete Tasks With Agents for Amazon Bedrock](https://aws.amazon.com/blogs/aws/preview-enable-foundation-models-to-complete-tasks-with-agents-for-amazon-bedrock/)
- AWS News Blog: [Agents for Amazon Bedrock is now available with improved control of orchestration and visibility into reasoning](https://aws.amazon.com/blogs/aws/agents-for-amazon-bedrock-is-now-available-with-improved-control-of-orchestration-and-visibility-into-reasoning/)

## Let's build!

### :zero: Step 0: Create Telegram bot and obtain token

Go to Telegram bot father, [create bot](https://core.telegram.org/bots/features#creating-a-new-bot) and save the token. 
Be careful with the token and save it in a safe place. We will use it when getting message updates.

Add your bot to chat(s) from where you want to receive updates. 

### :one: Step 1: Create DynamoDB table




### :two: Step 2: Create Lambda Function

Lambda Function will manage all the logic required for the agent actions.
Code contains set of APIs that Bedrock agent will call. The function will then format the response and send it back to the agent.

As per March 2024, [Bedrock agents are available in the following regions:](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-supported.html)
- US East (N. Virginia)
- US West (Oregon)

That's why it will be a good idea to create Lambda Function in the same region where we are planning to create an agent (to decrease cross-region latency and avoid potential cross-region data transfer costs).

#### Create Lambda:

1. Navigate to the [Lambda Console](https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/functions) and click on `Create function` button. 
Make sure that `US East (N. Virginia)` or `US West (Oregon)` is selected as region.
2. Paste `ChatSummarizer` as a function name and choose `Python 3.12` as a runtime
3. Click on Create function button in the bottom of the page

![Create Lambda Function](/images/create_lambda.jpg)

#### Update Lambda permissions:
1. Once the function is created, click on the Configuration Tab in the same page and Choose `Permissions` from the left side panel
2. Click on `Add permissions` button in Resource-based policy statement section to provide the permission to invoke lambda functions from Bedrock
3. Provide Statement Id as `agent`, Principal as `bedrock.amazonaws.com` and Action as `lambda:InvokeFunction`. Click Save after adding all the above three information.

![Lambda add permissions](/images/lambda_add_permissions.jpg)
4. Add the following Policy Statement to your Execution role, so Lambda can call Bedrock. (You can find details [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html#add-policies-console))
```{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "bedrock:InvokeModel",
            "Resource": "*"
        }
    ]
}
```
5. Add `AmazonDynamoDBReadOnlyAccess` and `TranslateReadOnly` policies to your Execution role, so Lambda can call DynamoDB, Comprehend and Translate.

![Lambda execution role permissions policies](/images/lambda_execution_role_policies.jpg)

#### Add environment variables:

1. Once permissions are updated, go back to the `ChatSummarizer` lambda, click on the `Configuration` Tab in the same page and Choose `Environment variables` from the left side panel 
2. Click `Edit` button to add environment variables
3. By clicking `Add environment variable` button add the following key value pairs:
- `BOT_ID`: `100200300` (you can change it to any unique value, make sure you use the same Id for your bot in DynamoDB table)
- `BOT_TOKEN`: insert your Telegram bot token obtained in Step 0
- `DEFAULT_CHAT_ID`: value should start from `-`, paste the Telegram chat id you want to use as default 
- `DYNAMODB_TABLE_NAME`: `bedrock_agent_chats`

![Lambda edit environment variables](/images/edit_environment_variables.jpg)

#### Adjust the timeout:

1. Choose `General configuration` from the left side panel 
2. Click on the `Edit` button
3. Modify `Timeout` by increasing it to 15 seconds to make sure your Lambda won't fail while waiting for Bedrock models to respond.
4. Click on the `Save` button

![Update Lambda timeout](/images/update_timeout.jpg)

#### Add code:

1. To use this project code, clone the repo:
```
https://github.com/dashapetr/smart-assistant-agent.git
cd smart-assistant-agent
```
2. Create a new directory named package into which you will install your dependencies.
```
mkdir package
```
3. Install your dependencies in the package directory. 
```
pip install --target ./package requests
pip install --target ./package fuzzywuzzy
```
4. Create a .zip file with the installed libraries at the root.
```
cd package
zip -r ../my_deployment_package.zip .
```
This generates a `my_deployment_package.zip` file in your project directory.

5. Add code files to the root of the .zip file
```
cd ..
zip my_deployment_package.zip lambda_function.py
zip my_deployment_package.zip tools.py
```
6. Now you can go back to the Lambda function, click on the `Code` tab in the same page 
7. Click on the `Upload from` button and select `.zip file` in the dropdown list
8. Select `my_deployment_package.zip` and upload it
9. Your code should appear inside the `Code source` window

![Lambda code](images/lambda-code.jpg)
https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-create-dependencies

#### Test your Lambda:

Based on the Bedrock documentation, here is how request payload looks like.
Create test events to test your Lambda

### :three: Step 3: Add openapi file to S3

Upload openapi file to S3

### :four: Step 4: Configure Bedrock agent

Now as all the preparation is done, we can proceed with Agent creation.
Go to Bedrock and create agent. Mind the region!
Make sure that claude model is enabled

### :five: Step 5: Test it out!

Note: Keep in mind that 24 hours window

## Conclusion and more ideas: 

Bedrock Agents would be a great choice for orchestration and automation for chains-like tasks. 
They are very flexible and easily extensible, so they can act as smart assistant in various scenarios (for example, customer support).

If you enjoyed agents, you might also like:
- [Amazon Bedrock Agents Quickstart workshop](https://github.com/build-on-aws/amazon-bedrock-agents-quickstart/tree/main) by Banjo Obayomi
- Building an Amazon Bedrock JIRA Agent with Source Code Knowledge Base - [Part 1](https://community.aws/content/2aB8MoS2mXcfRKeUbVRVVEG4AWJ/trying-out-amazon-bedrock-agents-and-knowledge-bases) and [Part 2](https://community.aws/content/2b3H2e2qcvwgustxLWb2E4VKygh/building-an-amazon-bedrock-jira-agent-with-source-code-knowledge-base) by Martyn Kilbryde
- [Shopify Customer Care powered by GenAI](https://community.aws/content/2dJUQiedCwDfOzNrbW8z9awWgxy/introducing-amazon-bedrock-agents-to-take-your-shopify-management-to-the-next-level-with-generative-ai) by Ricardo Ceci