import json
import time
import boto3
import requests
import os
import datetime
import ast

bot_token = os.environ['BOT_TOKEN']
group_chat_id = os.environ['GROUP_CHAT_ID']

# Bedrock client used to interact with APIs around models
bedrock = boto3.client(
    service_name='bedrock',
    region_name='us-east-1'
)

# Bedrock Runtime client used to invoke and question the models
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)


def summarize_messages(messages):
    prompt = str(
        messages) + "\n\nGiven messages extracted from the chat, summarize the chat and extract my action points."

    prompt_config = {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 4096,
            "stopSequences": [],
            "temperature": 0.7,
            "topP": 1,
        },
    }

    body = json.dumps(prompt_config)

    modelId = "amazon.titan-text-lite-v1"
    accept = "application/json"
    contentType = "application/json"

    response = bedrock_runtime.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())

    print(response_body)

    results = response_body.get("results")[0].get("outputText")
    return results


def translate_messages(messages):
    client = boto3.client('translate', region_name='us-east-1')
    messages_payload = ast.literal_eval(messages) if isinstance(messages, str) else messages

    for message in messages_payload:
        response = client.translate_text(
            Text=message["content"],
            SourceLanguageCode='auto',  # Automatically detect the source language
            TargetLanguageCode='en'  # Translate to English
        )

        translated_message = response['TranslatedText']
        message["translated_content"] = translated_message

    return messages_payload


def get_current_date():
    return time.strftime("%Y-%m-%d")


def get_updates():
    url = f'https://api.telegram.org/bot{bot_token}/getUpdates'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching updates: {response.status_code}")
        return None


# Main function to process updates
def pull_messages():
    updates = get_updates()
    messages = []
    if updates and 'result' in updates:
        for update in updates['result']:
            print(update)
            if 'message' in update and 'text' in update['message']\
                    and 'link_preview_options' not in update['message']:
                message_text = update['message']['text']
                message_text = message_text.replace('\n', "")
                sender = update['message']['from']['username']
                date = update['message']['date']
                date = datetime.datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')
                messages.append({"sender": sender, "content": message_text, "timestamp": date})
    return messages


def translate_summarize_messages(messages):
    translated_messages = translate_messages(messages)
    for message in translated_messages:
        del message["content"]
    print(translated_messages)
    return summarize_messages(translated_messages)


def lambda_handler(event, context):
    # Print the received event to the logs
    print("Received event: ")
    print(event)

    # Initialize response code to None
    response_code = None

    # Extract the action group, api path, and parameters from the prediction
    action = event["actionGroup"]
    api_path = event["apiPath"]
    parameters = event.get("parameters", None)
    input_text = event["inputText"]
    http_method = event["httpMethod"]

    print(f"inputText: {input_text}")

    if api_path == '/current-date':
        body = get_current_date()
        response_body = {"application/json": {"body": str(body)}}
        response_code = 200
    elif api_path == '/pull-messages':
        body = pull_messages()
        response_body = {"application/json": {"body": str(body)}}
        response_code = 200
    elif api_path == '/translate-summarize':
        body = translate_summarize_messages(parameters)
        response_body = {"application/json": {"body": str(body)}}
        response_code = 200
    else:
        body = {"{}::{} is not a valid api, try another one.".format(action, api_path)}
        response_code = 400
        response_body = {"application/json": {"body": str(body)}}

    # Print the response body to the logs
    print(f"Response body: {response_body}")

    # Create a dictionary containing the response details
    action_response = {
        "actionGroup": action,
        "apiPath": api_path,
        "httpMethod": http_method,
        "httpStatusCode": response_code,
        "responseBody": response_body,
    }

    # Return the list of responses as a dictionary
    api_response = {"messageVersion": "1.0", "response": action_response}

    return api_response
