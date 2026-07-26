import logging
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from firecrawl import FirecrawlApp
from app.core.config import settings

logger = logging.getLogger(__name__)

class FirecrawlService:
    def __init__(self):
        self.api_key = getattr(settings, "FIRECRAWL_API_KEY", None)
        self.app = None
        if self.api_key:
            self.app = FirecrawlApp(api_key=self.api_key)
        else:
            logger.warning("FIRECRAWL_API_KEY not configured. FirecrawlService will not function.")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    async def extract_markdown(self, url: str) -> str:
        """
        Uses Firecrawl Cloud Scrape API to fetch clean markdown from a URL.
        """
        if not self.app:
            logger.error("Cannot extract markdown: Firecrawl API key is missing.")
            return ""

        try:
            logger.info(f"Extracting markdown via Firecrawl for URL: {url}")
            
            # The official firecrawl-py SDK may be synchronous for scrape_url
            response = await asyncio.to_thread(
                self.app.scrape_url,
                url,
                params={'formats': ['markdown']}
            )
            
            if response:
                if 'markdown' in response:
                    return response['markdown']
                elif 'data' in response and 'markdown' in response['data']:
                    return response['data']['markdown']
            
            logger.warning(f"Firecrawl extraction returned no markdown for {url}")
            return ""
                
        except Exception as e:
            logger.error(f"Firecrawl API call failed for {url}: {str(e)}")
            raise e
