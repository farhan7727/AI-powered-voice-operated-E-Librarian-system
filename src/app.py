import logging
import json
from pathlib import Path
from typing import Union

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from llm_query import LLM
from db_manager import query_and_summary

load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("e_librarian_backend")


app = FastAPI(
    title="E-Librarian VAPI Backend",
    description="Simple single-tool backend for user request -> SQL -> DB fetch -> summary.",
    version="1.2.0",
)

llm = LLM()
qas = query_and_summary()


class ToolCallFunction(BaseModel):
    name: str
    arguments: str | dict

class ToolCall(BaseModel):
    id: str
    function: ToolCallFunction

class Message(BaseModel):
    toolCalls: list[ToolCall]

class VapiRequest(BaseModel):
    message: Message

class LibrarianSearchResponse(BaseModel):
    id: int
    # title: str
    description: Union[str,None]
    query: str = Field(..., min_length=2)
    completed:bool
    
    class Config:
        orm_mode=True

class SearchResponse(BaseModel):
    id: int
    title: str
    description: Union[str,None]
    query: str = Field(..., min_length=2)
    completed:bool
    
    class Config:
        orm_mode=True

@app.post('/LibrarianSearchResponse')
def search_the_DB(request: VapiRequest):
    logger.info("Received LibrarianSearchResponse request")

    try:
        for tool_call in request.message.toolCalls:
            if tool_call.function.name=='find_books':
                break
        else:
            logger.warning("Request rejected: No toolCalls provided")
            raise HTTPException(status_code=400, detail="No toolCalls provided")

        # Extract user query
        user_request = extract_query_from_vapi(request)
        logger.info(f"Extracted user query: {user_request}")

        if not user_request or len(user_request) < 2:
            logger.warning("Invalid or empty query received")
            raise HTTPException(status_code=400, detail="Invalid query")

        # Convert text to SQL
        logger.info("Calling llm.text_to_sql()")
        sql_result = llm.text_to_sql(user_request)
        logger.info(f"Generated SQL: {sql_result}")

        # Execute query and summarize
        logger.info("Calling qas.final_summary()")
        response = qas.final_summary(sql_result)
        logger.info("Summary successfully generated")

        return {
            "results": [
                {
                    "toolCallId": tool_call.id,
                    "result": str(response),
                }
            ]
        }

    except HTTPException:
        raise  # re-raise client errors unchanged

    except Exception as e:
        logger.exception("Unexpected server error occurred")
        raise HTTPException(status_code=500, detail="Internal server error")



def extract_query_from_vapi(request: VapiRequest) -> str:
    logger.debug("Extracting query from VAPI payload")

    tool_call = request.message.toolCalls[0]
    arguments = tool_call.function.arguments

    if isinstance(arguments, str):
        logger.debug("Arguments detected as string, parsing JSON")
        arguments = json.loads(arguments)

    query = arguments.get("query")
    logger.debug(f"Query extracted: {query}")

    return query