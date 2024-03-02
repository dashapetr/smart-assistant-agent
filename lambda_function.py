import boto3
import os

from tools import ask_model, get_chat_id, get_updates, format_messages

BOT_ID = os.environ['BOT_ID']


def summarize_messages(parameters):
    messages = next(item["value"] for item in parameters if item["name"] == "messages")
    instructions = "Given messages extracted from the chat, summarize the chat and extract my action points.\n"
    return ask_model(messages, instructions)


def query_chat(parameters):
    messages = next(item["value"] for item in parameters if item["name"] == "messages")
    custom_prompt = next(item["value"] for item in parameters if item["name"] == "customPrompt")
    instructions = f"Given messages extracted from the chat, answer the following question: {custom_prompt} \n"
    return ask_model(messages, instructions)


def translate_messages(parameters):
    messages = next(item["value"] for item in parameters if item["name"] == "messages")
    source_lang = next(item["value"] for item in parameters if item["name"] == "sourceLanguage")
    if not messages:
        return "No messages was found. Consider using other chat."
    client = boto3.client('translate', region_name='us-east-1')

    response = client.translate_text(
            Text=messages,
            SourceLanguageCode=source_lang,
            TargetLanguageCode='en'
        )

    translated_message = response['TranslatedText']

    return translated_message


def detect_language(parameters):
    messages = next(item["value"] for item in parameters if item["name"] == "messages")
    if not messages:
        return "No messages was found. Consider using other chat."
    comprehend = boto3.client('comprehend')

    response = comprehend.detect_dominant_language(Text=messages)
    detected_language = response['Languages'][0]['LanguageCode']

    return detected_language


def pull_messages(parameters):
    chat_name = next(item["value"] for item in parameters if item["name"] == "chatName")
    chat_id = get_chat_id(BOT_ID, chat_name)
    updates = get_updates()
    messages = format_messages(chat_id, updates)
    return messages


def lambda_handler(event, context):
    print("Received event: ")
    print(event)

    # Initialize response code to None
    response_code = None

    # Extract the action group, api path, and parameters from the prediction
    action = event["actionGroup"]
    api_path = event["apiPath"]
    parameters = event.get("parameters", None)
    if not parameters:
        parameters = event['requestBody']['content']['application/json']['properties']
    http_method = event["httpMethod"]

    if api_path == '/pull-messages':
        body = pull_messages(parameters)
        response_body = {"application/json": {"body": str(body)}}
        response_code = 200
    elif api_path == '/detect-language':
        body = detect_language(parameters)
        response_body = {"application/json": {"body": str(body)}}
        response_code = 200
    elif api_path == '/translate':
        body = translate_messages(parameters)
        response_body = {"application/json": {"body": str(body)}}
        response_code = 200
    elif api_path == '/summarize':
        body = summarize_messages(parameters)
        response_body = {"application/json": {"body": str(body)}}
        response_code = 200
    elif api_path == '/query-chat':
        body = query_chat(parameters)
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
