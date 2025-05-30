from duckduckgo_search import ddg  
from typing import List
from app.models import WebSearchResult
import logging

logger = logging.getLogger(__name__)

class WebSearchService:
    def search(self, query: str, max_results: int = 5) -> List[WebSearchResult]:
        """
        Perform web search using DuckDuckGo (stable ddg() method)
        """
        try:
            search_results = ddg(query, max_results=max_results)
            if not search_results:
                return []

            results = []
            for result in search_results:
                title = result.get('title', '')
                url = result.get('href', '')
                snippet = result.get('body', '')

                web_result = WebSearchResult(
                    title=title,
                    url=url,
                    snippet=snippet
                )
                results.append(web_result)
            return results

        except Exception as e:
            logger.error(f"Web search failed for query '{query}': {str(e)}")
            return []

    def multi_search(self, queries: List[str], max_results_per_query: int = 3) -> List[WebSearchResult]:
        """
        Perform multiple searches and combine results
        """
        all_results = []
        for query in queries:
            results = self.search(query, max_results_per_query)
            all_results.extend(results)

        # Remove duplicates based on URL
        unique_results = []
        seen_urls = set()
        for result in all_results:
            if result.url and result.url not in seen_urls:
                unique_results.append(result)
                seen_urls.add(result.url)

        return unique_results[:5]  # Return top 5 unique results
