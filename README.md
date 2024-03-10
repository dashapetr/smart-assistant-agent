# AI Telegram Chat assistant with Amazon Bedrock agent.

Welcome to building Generative AI Telegram Chat Agent using Amazon Bedrock Agents. 


![Agent Architecture Diagram](/images/agent_architecture.png)

## What Chat Assistant Can Do

Demo gif here

### 1- Get latest chat updates:

### 2 - Translate messages:

### 3 - Summarize messages and extract action points:

### 4 - Query chats based on a custom prompt:


## Let's build!

### Step 0: Create Telegram bot and obtain token

Go to Telegram bot father, create bot and save the token. 
Be careful with the token and save it in a safe place.


### Step 1:  Create Lambda Function

As per March 2024, Bedrock agents are available in the following regions:
Documentation link.
That's why we will create Lambda in the same region
Note: region, IAM permissions
Runtime, configuration, environmental variables, 
How to package Lambda using simple commands.

### Step 2:  Add openapi file to S3

Upload openapi file to S3

### Step 3:  Configure Bedrock agent

Go to Bedrock and create agent. Mind the region!
Make sure that claude model is enabled

### Step 4:  Test it out!

Note: 24 hours window

## Conclusion and more ideas: 