# pydoll/schemas.py
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class ByModel(BaseModel):
    tag_name: Optional[str] = None
    name: Optional[str] = None
    text: Optional[str] = None
    id: Optional[str] = None
    selector: Optional[str] = None
    timeout: Optional[int] = None

class Step(BaseModel):
    action: str = Field(..., description="Action to perform")
    by: Optional[ByModel] = Field(None, description="Element selector (if needed)")
    insert_text: Optional[str] = None
    click: Optional[bool] = None
    key: Optional[str] = None
    script: Optional[str] = None
    return_by_value: Optional[bool] = None
    method: Optional[str] = None
    url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    json: Optional[Dict[str, Any]] = None
    attribute: Optional[str] = None
    full_page: Optional[bool] = None  # screenshot
    find_all: Optional[bool] = None   # for query
    browser_context_id: Optional[str] = None  # for new_tab

class CrawlRequest(BaseModel):
    url: str = Field(..., description="URL to open first")
    steps: Optional[List[Step]] = Field(default_factory=list)
