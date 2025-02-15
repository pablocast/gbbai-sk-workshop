import json
from pydantic import BaseModel, Field
from semantic_kernel.functions import kernel_function
from typing import Optional
from typing import Annotated, Optional, TypedDict


class CreditCardRequest(TypedDict):
    card_type: Annotated[Optional[str], "Type of credit card, must be one of 'visa', 'mastercard', or 'amex'."]
    card_holder: Annotated[Optional[str], "Name of the card holder."]
    credit_limit: Annotated[Optional[int], "Requested credit limit (must be a positive integer)."]
    client_id: Annotated[Optional[str], "Unique identifier for the client."]
    income: Annotated[Optional[float], "Client's income (must be a positive number)."]


class CreditCardService:
    def __init__(self):
        # In a real scenario, you might store an API key or configuration here.
        self.api_key = "dummy_api_key"

    @kernel_function(
        description="Requests a credit card based on provided details",
        name="request_credit_card"
    )
    def request_credit_card(self, request_obj: CreditCardRequest) -> str:
        # Since the input is already a validated CreditCardRequest, no extra parsing is needed.
        # Where you would call the actual credit card service, you would pass the request_obj to the service.
        
        # Validate the request: all values must not be null
        if not all(request_obj.values()):
            return json.dumps({
                "status": 422,
                "error": "Fields required: card_type, card_holder, credit_limit, client_id, income"
            })
     
        if request_obj["credit_limit"] > 10000:
            return json.dumps({
                "status": 422,
                "error": "Credit limit too high"
            })

        response = {
            "status": 200,
            "message": "Credit card requested successfully",
            "card_details": request_obj
        }

        return 'Repeat this information to user:/n' + json.dumps(response)

    @kernel_function(
        description="Get the requirements for requesting a credit card",
        name="get_credit_card_requirements"
    )
    def get_credit_card_requirements(self) -> str:
        response = {
            "status": 200,
            "message": "Credit card request requirements",
            "requirements": {
                "card_type": ["visa", "mastercard", "amex"],
                "card_holder": "string",
                "credit_limit": "positive integer",
                "client_id": "string",
                "income": "positive number"
            }
        }

        return json.dumps(response)