from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

class CommandType(str, Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SEARCH = "search"
    FILL_FORM = "fill_form"
    READ_PAGE = "read_page"
    SCROLL = "scroll"

class VoiceCommand(BaseModel):
    text: str
    confidence: Optional[float] = None

class ParsedCommand(BaseModel):
    type: CommandType
    action: str
    target: Optional[str] = None
    value: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = {}

class BrowserAction(BaseModel):
    action: str
    selector: Optional[str] = None
    text: Optional[str] = None
    url: Optional[str] = None
    options: Optional[Dict[str, Any]] = {}

class VoiceResponse(BaseModel):
    message: str
    success: bool
    data: Optional[Dict[str, Any]] = None

class PageContent(BaseModel):
    title: str
    text: str
    links: List[Dict[str, str]] = []
    forms: List[Dict[str, Any]] = []
    buttons: List[Dict[str, str]] = []