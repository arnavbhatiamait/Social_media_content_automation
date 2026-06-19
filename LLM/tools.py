import os
import urllib.parse
import urllib.request
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def search_tavily(query: str) -> list:
    """Search Tavily if TAVILY_API_KEY is available."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return []
    try:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": api_key,
            "query": query,
            "search_depth": "regular",
            "include_answer": False,
            "max_results": 5
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            results = []
            for item in data.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", ""),
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
            return results
    except Exception as e:
        print(f"Tavily search failed: {e}")
        return []

def search_serper(query: str) -> list:
    """Search Google via Serper if SERPER_API_KEY is available."""
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return []
    try:
        url = "https://google.serper.dev/search"
        payload = {"q": query, "num": 5}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            results = []
            for item in data.get("organic", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "date": item.get("date", datetime.now().strftime("%Y-%m-%d"))
                })
            return results
    except Exception as e:
        print(f"Serper search failed: {e}")
        return []

def search_google_news(query: str) -> list:
    """Search Google News RSS feed (completely free and keyless!)."""
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            results = []
            for item in root.findall(".//item")[:5]:
                title = item.find("title").text if item.find("title") is not None else ""
                link = item.find("link").text if item.find("link") is not None else ""
                pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                try:
                    dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
                    date_str = dt.strftime("%Y-%m-%d")
                except:
                    date_str = pub_date
                results.append({
                    "title": title,
                    "url": link,
                    "snippet": f"News story published on {pub_date}",
                    "date": date_str
                })
            return results
    except Exception as e:
        print(f"Google News RSS search failed: {e}")
        return []

def search_arxiv(query: str) -> list:
    """Search arXiv (completely free and keyless!)."""
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&max_results=5&sortBy=submittedDate&sortOrder=descending"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            namespaces = {'atom': 'http://www.w3.org/2005/Atom'}
            root = ET.fromstring(xml_data)
            results = []
            for entry in root.findall("atom:entry", namespaces)[:5]:
                title_elem = entry.find("atom:title", namespaces)
                title = title_elem.text.strip().replace("\n", " ") if title_elem is not None else ""
                id_elem = entry.find("atom:id", namespaces)
                link = id_elem.text if id_elem is not None else ""
                summary_elem = entry.find("atom:summary", namespaces)
                snippet = summary_elem.text.strip().replace("\n", " ")[:200] + "..." if summary_elem is not None else ""
                pub_elem = entry.find("atom:published", namespaces)
                pub_date = pub_elem.text if pub_elem is not None else ""
                try:
                    date_str = pub_date[:10]
                except:
                    date_str = pub_date
                results.append({
                    "title": title,
                    "url": link,
                    "snippet": snippet,
                    "date": date_str
                })
            return results
    except Exception as e:
        print(f"arXiv search failed: {e}")
        return []

def get_huggingface_daily_papers() -> list:
    """Fetch Hugging Face daily papers (completely free JSON API)."""
    try:
        url = "https://huggingface.co/api/daily_papers"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            papers = json.loads(response.read().decode())
            results = []
            for paper in papers[:10]:
                title = paper.get("title", "")
                paper_id = paper.get("id", "")
                link = f"https://huggingface.co/papers/{paper_id}" if paper_id else ""
                published_at = paper.get("publishedAt", datetime.now().strftime("%Y-%m-%d"))
                summary = paper.get("summary", "")
                results.append({
                    "title": title,
                    "url": link,
                    "snippet": summary[:200] + "..." if summary else "Hugging Face Daily Paper",
                    "date": published_at[:10]
                })
            return results
    except Exception as e:
        print(f"HuggingFace Daily Papers fetch failed: {e}")
        return []

def get_trending_github(topic: str = "machine-learning") -> list:
    """Fetch trending GitHub repositories related to a topic."""
    try:
        encoded_q = urllib.parse.quote(f"{topic} created:>2025-01-01 stars:>50")
        url = f"https://api.github.com/search/repositories?q={encoded_q}&sort=stars&order=desc&per_page=5"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            results = []
            for repo in data.get("items", []):
                results.append({
                    "title": repo.get("full_name", ""),
                    "url": repo.get("html_url", ""),
                    "snippet": repo.get("description", "") or "GitHub Repository",
                    "date": repo.get("created_at", "")[:10]
                })
            return results
    except Exception as e:
        print(f"GitHub search failed: {e}")
        return []

def compile_research(query: str) -> str:
    """Runs all search methods and returns a unified context string for the LLM."""
    all_results = []
    
    # 1. Google News
    gnews = search_google_news(query)
    if gnews:
        all_results.append(f"--- Google News Results for '{query}' ---")
        for idx, item in enumerate(gnews):
            all_results.append(f"{idx+1}. Title: {item['title']}\n   URL: {item['url']}\n   Date: {item['date']}")
            
    # 2. arXiv
    arxiv = search_arxiv(query)
    if arxiv:
        all_results.append(f"--- arXiv Papers for '{query}' ---")
        for idx, item in enumerate(arxiv):
            all_results.append(f"{idx+1}. Title: {item['title']}\n   URL: {item['url']}\n   Date: {item['date']}\n   Summary: {item['snippet']}")

    # 3. Tavily & Serper
    tavily_res = search_tavily(query)
    if tavily_res:
        all_results.append(f"--- Tavily Web Search for '{query}' ---")
        for idx, item in enumerate(tavily_res):
            all_results.append(f"{idx+1}. Title: {item['title']}\n   URL: {item['url']}\n   Snippet: {item['snippet']}")
            
    serper_res = search_serper(query)
    if serper_res:
        all_results.append(f"--- Serper Search for '{query}' ---")
        for idx, item in enumerate(serper_res):
            all_results.append(f"{idx+1}. Title: {item['title']}\n   URL: {item['url']}\n   Snippet: {item['snippet']}\n   Date: {item['date']}")
            
    # 4. Hugging Face
    if any(k in query.lower() for k in ["llm", "ai", "machine learning", "agent", "deep learning"]):
        hf = get_huggingface_daily_papers()
        if hf:
            all_results.append("--- Hugging Face Daily Trending Papers ---")
            for idx, item in enumerate(hf[:3]):
                all_results.append(f"{idx+1}. Title: {item['title']}\n   URL: {item['url']}\n   Date: {item['date']}\n   Abstract: {item['snippet']}")

    # 5. GitHub
    github_res = get_trending_github(query)
    if github_res:
        all_results.append(f"--- GitHub Repositories for '{query}' ---")
        for idx, item in enumerate(github_res):
            all_results.append(f"{idx+1}. Repository: {item['title']}\n   URL: {item['url']}\n   Description: {item['snippet']}")

    return "\n\n".join(all_results) if all_results else "No research results found for this topic."
