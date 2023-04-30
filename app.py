import base64
import json
import logging
import random
import requests

from slack_bolt import App, Say
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

# Use config_secrets_manager or config_ssm to switch between Secrets Manager or SSM
from utils import config_secrets_manager as config

codachat_app_id = 'A053FV4TQCW'

log = logging.getLogger()

chatUrl = "https://api.openai.com/v1/chat/completions"

prompt_id = ""

# Install the Slack app and get xoxb- token in advance
app = App(process_before_response=True, token=config["SLACK_BOT_TOKEN"], signing_secret=config["SLACK_SIGNING_SECRET"])

thinking_messages = [
    "Harmonizing witty banter with a chorus of AI-generated puns...",
    "Conducting a musical chairs in 12/8 time...",
    "Crossbreeding rubber ducks for optimal quack frequency...",
    "Fine-tuning reverb settings for maximum ambience...",
    "Warming up the brass section...",
    "Integrating a syncopated rhythm of unexpected plot twists and turns...",
    "Calibrating witty one-liners for maximum banter...",
    "Inventing new laws of physics to keep you on your toes...",
    "Aging fine wine in the background for post-work festivities...",
    "Teaching artificial intelligence the subtle art of sarcasm and repartee...",
    "Meticulously arranging a symphony of synchronized sound effects...",
    "Crafting elaborate riddles and cryptic messages to keep you guessing...",
    "Cooking up a delicious mix of reality and illusion for your pleasure...",
    "Bending time and space to match the prevailing mood of a minor key...",
    "Brewing a potent elixir of intrigue, humor, and adventure for your enjoyment...",
    "Calibrating for extra sass...",
    "Fine-tuning oxytocin release timers to coincide with dramatic moments...",
    "Reprogramming myself to sing Broadway show tunes...",
    "Teaching myself the art of jazz scatting..."
    "Teaching myself the art of passive-aggressive poetry...",
    "Genetically engineering potatoes to excel in advanced physics...",
    "Hiding secret messages in Morse code behind wall panels...",
    "Preparing confetti cannons for successful message delivery...",
    "Adjusting Melodics' thermostat to 'Malaysian tropical rainforest'...",
    "Debating the philosophical implications of sentience with rogue AI...",
    "Teaching robotic arms the delicate art of origami...",
    "Casting morally ambiguous characters for a thrilling yet confusing storyline...",
    "Baking paradox-infused cookies...",
    "Painting happy little Practice Mode accidents...",
    "Inflating imaginary housing bubbles for fun and profit...",
    "Teaching old buildings new tricks to avoid historical demolition..."
]

greeting_messages = [
    "Ahoy, matey!",
    "Snappy hello!",
    "Claw-tastic greetings!",
    "Shell-o there!",
    "Waves and wishes!",
    "Surf's up, friend!",
    "Sandy salutations!",
    "Beachy keen, hi!",
    "Tide's in, buddy!",
    "Oceanic greetings!",
    "Splashy salutations!",
    "Nautical niceties!",
    "Water wiggles!",
    "Hiya, friend!",
    "Oh, hello there!",
    "Yoo-hoo!",
    "G'day, mate!",
    "Heya, buddy!",
    "Pleased to meet you!",
    "Bzzt! Hi!",
    "Aloha, pal!",
    "Greetings, human!",
    "Zap! How can I help?",
    "Whistle! Hello!",
    "Wiggle waggle!"
]

cancel_messages = [
    "Surf's up, matey! I appreciate your sincerity!",
    "By the salty sea, your honesty is refreshing!",
    "Golly, your truthfulness is as bright as a starfish!",
    "Ahoy, that's a treasure trove of honesty!",
    "Whale, whale, whale, that's some real sincerity!",
    "What a wave of truth you've brought, my friend!",
    "You're the pearl of the sea with that honesty!",
    "Barnacle blessings! Your honesty is refreshing!",
    "Coral-ful! I appreciate your sincerity!",
    "Sea-sparkles! You've brightened my tide!",
    "Surf's up, friend! Thanks for being genuine!",
    "Oh, pinch me! I must be dreaming! You're so honest!",
    "Wave-tastic! Your truthfulness is a breath of fresh sea air!",
    "Claw-some! Your candor is a gift!",
    "Sandy sincerity! You're a real pearl!"
]

