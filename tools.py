import json
import os
import requests
import boto3
from typing import Union

from fuzzywuzzy import process

BOT_TOKEN = os.environ['BOT_TOKEN']
DEFAULT_CHAT_ID = os.environ['DEFAULT_CHAT_ID']
TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']


def get_updates() -> Union[dict, None]:
    """
    Fetches updates (last 24 hours) from the Telegram bot API.

    Returns:
        Union[dict, None]: A dictionary containing the updates if the request
        is successful, otherwise None.
    """
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching updates: {response.status_code}")
        return None


def ask_model(messages: str, instructions: str) -> str:
    """
    Generates responses from a language model based on chat messages and instructions.

    Args:
        messages (str): The chat messages to be used as context for generating responses.
        instructions (str): Additional instructions or question to provide to the model.

    Returns:
        str: The generated response from the language model.
    """
    if not messages:
        return "No messages was found. Consider using other chat."

    prompt = instructions + str(messages)

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

    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1'
    )

    model_id = "amazon.titan-text-lite-v1"
    accept = "application/json"
    content_type = "application/json"

    response = bedrock_runtime.invoke_model(
        body=body, modelId=model_id, accept=accept, contentType=content_type
    )
    response_body = json.loads(response.get("body").read())

    results = response_body.get("results")[0].get("outputText")
    return results


def get_chat_id(bot_id: str, chat_name: str,
                default_id=DEFAULT_CHAT_ID) -> str:
    """
    Retrieves the chat ID based on the bot ID and chat name.
    Chat name could be not exact: the function performs fuzzy search.

    Args:
        bot_id (str): The ID of the bot.
        chat_name (str): The name of the chat to retrieve the ID for.
        default_id (str, optional): The default chat ID to return
           if no match is found. Defaults to DEFAULT_CHAT_ID.

    Returns:
        str: The chat ID corresponding to the provided bot ID and
           chat name, or the default ID if no match is found.
    """
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')
    table_name = TABLE_NAME

    response = dynamodb.get_item(
        TableName=table_name,
        Key={
            'agent_id': {'S': bot_id}
            }
    )

    chats = response['Item'].get('chats', {}).get('L', [])
    chat_names = [chat.get('M', {}).get('chat_name', {}).get('S', '') for chat in chats]
    closest_match = process.extractOne(chat_name, chat_names)

    if closest_match:
        closest_name, score = closest_match
        if score >= 70:
            for chat in chats:
                chat_details = chat.get('M', {})
                if chat_details.get('chat_name', {}).get('S') == closest_name:
                    return chat_details.get('chat_id', {}).get('S')
        print(f"No close match found for the chat name '{chat_name}'.")
        return default_id
    return default_id


def format_messages(chat_id: str, updates: dict) -> str:
    """
    Formats messages from the Telegram updates, filters messages
    based on the provided chat ID.

    Args:
        chat_id (str): The ID of the chat to filter messages for.
        updates (dict): The Telegram updates dictionary.

    Returns:
        str: A formatted string containing messages from the updates
           for the specified chat ID.
    """
    messages = ''
    if updates and 'result' in updates:
        for update in updates['result']:
            print(update)
            if 'message' in update and 'text' in update['message'] \
                    and 'link_preview_options' not in update['message'] \
                    and str(update['message']['chat']['id']) == chat_id:
                message_text = update['message']['text']
                message_text = message_text.replace('\n', " ")
                sender = update['message']['from']['username']
                messages += f"{sender}: {message_text}, "
    return messages
