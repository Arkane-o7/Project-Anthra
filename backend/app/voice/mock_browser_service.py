"""
Mock browser service for testing voice commands without requiring Playwright installation.
This provides a simulation of browser actions for development and testing.
"""

from typing import Optional, Dict, Any, List
import asyncio
import json
import random
from .schemas import BrowserAction, PageContent, VoiceResponse

class MockBrowserService:
    def __init__(self):
        self.current_url = ""
        self.current_page_title = ""
        self.is_initialized = False
        self.page_history = []
        
        # Mock page content for different URLs
        self.mock_pages = {
            "https://google.com": {
                "title": "Google",
                "text": "Google Search homepage. Search the world's information, including webpages, images, videos and more. Google has many special features to help you find exactly what you're looking for.",
                "links": [
                    {"text": "Images", "href": "https://images.google.com"},
                    {"text": "Maps", "href": "https://maps.google.com"},
                    {"text": "YouTube", "href": "https://youtube.com"},
                    {"text": "News", "href": "https://news.google.com"}
                ]
            },
            "https://amazon.com": {
                "title": "Amazon.com: Online Shopping",
                "text": "Amazon.com offers millions of books, movies, music, electronics, toys, tools, home improvement, automotive, and more. Online shopping from the earth's biggest selection of books, magazines, music, DVDs, videos, electronics, computers, software, apparel & accessories.",
                "links": [
                    {"text": "Today's Deals", "href": "https://amazon.com/deals"},
                    {"text": "Customer Service", "href": "https://amazon.com/help"},
                    {"text": "Registry", "href": "https://amazon.com/registry"},
                    {"text": "Gift Cards", "href": "https://amazon.com/gift-cards"}
                ]
            },
            "search_results": {
                "title": "Search Results",
                "text": "Search results for your query. Found several relevant items and links that match your search criteria. You can browse through the results to find what you're looking for.",
                "links": [
                    {"text": "Wireless Headphones - Best Buy", "href": "https://bestbuy.com/headphones"},
                    {"text": "Amazon Wireless Headphones", "href": "https://amazon.com/headphones"},
                    {"text": "Sony WH-1000XM4 Review", "href": "https://review.com/sony"},
                    {"text": "Bose QuietComfort Headphones", "href": "https://bose.com/headphones"}
                ]
            }
        }
        
    async def initialize(self):
        """Mock browser initialization"""
        await asyncio.sleep(0.5)  # Simulate initialization time
        self.is_initialized = True
        return True
    
    async def close(self):
        """Mock browser cleanup"""
        self.is_initialized = False
        await asyncio.sleep(0.1)
    
    async def navigate(self, url: str) -> VoiceResponse:
        """Mock navigation to a URL"""
        try:
            await asyncio.sleep(1)  # Simulate loading time
            
            # Normalize URL
            if not url.startswith(("http://", "https://")):
                if any(domain in url.lower() for domain in ["google.com", "amazon.com"]):
                    url = f"https://{url}"
                else:
                    # Treat as search query
                    url = f"https://www.google.com/search?q={url}"
            
            # Clean up common URL patterns
            if "google.com" in url:
                url = "https://google.com"
            elif "amazon.com" in url:
                url = "https://amazon.com"
            
            # Set current page
            self.current_url = url
            if url in self.mock_pages:
                self.current_page_title = self.mock_pages[url]["title"]
            else:
                self.current_page_title = "Mock Page"
            
            # Add to history
            self.page_history.append({
                "url": url,
                "title": self.current_page_title,
                "timestamp": "now"
            })
            
            return VoiceResponse(
                message=f"Successfully navigated to {self.current_page_title}",
                success=True,
                data={"url": self.current_url, "title": self.current_page_title}
            )
        except Exception as e:
            return VoiceResponse(
                message=f"Failed to navigate: {str(e)}",
                success=False
            )
    
    async def click_element(self, target: str) -> VoiceResponse:
        """Mock clicking an element"""
        try:
            await asyncio.sleep(0.5)  # Simulate click action
            
            # Simulate different click outcomes
            target_lower = target.lower()
            
            if any(word in target_lower for word in ["login", "sign in"]):
                return VoiceResponse(
                    message=f"Clicked {target}. Login form is now displayed.",
                    success=True
                )
            elif any(word in target_lower for word in ["search", "submit"]):
                return VoiceResponse(
                    message=f"Clicked {target}. Search has been submitted.",
                    success=True
                )
            elif any(word in target_lower for word in ["button", "link"]):
                return VoiceResponse(
                    message=f"Successfully clicked {target}",
                    success=True
                )
            else:
                # Sometimes simulate not finding the element
                if random.random() < 0.2:  # 20% chance of not finding
                    return VoiceResponse(
                        message=f"Could not find element: {target}",
                        success=False
                    )
                else:
                    return VoiceResponse(
                        message=f"Successfully clicked {target}",
                        success=True
                    )
        except Exception as e:
            return VoiceResponse(
                message=f"Failed to click: {str(e)}",
                success=False
            )
    
    async def type_text(self, text: str, target: Optional[str] = None) -> VoiceResponse:
        """Mock typing text"""
        try:
            await asyncio.sleep(0.3)  # Simulate typing time
            
            if target:
                return VoiceResponse(
                    message=f"Successfully typed '{text}' into {target}",
                    success=True
                )
            else:
                return VoiceResponse(
                    message=f"Successfully typed: {text}",
                    success=True
                )
        except Exception as e:
            return VoiceResponse(
                message=f"Failed to type: {str(e)}",
                success=False
            )
    
    async def search(self, query: str) -> VoiceResponse:
        """Mock search functionality"""
        try:
            await asyncio.sleep(1.5)  # Simulate search time
            
            # Simulate search by navigating to search results
            self.current_url = f"https://www.google.com/search?q={query}"
            self.current_page_title = f"Search Results for '{query}'"
            
            # Add to history
            self.page_history.append({
                "url": self.current_url,
                "title": self.current_page_title,
                "timestamp": "now"
            })
            
            return VoiceResponse(
                message=f"Successfully searched for: {query}. Found multiple results.",
                success=True
            )
        except Exception as e:
            return VoiceResponse(
                message=f"Failed to search: {str(e)}",
                success=False
            )
    
    async def get_page_content(self) -> PageContent:
        """Mock page content extraction"""
        try:
            await asyncio.sleep(0.5)  # Simulate content extraction
            
            # Return mock content based on current URL
            if self.current_url in self.mock_pages:
                page_data = self.mock_pages[self.current_url]
                return PageContent(
                    title=page_data["title"],
                    text=page_data["text"],
                    links=page_data["links"]
                )
            elif "search" in self.current_url.lower():
                # Return search results content
                page_data = self.mock_pages["search_results"]
                return PageContent(
                    title=page_data["title"],
                    text=page_data["text"],
                    links=page_data["links"]
                )
            else:
                # Generic page content
                return PageContent(
                    title=self.current_page_title or "Mock Page",
                    text=f"This is a mock page at {self.current_url}. The content would normally be extracted from the actual webpage, but we're using simulated content for demonstration purposes.",
                    links=[
                        {"text": "Example Link 1", "href": "https://example1.com"},
                        {"text": "Example Link 2", "href": "https://example2.com"}
                    ]
                )
        except Exception as e:
            return PageContent(
                title="Error",
                text=f"Failed to get page content: {str(e)}"
            )