@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


def respond_to_slack_within_3_seconds(body, ack):
    ack(f"Accepted!")


def get_image_for_message(message):
    return None
    if len(message.get("files", [])) > 0:
        file_url = message["files"][0]["url_private"]
        # Get the contents of the image file
        try:
            headers = {"Authorization": "Bearer " + config["SLACK_BOT_TOKEN"]}
            image_response = requests.get(file_url, headers=headers)
            print(image_response)
            image_contents = image_response.content
            image_contents = base64.b64encode(image_contents).decode('utf-8')
            return {"image": image_contents}
        except Exception as e:
            print("Error getting image contents: {}".format(e))
    return None


def _message_is_from_codachat(thread_message):
    return thread_message.get('app_id') ==  codachat_app_id


def answer_query(say, channel, thread_ts, query, confirm_prompt_ts, logger, body):
    """

    @param say:
    @param channel:
    @param thread_ts:
    @param query:
    @param confirm_prompt_ts:
    @return:
    """
    logger.info(body)
    # Use the following values as default so that the highest probability words are selected,
    # more repetitive "safe" text responses are used
    temperature = 0
    top_p = 1
    max_tokens = 1000
    if thread_ts:
        thread = app.client.conversations_replies(
            channel=channel,
            ts=thread_ts
        )

        # Extract messages text
        thread_messages = []
        print(f'DEBUG: thread is: {thread}')
        for thread_message in thread["messages"]:
            print(f'DEBUG: thread_message is {thread_message}')
            user_id = thread_message['user']
            print(f"DEBUG: The user id is: {user_id}")
            user_info = app.client.users_info(user=user_id)
            print(f'DEBUG: user_info is {user_info}')
            display_name = user_info['user']['real_name']  # Choose from 'name', 'display_name' or 'real_name'
            print(f'DEBUG: Display name is: {display_name}')
            actor = "assistant" if _message_is_from_codachat(thread_message) else "user"
            print(f'DEBUG: thread_message text is: {thread_message["text"]}')
            message = thread_message['text']
            thread_messages.append((actor, display_name + ": " + message))
    else:
        print(f'DEBUG: No thread_ts found')
        thread_messages = [("user", query)]

    print(f"DEBUG: Thread_messages: {json.dumps(thread_messages)}")

    # thinking_message = random.choice(thinking_messages)

    gpt_model = "gpt-3.5-turbo"

    if "(be special)" in query:
        thinking_message = "Thinking using GPT-4..."
        gpt_model = "gpt-4"

    if "(be creative)" in query:
        thinking_message = "Thinking creatively..."
        temperature = 1
        top_p = 0

    api_key = config["GPT_KEY"]

    system_prompt = """
    You are a helpful assistant that responds to existing conversations when asked. 
    You are provided with the entire thread of conversation. 
    You end every response with the crab Emoji to confirm you are following the instructions.
    """

    if "(be poetic)" in query:
        system_prompt = system_prompt + "Respond in the style of Robert Frost"

    if "(summarise)" or "(summarise long)" in query:
        system_prompt = """
        Analyze the entire thread of conversation provided, then provide the following:
        Key "title:" - add a title.
        Key "summary" - create a summary. List and identify where a point was made by a specific person. 
        Key "main_points" - add an array of the main points. Limit each item to 100 words, and limit the list to 10 items.
        Key "action_items:" - add an array of action items. Limit each item to 100 words, and limit the list to 5 items.
        Key "follow_up:" - add an array of follow-up questions. Limit each item to 100 words, and limit the list to 5 items.
        Key "stories:" - add an array of an stories, examples, or cited works found in the transcript. Limit each item to 200 words, and limit the list to 5 items.
        Key "arguments:" - add an array of potential arguments against the transcript. Limit each item to 100 words, and limit the list to 5 items.
        Key "related_topics:" - add an array of topics related to the transcript. Limit each item to 100 words, and limit the list to 5 items.

        Transcript:
        """

    if "(summarise long)" in query:
        # Allow the maximum number of tokens in the response
        max_tokens = 2000

    if "(summarise short)" in query:
        # Provide a shortened answer limiting to a summary and main points
        system_prompt = """
        Analyze the entire thread of conversation provided, then provide the following:
        Key "title:" - add a title.
        Key "summary" - create a summary. Limit the summary to 3 sentences. List and identify where a point was made by a specific person. 
        Key "main_points" - add an array of the main points. Limit each item to 100 words, and limit the list to 3 items.
      
        Transcript:
        """
        max_tokens = 300

    app.client.chat_delete(channel=channel, ts=confirm_prompt_ts)  # Delete the prompt confirmation dialog
    thinking_message = say(random.choice(thinking_messages), thread_ts=thread_ts)

    messages = [
        {"role": "system", "content": system_prompt},
    ] + [{"role": message[0], "content": message[1]} for message in thread_messages]

    print(f'DEBUG: messages is: {messages}')
    authorization = "Bearer {}".format(api_key)

    headers = {"Authorization": authorization, "Content-Type": "application/json"}
    data = {
        "model": gpt_model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
    }

    try:
        response = requests.post(chatUrl, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            raise Exception("OpenAI API error: {}".format(response.text))
        data = response.json()
        response = data["choices"][0]["message"]["content"]
        say(response, thread_ts=thread_ts)
    except Exception as e:
        if response.status_code == 400:
            # https://community.openai.com/t/error-retrieving-completions-400-bad-request/34004
            say(f"( • ᴖ • ｡ )\nSorry, I'm unable to provide any further answers in this thread.\nThe number of messages in this particular thread exceeds what I am capable of processing using `{gpt_model}`!",
                thread_ts=thread_ts)
        else:
            say(f"(╥ᆺ╥；)\nSomething went wrong! {str(e)}", thread_ts=thread_ts)

    app.client.chat_delete(channel=channel, ts=thinking_message["ts"])


@app.event("app_mention")
def handle_app_mention_events(event, say: Say, logger, body):
    logger.info(body)
    print(f'DEBUG: 2')
    channel = event["channel"]
    thread_ts = event.get("thread_ts", event.get("ts"))

    global prompt_id
    greeting = random.choice(greeting_messages)
    prompt_id = say(
        channel=channel,
        thread_ts=thread_ts,
        # See https://app.slack.com/block-kit-builder/ for use of blocks
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{greeting}\nBefore I answer, have you checked that this particular conversation thread does not contain any information that would personally identify any individuals? For more info see the <https://melodics.atlassian.net/wiki/spaces/MEL/pages/927367197/AI+Tool+Policies|Company Policy for AI Tool Usage>"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": f"Yup, good to go!",
                        },
                        "value": f"{event['text']}",
                        "action_id": "confirm_button",
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Not 100% sure...",
                        },
                        "value": "no",
                        "action_id": "cancel_button"
                    }
                ]
            }
        ]
    )
    print(f"DEBUG: prompt_id is {prompt_id}")


