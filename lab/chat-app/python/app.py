# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import sys
import traceback
from http import HTTPStatus
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.cosmos.cosmos_client import CosmosClient
from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.azure import (
    CosmosDbPartitionedStorage,
    CosmosDbPartitionedConfig,
)
from botbuilder.core import (
    ConversationState,
    MemoryStorage,
    TurnContext,
    UserState,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
from botbuilder.schema import Activity

from dotenv import load_dotenv

from bot import SemanticKernelBot
from dialogs import LoginDialog
from config import DefaultConfig

load_dotenv(override=True)
config = DefaultConfig()

# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about how bots work.
adapter = CloudAdapter(ConfigurationBotFrameworkAuthentication(config))

# Catch-all for errors.
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity(
        "To continue to run this bot, please fix the bot source code."
    )
    await context.send_activity(str(error))


# Set the error handler on the Adapter.
adapter.on_turn_error = on_error

# Set up service authentication
credential = DefaultAzureCredential(managed_identity_client_id=os.getenv("MicrosoftAppId"))

# Conversation history storage
storage = MemoryStorage()

# Create conversation and user state
user_state = UserState(storage)
conversation_state = ConversationState(storage)

# Create the bot
dialog = LoginDialog()
bot = None
bot = SemanticKernelBot(conversation_state, user_state, dialog)

# Listen for incoming requests on /api/messages.
async def messages(req: Request) -> Response:
    # Parse incoming request
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    # Route received a request to adapter for processing
    response = await adapter.process_activity(auth_header, activity, bot.on_turn)
    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=HTTPStatus.OK)


app = web.Application(middlewares=[aiohttp_error_middleware])
app.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        web.run_app(app, port=3978)
    except Exception as error:
        raise error