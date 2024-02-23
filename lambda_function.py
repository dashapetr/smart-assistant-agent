import json
import boto3
import requests
import os

# todo: custom prompt as a question: add api endpoint
# todo: pull from a specific chat

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
    if not messages:
        return "No messages was found. Consider using other chat."
    prompt = str(
        messages) + "\n\nGiven messages extracted from the chat, summarize the chat and extract my action points."

    prompt_config = {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 1000,
            "stopSequences": [],
            "temperature": 1,
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


def translate_messages(parameters):
    messages = next(item["value"] for item in parameters if item["name"] == "messages")
    source_lang = next(item["value"] for item in parameters if item["name"] == "sourceLanguage")
    if not messages:
        return "No messages was found. Consider using other chat."
    client = boto3.client('translate', region_name='us-east-1')

    response = client.translate_text(
            Text=messages,
            SourceLanguageCode=source_lang,  # Automatically detect the source language
            TargetLanguageCode='en'  # Translate to English
        )

    translated_message = response['TranslatedText']

    return translated_message


def detect_language(messages):
    if not messages:
        return "No messages was found. Consider using other chat."
    comprehend = boto3.client('comprehend')

    response = comprehend.detect_dominant_language(Text=messages)
    detected_language = response['Languages'][0]['LanguageCode']

    return detected_language


def get_updates():
    # can see 24 h only
    url = f'https://api.telegram.org/bot{bot_token}/getUpdates'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching updates: {response.status_code}")
        return None


# Main function to process updates
def pull_messages(parameters):
    updates = get_updates()
    messages = ''
    if updates and 'result' in updates:
        for update in updates['result']:
            print(update)
            if 'message' in update and 'text' in update['message']\
                    and 'link_preview_options' not in update['message']:
                message_text = update['message']['text']
                message_text = message_text.replace('\n', "")
                sender = update['message']['from']['username']
                messages += f"{sender}: {message_text}, "
    return messages


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

    if api_path == '/pull-messages':
        body = pull_messages(parameters)
        response_body = {"application/json": {"body": str(body)}}
        response_code = 200
    elif api_path == '/detect-language':
        if not parameters:
            parameters = event['requestBody']['content']['application/json']['properties'][0]['value']
        body = detect_language(parameters)
        response_body = {"application/json": {"body": str(body)}}
        response_code = 200
    elif api_path == '/translate':
        if not parameters:
            parameters = event['requestBody']['content']['application/json']['properties']
        body = translate_messages(parameters)
        response_body = {"application/json": {"body": str(body)}}
        response_code = 200
    elif api_path == '/summarize':
        if not parameters:
            parameters = event['requestBody']['content']['application/json']['properties'][0]['value']
        body = summarize_messages(parameters)
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
