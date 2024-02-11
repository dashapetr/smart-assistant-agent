import json
import time
import boto3
import requests
import os
import datetime

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

    for message in messages:
        response = client.translate_text(
            Text=message["content"],
            SourceLanguageCode='auto',  # Automatically detect the source language
            TargetLanguageCode='en'  # Translate to English
        )

        translated_message = response['TranslatedText']
        message["translated_content"] = translated_message

    return messages


def get_current_date():
    return time.strftime("%Y-%m-%d")


def pull_messages_test():
    return [{"sender": "Amelia", "content": "Drodzy Rodzice, oddajmy głos na prezenty dla dzieci",
             "timestamp": "2024-01-27 14:30:26.159446"},
            {"sender": "Emil", "content": "głosuję na to samo co rok temu", "timestamp": "2024-01-27 14:32:26.159446"},
            {"sender": "Margo", "content": "ja również", "timestamp": "2024-01-27 14:33:26.159446"},
            {"sender": "Ilona", "content": "kiedy musimy przynieść pieniądze?",
             "timestamp": "2024-01-27 14:35:26.159446"},
            {"sender": "Emma", "content": "do 2 lutego", "timestamp": "2024-01-27 14:39:26.159446"}]


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
            if 'message' in update and 'text' in update['message']:
                message_text = update['message']['text']
                sender = update['message']['from']['username']
                date = update['message']['date']
                date = datetime.datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')
                messages.append({"sender": sender, "content": message_text, "timestamp": date})
    return messages


def translate_summarize_messages(parameters):
    translated_messages = translate_messages(parameters)
    for message in translated_messages:
        del message["content"]
    print(translated_messages)
    return summarize_messages(translated_messages)


def lambda_handler(event, context):
    response_code = 200
    action = event['actionGroup']
    api_path = event['apiPath']

    if api_path == '/current-date':
        body = get_current_date()
    elif api_path == '/pull-messages':
        body = pull_messages()
    elif api_path == '/translate-summarize':
        parameters = event['parameters']
        body = translate_summarize_messages(parameters)
    else:
        body = {"{}::{} is not a valid api, try another one.".format(action, api_path)}

    response_body = {
        'application/json': {
            'body': str(body)
        }
    }

    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        'httpMethod': event['httpMethod'],
        'httpStatusCode': response_code,
        'responseBody': response_body
    }

    api_response = {'response': action_response}

    return api_response