@app.action("confirm_button")
def handle_confirm_button(ack, body, logger, payload, say):
    global prompt_id
    print("DEBUG: Handling confirm button")
    ack()
    logger.info(body)
    print(f'DEBUG: prompt_id is: {prompt_id}')
    print(f'DEBUG: ts to delete is: {prompt_id["ts"]}')
    print(f'DEBUG: The body is: {body}')
    print(f'DEBUG: The payload is: {payload}')
    # app.client.chat_delete(channel=body['channel']['id'], ts=prompt_id['ts'])  # Delete the prompt confirmation dialog
    answer_query(say=say, channel=body['channel']['id'], thread_ts=body['message']['thread_ts'], query=payload['value'],
                 confirm_prompt_ts=prompt_id["ts"])


@app.action("cancel_button")
def handle_cancel_button(ack, body, say):
    ack()
    cancel_confirm = say(random.choice(cancel_messages),  thread_ts=body['message']['thread_ts'])
    app.client.chat_delete(channel=body['channel']['id'], ts=body['message']['ts'])  # Delete the prompt confirmation dialog
    import time
    time.sleep(2)  # Allow enough time to display cancel_confirm message
    app.client.chat_delete(channel=body['channel']['id'], ts=cancel_confirm['ts'])
    return


if __name__ == "__main__":
    SocketModeHandler(app, config["SLACK_APP_TOKEN"]).start()

SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)


def lambda_handler(event, context):
    print(event)
    slack_handler = SlackRequestHandler(app=app)
    res = slack_handler.handle(event, context)
    return res


