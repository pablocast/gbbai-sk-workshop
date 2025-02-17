import os
import json
from botbuilder.core import ConversationState, TurnContext, UserState
from botbuilder.schema import ChannelAccount
from botbuilder.dialogs import Dialog
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    AzureChatPromptExecutionSettings,
    ExtraBody,
)
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from data_models import ConversationData
from .state_management_bot import StateManagementBot
from utils import replace_citations
from typing import TypedDict
from typing import Annotated

# 1. Import Plugins
from plugins.Search import search as search_plugin
from plugins.DebitAccount import debit_account as debit_account_plugin
from plugins.CreditCard import credit_card as credit_card_plugin

class SemanticKernelBot(StateManagementBot):

    def __init__(self, conversation_state: ConversationState, user_state: UserState, dialog: Dialog):
        super().__init__(conversation_state, user_state, dialog)
        self.welcome_message = os.getenv("LLM_WELCOME_MESSAGE", "¡Hola y bienvenido al Banco Nacional de Costa Rica! ¿En qué puedo ayudarte hoy?")

    @staticmethod
    def to_json(obj):
        return json.dumps(obj, default=lambda obj: obj.__dict__)


    # Modify onMembersAdded as needed
    async def on_members_added_activity(self, members_added: list[ChannelAccount], turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(self.welcome_message)

    async def on_message_activity(self, turn_context: TurnContext):
        # Load conversation state
        conversation_data = await self.conversation_data_accessor.get(turn_context, ConversationData([]))

        # Add user message to history
        conversation_data.add_turn("user", turn_context.activity.text)
        
        # 2.Create a new kernel
        kernel = sk.Kernel()
      
        # 3.Add Azure Chat service 
        credential = DefaultAzureCredential()

        chat_service = AzureChatCompletion(
            service_id="chat-gpt",
            ad_token_provider=get_bearer_token_provider(
                credential, 
                "https://cognitiveservices.azure.com/.default"
            ),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            deployment_name=os.getenv("AZURE_OPENAI_GPT4o_DEPLOYMENT"),
        )

        kernel.add_service(chat_service)
        
        ## 4. Add Plugins 
        kernel.add_plugin(
            search_plugin.SearchService(
                service_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
                index_name=os.getenv("AZURE_SEARCH_INDEX_NAME")
            ), 
            plugin_name="SearchPlugin"
        )

        kernel.add_plugin(
            debit_account_plugin.DebitAccountService(
                database=os.getenv("AZURE_POSTGRES_DATABASE"),
                user=os.getenv("AZURE_POSTGRES_USER"),
                password=os.getenv("AZURE_POSTGRES_PASSWORD"),
                host=os.getenv("AZURE_POSTGRES_SERVER")
            ),
            plugin_name="DebitAccountPlugin"
        )

        kernel.add_plugin(
            credit_card_plugin.CreditCardService(),
            plugin_name="CreditCardPlugin"
        )

        path =  os.path.join(os.path.dirname(__file__), "../plugins")
        kernel.add_plugin(
            None,
            parent_directory=path, 
            plugin_name="Recommender",
            description="Recomendar un producto financiero",
        )
        
        # 6. Add ChatCompletionAgent
        settings = kernel.get_prompt_execution_settings_from_service_id(service_id="chat-gpt")
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
        
        instructions_path = os.path.join(os.path.dirname(__file__), "instructions.jinja")
        instructions = open(instructions_path, "r").read()
        
        agent = ChatCompletionAgent(
            service_id="chat-gpt",
            kernel=kernel,
            name='agente',
            instructions=instructions,
            execution_settings=settings            
        )

        # 6. Add user input to the history
        history = ChatHistory()
        for message in conversation_data.history:
            if message.role == "user":	
                history.add_user_message(message.content)
            else:
                history.add_assistant_message(message.content)

        # 7. Get the response from the AI with automatic function calling
        async for response in agent.invoke(history):
            conversation_data.add_turn("assistant", response.content)

        # Respond back to user
        await turn_context.send_activity(response.content)
