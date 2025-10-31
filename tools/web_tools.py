import requests
from typing import Optional, Dict, Any
from urllib.parse import urlparse

class WebTools:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
    
    def fetch_url(self, url: str, max_size: Optional[int] = None) -> str:
        """
        Fetch content from a URL safely.
        
        Args:
            url: URL to fetch
            max_size: Maximum number of bytes to read
            
        Returns:
            Content as string
        """
        try:
            # Validate URL
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                return f"❌ Invalid URL: {url}"
            
            # Only allow http/https
            if parsed.scheme not in ['http', 'https']:
                return f"❌ Only HTTP/HTTPS URLs are supported"
            
            response = self.session.get(
                url,
                timeout=self.timeout,
                stream=bool(max_size)
            )
            
            response.raise_for_status()
            
            if max_size:
                content = next(response.iter_content(max_size, decode_unicode=True))
            else:
                content = response.text
                
            return content
            
        except requests.exceptions.RequestException as e:
            return f"❌ Error fetching URL: {str(e)}"
    
    def post_json(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send POST request with JSON data.
        
        Args:
            url: URL to send request to
            data: Dictionary to send as JSON
            
        Returns:
            Response data as dictionary
        """
        try:
            response = self.session.post(
                url,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def is_url_accessible(self, url: str) -> bool:
        """
        Check if a URL is accessible.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is accessible, False otherwise
        """
        try:
            response = self.session.head(url, timeout=self.timeout)
            return response.status_code == 200
        except:
            return False
