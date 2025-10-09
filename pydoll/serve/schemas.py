# pydoll/schemas.py
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class ByModel(BaseModel):
    """
    How to locate an element on the page.
    """
    tag_name: Optional[str] = Field(
        None, description="HTML tag name (e.g. 'input', 'button').", example="input"
    )
    name: Optional[str] = Field(
        None, description="Value of the 'name' attribute of the element.", example="q"
    )
    text: Optional[str] = Field(
        None, description="Visible text of the element.", example="Search"
    )
    id: Optional[str] = Field(
        None, description="Value of the 'id' attribute of the element.", example="submit-btn"
    )
    selector: Optional[str] = Field(
        None, description="CSS selector to locate the element.", example="#main > div h3"
    )
    timeout: Optional[int] = Field(
        None, description="How long to wait (in seconds) for the element to appear.", example=10
    )

    class Config:
        schema_extra = {
            "example": {
                "selector": "input[name='q']",
                "timeout": 5
            }
        }

class Step(BaseModel):
    """
    One action to perform on the page.
    """
    action: str = Field(
        ..., description="Type of action (e.g. 'find', 'press_key', 'execute_script', 'screenshot').",
        example="find"
    )
    by: Optional[ByModel] = Field(
        None, description="Selector for the element to act upon (if required).",
        example={"selector": "textarea[name='q']"}
    )
    insert_text: Optional[str] = Field(
        None, description="Text to type into the element (used with 'find').",
        example="pydoll python"
    )
    click: Optional[bool] = Field(
        None, description="Whether to click the element (used with 'find').", example=True
    )
    key: Optional[str] = Field(
        None, description="Keyboard key to press (used with 'press_key'). Must match pydoll.constants.Key.",
        example="ENTER"
    )
    script: Optional[str] = Field(
        None, description="JavaScript code to execute in the page (used with 'execute_script').",
        example="return document.title;"
    )
    return_by_value: Optional[bool] = Field(
        None, description="If true, returns value by JSON (used with 'execute_script').", example=True
    )
    method: Optional[str] = Field(
        None, description="HTTP method for a network request (used with 'request').", example="GET"
    )
    url: Optional[str] = Field(
        None, description="Target URL for actions like 'request' or 'new_tab'.",
        example="https://example.com/api"
    )
    headers: Optional[Dict[str, str]] = Field(
        None, description="Optional HTTP headers for 'request' action.",
        example={"Authorization": "Bearer token"}
    )
    json_payload: Optional[Dict[str, Any]] = Field(
        None, description="Optional JSON payload for 'request' action.", example={"param": "value"}
    )
    attribute: Optional[str] = Field(
        None, description="Attribute name to get from an element (used with 'get_attribute').",
        example="href"
    )
    full_page: Optional[bool] = Field(
        None, description="If true, takes a full-page screenshot (used with 'screenshot').", example=True
    )
    find_all: Optional[bool] = Field(
        None, description="If true, query all elements matching selector (used with 'query').", example=True
    )
    browser_context_id: Optional[str] = Field(
        None, description="Optional browser context ID (used with 'new_tab').", example="context1"
    )

    class Config:
        schema_extra = {
            "example": {
                "action": "find",
                "by": {"selector": "textarea[name='q']"},
                "insert_text": "pydoll python"
            }
        }

class CrawlRequest(BaseModel):
    """
    Request body for the /crawl endpoint.
    """
    url: str = Field(
        ..., description="URL to open first in the browser.", example="https://www.google.com"
    )
    steps: Optional[List[Step]] = Field(
        default_factory=list,
        description="List of actions to execute after the page loads.",
        example=[
            {
                "action": "find",
                "by": {"selector": "textarea[name='q']"},
                "insert_text": "pydoll python"
            },
            {"action": "press_key", "key": "ENTER"},
            {
                "action": "wait_for",
                "by": {"text": "autoscrape-labs/pydoll"}
            },
            {
                "action": "click",
                "by": {"text": "autoscrape-labs/pydoll"}
            },
            {"action": "execute_script", "script": "return document.title;", "return_by_value": True}
        ]
    )

    class Config:
        schema_extra = {
            "example": {
                "url": "https://www.google.com",
                "steps": [
                    {
                        "action": "find",
                        "by": {"selector": "textarea[name='q']"},
                        "insert_text": "pydoll python"
                    },
                    {"action": "press_key", "key": "ENTER"},
                    {"action": "wait_for", "by": {"text": "autoscrape-labs/pydoll"}},
                    {"action": "execute_script", "script": "return document.title;", "return_by_value": True}
                ]
            }
        }
