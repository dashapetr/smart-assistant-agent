import boto3
import os

from tools import ask_model, get_chat_id, get_updates, format_messages

BOT_ID = os.environ['BOT_ID']


def summarize_messages(parameters: list) -> str:
    """
    Summarizes messages extracted from a chat.

    Args:
        parameters (list): A list of dictionaries containing parameters
            related to the chat. Each dictionary contains 'name' and 'value'
            keys, where 'name' represents the parameter name and 'value'
            represents the parameter value.

    Returns:
        str: A summary of the chat and extracted action points.
    """
    messages = next(item["value"] for item in parameters if item["name"] == "messages")
    instructions = "Given the messages extracted from the chat, summarize.\n"
    return ask_model(messages, instructions)


def query_chat(parameters: list) -> str:
    """
    Queries the chat based on the custom prompt.

    Args:
        parameters (list): A list of dictionaries containing parameters
            related to the chat. Each dictionary contains 'name' and 'value'
            keys, where 'name' represents the parameter name and 'value'
            represents the parameter value.

    Returns:
        str: A chat-based answer to the custom prompt.
    """
    messages = next(item["value"] for item in parameters if item["name"] == "messages")
    custom_prompt = next(item["value"] for item in parameters if item["name"] == "customPrompt")
    instructions = f"Given messages extracted from the chat, " \
                   f"answer the following question: {custom_prompt} \n"
    return ask_model(messages, instructions)


def translate_messages(parameters: list) -> str:
    """
    Translates messages from a specified source language to English.

    Args:
        parameters (list): A list of dictionaries containing parameters
            related to the translation. Each dictionary contains 'name' and 'value'
            keys, where 'name' represents the parameter name and 'value'
            represents the parameter value.

    Returns:
        str: Translated messages in English.
    """
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


def detect_language(parameters: list) -> str:
    """
    Detects the language of messages.

    Args:
        parameters (list): A list of dictionaries containing parameters
            related to the chat. Each dictionary contains 'name' and 'value'
            keys, where 'name' represents the parameter name and 'value'
            represents the parameter value.

    Returns:
        str: Language code, for example 'pl'.
    """
    messages = next(item["value"] for item in parameters if item["name"] == "messages")
    if not messages:
        return "No messages was found. Consider using other chat."
    comprehend = boto3.client('comprehend')

    response = comprehend.detect_dominant_language(Text=messages)
    detected_language = response['Languages'][0]['LanguageCode']

    return detected_language


def pull_messages(parameters: list) -> str:
    """
    Gets messages updates from a specific chat.

    Args:
        parameters (list): A list of dictionaries containing parameters
            related to the chat. Each dictionary contains 'name' and 'value'
            keys, where 'name' represents the parameter name and 'value'
            represents the parameter value.

    Returns:
        str: Pulled messages from a specific chat.
    """
    chat_name = next(item["value"] for item in parameters if item["name"] == "chatName")
    chat_id = get_chat_id(BOT_ID, chat_name)
    updates = get_updates()
    messages = format_messages(chat_id, updates)
    return messages


def lambda_handler(event: dict, context: object) -> dict:
    """
    Lambda function handler to process incoming API requests.

    Args:
        event (dict): The event data passed to the lambda function.
        context (object): The runtime information of the lambda function.

    Returns:
        dict: A dictionary containing the response data to be returned
           by the lambda function.

    """
    print("Received event: ")
    print(event)

    response_code = None
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

    print(f"Response body: {response_body}")

    action_response = {
        "actionGroup": action,
        "apiPath": api_path,
        "httpMethod": http_method,
        "httpStatusCode": response_code,
        "responseBody": response_body,
    }

    api_response = {"messageVersion": "1.0", "response": action_response}

    return api_response
