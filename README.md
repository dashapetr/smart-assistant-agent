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

### Step 0: Create Telegram bot and obtain token

Go to Telegram bot father, [create bot](https://core.telegram.org/bots/features#creating-a-new-bot) and save the token. 
Be careful with the token and save it in a safe place. We will use it when getting message updates.

Add your bot to chat(s) from where you want to receive updates. 

### Step 1: Create Lambda Function

Lambda Function will manage all the logic required for the agent actions.
Code contains set of APIs that Bedrock agent will call. The function will then format the response and send it back to the agent.

As per March 2024, [Bedrock agents are available in the following regions:](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-supported.html)
- US East (N. Virginia)
- US West (Oregon)

That's it might be a good idea to create Lambda Function in the same region where we are planning to create an agent (to avoid cross-region data transfer costs).

#### Create Lambda:

1. Navigate to the [Lambda Console](https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/functions) and click on `Create function` button.
2. Paste `ChatSummarizer` as a function name and choose `Python 3.12` as a runtime
3. Click on Create function button in the bottom of the page

#### Update permissions:
Note: IAM permissions

#### Add environmental variables:
configuration, environmental variables, 

#### Adjust the timeout:

#### Add code:
How to package Lambda using simple commands.

#### Test your Lambda:

Based on the Bedrock documentation, here is how request payload looks like.
Create test events to test your Lambda

### Step 2: Add openapi file to S3

Upload openapi file to S3

### Step 3: Configure Bedrock agent

Go to Bedrock and create agent. Mind the region!
Make sure that claude model is enabled

### Step 4: Test it out!

Note: 24 hours window

## Conclusion and more ideas: 