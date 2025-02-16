import psycopg2
from psycopg2 import sql
from semantic_kernel.functions import kernel_function
from typing import Annotated, Optional, TypedDict
import os
import datetime as dt

class DebitAccountModel(TypedDict):
    account_id: Annotated[str, "The account ID of the debit account."]
    time: Annotated[Optional[str], "The time at which to get the balance."]

class DebitAccountService():
    def __init__(self, database: str, user: str, password:str , host: str) -> None:
        self.db_params = {
            "database": database,
            "user": f"{user}",
            "password": password,
            "host": f"{host}", 
            "port": 5432,
            "sslmode": "require"
        }
 
    @kernel_function(
        description="Get the balance of a debit account at a given time.",
        name="get_balance",
    )
    def get_balance(self, context: DebitAccountModel) -> str:
        try:
            account_id = context["account_id"]
            
            if context.get("time", False):
               time = (
                   dt.datetime
                   .fromisoformat(context["time"])
                   .strftime("%Y-%m-%d %H:%M:%S")
               )
            else:
                time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
            balance_query = """
                SELECT COALESCE(SUM(
                    CASE 
                        WHEN transaction_type = 'credit' THEN amount 
                        WHEN transaction_type = 'debit' THEN -amount 
                    END
                ), 0) AS balance
                FROM bank_transactions
                WHERE account_number = %s
                AND transaction_date <= %s;
            """
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()
            cursor.execute(balance_query, (account_id, time))
            balance = cursor.fetchone()[0]
            cursor.close()

            return f"El saldo de la cuenta {account_id} a las {time} es {balance}."
        
        except psycopg2.Error as e:
            return f"Error querying tables: {e}"