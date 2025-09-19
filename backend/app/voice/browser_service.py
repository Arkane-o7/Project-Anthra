from playwright.async_api import async_playwright, Browser, Page
from typing import Optional, Dict, Any, List
import asyncio
import json
from .schemas import BrowserAction, PageContent, VoiceResponse

class BrowserAutomationService:
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.current_url = ""
        
    async def initialize(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            # Use chromium in headless mode for now
            self.browser = await self.playwright.chromium.launch(headless=True)
            context = await self.browser.new_context()
            self.page = await context.new_page()
            return True
        except Exception as e:
            print(f"Failed to initialize browser: {e}")
            return False
    
    async def close(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def navigate(self, url: str) -> VoiceResponse:
        """Navigate to a URL"""
        try:
            if not self.page:
                if not await self.initialize():
                    return VoiceResponse(
                        message="Failed to initialize browser",
                        success=False
                    )
            
            # Ensure URL has protocol
            if not url.startswith(("http://", "https://")):
                if any(domain in url.lower() for domain in ["google.com", "amazon.com", "github.com"]):
                    url = f"https://{url}"
                else:
                    url = f"https://www.google.com/search?q={url}"
            
            await self.page.goto(url, wait_until="domcontentloaded")
            self.current_url = self.page.url
            title = await self.page.title()
            
            return VoiceResponse(
                message=f"Successfully navigated to {title}",
                success=True,
                data={"url": self.current_url, "title": title}
            )
        except Exception as e:
            return VoiceResponse(
                message=f"Failed to navigate: {str(e)}",
                success=False
            )
    
    async def click_element(self, target: str) -> VoiceResponse:
        """Click an element on the page"""
        try:
            if not self.page:
                return VoiceResponse(
                    message="Browser not initialized",
                    success=False
                )
            
            # Try different selectors based on the target description
            selectors = self._generate_selectors(target)
            
            element_found = False
            for selector in selectors:
                try:
                    await self.page.click(selector, timeout=2000)
                    element_found = True
                    break
                except:
                    continue
            
            if element_found:
                return VoiceResponse(
                    message=f"Successfully clicked {target}",
                    success=True
                )
            else:
                return VoiceResponse(
                    message=f"Could not find element: {target}",
                    success=False
                )
        except Exception as e:
            return VoiceResponse(
                message=f"Failed to click: {str(e)}",
                success=False
            )
    
    async def type_text(self, text: str, target: Optional[str] = None) -> VoiceResponse:
        """Type text into an input field"""
        try:
            if not self.page:
                return VoiceResponse(
                    message="Browser not initialized",
                    success=False
                )
            
            # If target is specified, try to find that input
            if target:
                selectors = self._generate_input_selectors(target)
                input_found = False
                
                for selector in selectors:
                    try:
                        await self.page.fill(selector, text)
                        input_found = True
                        break
                    except:
                        continue
                
                if not input_found:
                    return VoiceResponse(
                        message=f"Could not find input field: {target}",
                        success=False
                    )
            else:
                # Type into the currently focused element
                await self.page.keyboard.type(text)
            
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
        """Perform a search on the current page"""
        try:
            if not self.page:
                return VoiceResponse(
                    message="Browser not initialized",
                    success=False
                )
            
            # Common search input selectors
            search_selectors = [
                'input[name="q"]',
                'input[type="search"]',
                'input[placeholder*="search" i]',
                '#search-box',
                '.search-input',
                'input[aria-label*="search" i]'
            ]
            
            search_found = False
            for selector in search_selectors:
                try:
                    await self.page.fill(selector, query)
                    await self.page.keyboard.press("Enter")
                    search_found = True
                    break
                except:
                    continue
            
            if search_found:
                await self.page.wait_for_load_state("domcontentloaded")
                return VoiceResponse(
                    message=f"Successfully searched for: {query}",
                    success=True
                )
            else:
                return VoiceResponse(
                    message="Could not find search box on this page",
                    success=False
                )
        except Exception as e:
            return VoiceResponse(
                message=f"Failed to search: {str(e)}",
                success=False
            )
    
    async def get_page_content(self) -> PageContent:
        """Extract page content for reading aloud"""
        try:
            if not self.page:
                return PageContent(title="", text="Browser not initialized")
            
            title = await self.page.title()
            
            # Get main text content
            text_content = await self.page.evaluate("""
                () => {
                    // Remove script and style elements
                    const elementsToRemove = document.querySelectorAll('script, style, nav, footer, aside');
                    elementsToRemove.forEach(el => el.remove());
                    
                    // Get main content
                    const main = document.querySelector('main, .main-content, #main, .content');
                    if (main) {
                        return main.innerText;
                    }
                    
                    // Fallback to body text
                    return document.body.innerText;
                }
            """)
            
            # Get links
            links = await self.page.evaluate("""
                () => {
                    const linkElements = document.querySelectorAll('a[href]');
                    return Array.from(linkElements).slice(0, 10).map(link => ({
                        text: link.innerText.trim(),
                        href: link.href
                    })).filter(link => link.text.length > 0);
                }
            """)
            
            # Clean up text content
            text_lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            clean_text = ' '.join(text_lines[:10])  # First 10 meaningful lines
            
            return PageContent(
                title=title,
                text=clean_text,
                links=links
            )
        except Exception as e:
            return PageContent(
                title="Error",
                text=f"Failed to get page content: {str(e)}"
            )
    
    def _generate_selectors(self, target: str) -> List[str]:
        """Generate possible CSS selectors for a target description"""
        target_lower = target.lower()
        selectors = []
        
        # Button selectors
        if any(word in target_lower for word in ["button", "btn"]):
            selectors.extend([
                f'button:has-text("{target}")',
                f'input[type="button"][value*="{target}" i]',
                f'input[type="submit"][value*="{target}" i]',
                f'[role="button"]:has-text("{target}")',
                f'.button:has-text("{target}")',
                f'.btn:has-text("{target}")'
            ])
        
        # Link selectors
        if any(word in target_lower for word in ["link", "href"]):
            selectors.extend([
                f'a:has-text("{target}")',
                f'a[href*="{target}" i]'
            ])
        
        # Generic selectors
        selectors.extend([
            f'*:has-text("{target}"):visible',
            f'[aria-label*="{target}" i]',
            f'[title*="{target}" i]',
            f'[data-testid*="{target}" i]'
        ])
        
        return selectors
    
    def _generate_input_selectors(self, target: str) -> List[str]:
        """Generate possible input selectors"""
        target_lower = target.lower()
        selectors = []
        
        # Specific input types
        if "email" in target_lower:
            selectors.append('input[type="email"]')
        elif "password" in target_lower:
            selectors.append('input[type="password"]')
        elif "search" in target_lower:
            selectors.append('input[type="search"]')
        
        # Generic input selectors
        selectors.extend([
            f'input[name*="{target}" i]',
            f'input[placeholder*="{target}" i]',
            f'input[aria-label*="{target}" i]',
            f'textarea[placeholder*="{target}" i]',
            f'textarea[aria-label*="{target}" i]'
        ])
        
        return selectors