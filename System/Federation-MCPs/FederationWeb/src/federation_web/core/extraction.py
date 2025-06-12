"""
Content extraction and processing for FederationWeb
"""

import asyncio
import httpx
from typing import Dict, Any, List, Optional, Tuple
from bs4 import BeautifulSoup
import html2text
from readability import Document
import re
from urllib.parse import urlparse, urljoin
import logging

class ContentExtractor:
    """Handles content extraction from web pages"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0  # Don't wrap lines
        
    async def fetch_content(self, url: str, timeout: Optional[int] = None) -> Tuple[str, Dict[str, Any]]:
        """Fetch raw HTML content from URL"""
        if timeout is None:
            timeout = self.config.get("extraction_timeout", 30)
            
        headers = {
            "User-Agent": self.config.get("user_agent", "FederationWeb/1.0"),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                
                metadata = {
                    "status_code": response.status_code,
                    "content_type": response.headers.get("content-type", ""),
                    "content_length": response.headers.get("content-length"),
                    "final_url": str(response.url),
                    "encoding": response.encoding
                }
                
                return response.text, metadata
                
            except httpx.HTTPError as e:
                self.logger.error(f"HTTP error fetching {url}: {e}")
                raise
            except Exception as e:
                self.logger.error(f"Error fetching {url}: {e}")
                raise
    
    def extract_readable_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract readable content using Readability"""
        try:
            doc = Document(html)
            article = doc.summary()
            
            # Parse with BeautifulSoup for additional extraction
            soup = BeautifulSoup(article, 'html.parser')
            
            # Extract metadata
            title = doc.title()
            
            # Convert to markdown
            markdown_content = self.h2t.handle(article)
            
            # Extract additional elements
            extracted = {
                "title": title,
                "content": markdown_content,
                "text_content": soup.get_text(separator=' ', strip=True),
                "excerpt": self._generate_excerpt(soup.get_text()),
                "images": self._extract_images(soup, url),
                "links": self._extract_links(soup, url),
                "code_blocks": self._extract_code_blocks(soup)
            }
            
            return extracted
            
        except Exception as e:
            self.logger.error(f"Error in Readability extraction: {e}")
            # Fallback to basic extraction
            return self._basic_extraction(html, url)
    
    def _basic_extraction(self, html: str, url: str) -> Dict[str, Any]:
        """Basic extraction when Readability fails"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Extract title
        title = ""
        if soup.title:
            title = soup.title.string
        elif soup.find('h1'):
            title = soup.find('h1').get_text(strip=True)
            
        # Extract main content areas
        content_tags = ['main', 'article', 'div[role="main"]', '#content', '.content']
        content = None
        
        for tag in content_tags:
            element = soup.select_one(tag)
            if element:
                content = element
                break
                
        if not content:
            content = soup.body if soup.body else soup
            
        # Convert to markdown
        markdown_content = self.h2t.handle(str(content))
        text_content = content.get_text(separator=' ', strip=True)
        
        return {
            "title": title,
            "content": markdown_content,
            "text_content": text_content,
            "excerpt": self._generate_excerpt(text_content),
            "images": self._extract_images(content, url),
            "links": self._extract_links(content, url),
            "code_blocks": self._extract_code_blocks(content)
        }
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract images with alt text and URLs"""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                images.append({
                    "url": urljoin(base_url, src),
                    "alt": img.get('alt', ''),
                    "title": img.get('title', '')
                })
        return images
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract links with text"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and not href.startswith('#'):
                links.append({
                    "url": urljoin(base_url, href),
                    "text": link.get_text(strip=True),
                    "title": link.get('title', '')
                })
        return links
    
    def _extract_code_blocks(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract code blocks if present"""
        code_blocks = []
        
        # Look for <pre><code> blocks
        for pre in soup.find_all('pre'):
            code = pre.find('code')
            if code:
                language = ''
                # Try to detect language from class
                for cls in code.get('class', []):
                    if cls.startswith('language-'):
                        language = cls.replace('language-', '')
                        break
                        
                code_blocks.append({
                    "language": language,
                    "code": code.get_text(),
                    "formatted": True
                })
            else:
                # Plain pre block
                code_blocks.append({
                    "language": "",
                    "code": pre.get_text(),
                    "formatted": False
                })
                
        # Also look for inline code if preserve_code_blocks is enabled
        if self.config.get("preserve_code_blocks", True):
            for code in soup.find_all('code'):
                if not code.parent.name == 'pre':
                    code_blocks.append({
                        "language": "",
                        "code": code.get_text(),
                        "formatted": False,
                        "inline": True
                    })
                    
        return code_blocks
    
    def _generate_excerpt(self, text: str, max_length: int = 200) -> str:
        """Generate excerpt from text"""
        # Clean up whitespace
        text = ' '.join(text.split())
        
        if len(text) <= max_length:
            return text
            
        # Find sentence boundary
        excerpt = text[:max_length]
        last_period = excerpt.rfind('.')
        last_space = excerpt.rfind(' ')
        
        if last_period > max_length * 0.8:
            return excerpt[:last_period + 1]
        elif last_space > 0:
            return excerpt[:last_space] + "..."
        else:
            return excerpt + "..."
    
    async def extract_from_url(self, url: str) -> Dict[str, Any]:
        """Complete extraction pipeline for a URL"""
        try:
            # Fetch content
            html, metadata = await self.fetch_content(url)
            
            # Extract readable content
            extracted = self.extract_readable_content(html, url)
            
            # Add metadata
            extracted["metadata"] = metadata
            extracted["url"] = url
            
            # Calculate content metrics
            extracted["metrics"] = {
                "word_count": len(extracted["text_content"].split()),
                "char_count": len(extracted["text_content"]),
                "image_count": len(extracted["images"]),
                "link_count": len(extracted["links"]),
                "code_block_count": len(extracted["code_blocks"])
            }
            
            return extracted
            
        except Exception as e:
            self.logger.error(f"Error extracting from {url}: {e}")
            raise
    
    def chunk_content(self, content: str, chunk_size: Optional[int] = None, 
                     chunk_overlap: Optional[int] = None) -> List[str]:
        """Chunk content for processing"""
        if chunk_size is None:
            chunk_size = self.config.get("chunk_size", 1000)
        if chunk_overlap is None:
            chunk_overlap = self.config.get("chunk_overlap", 200)
            
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            # If paragraph is too long, split by sentences
            if len(para) > chunk_size:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) > chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            # Keep overlap
                            overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else current_chunk
                            current_chunk = overlap_text + " " + sentence
                        else:
                            # Single sentence too long, split by words
                            words = sentence.split()
                            for i in range(0, len(words), chunk_size // 10):
                                chunk_words = words[i:i + chunk_size // 10]
                                chunks.append(' '.join(chunk_words))
                    else:
                        current_chunk += " " + sentence
            else:
                # Add paragraph to current chunk
                if len(current_chunk) + len(para) > chunk_size:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                        overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else current_chunk
                        current_chunk = overlap_text + "\n\n" + para
                    else:
                        current_chunk = para
                else:
                    current_chunk += "\n\n" + para if current_chunk else para
        
        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks