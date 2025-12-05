"""
Data Ingestion Module
Handles PDFs, TXT, Excel, Word docs, and web scraping
"""

import os
from typing import List
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import requests
from bs4 import BeautifulSoup
import pandas as pd


class DataIngestion:
    def __init__(self, chunk_size=1000, chunk_overlap=100):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """Load and split PDF documents"""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            return self.text_splitter.split_documents(documents)
        except Exception as e:
            print(f"Error loading PDF {file_path}: {e}")
            return []
    
    def load_txt(self, file_path: str) -> List[Document]:
        """Load and split text documents"""
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            return self.text_splitter.split_documents(documents)
        except Exception as e:
            print(f"Error loading TXT {file_path}: {e}")
            return []
    
    def load_excel(self, file_path: str) -> List[Document]:
        """Load Excel documents and convert to text"""
        try:
            df = pd.read_excel(file_path)
            # Convert dataframe to text format
            text_content = df.to_string(index=False)
            doc = Document(
                page_content=text_content,
                metadata={"source": file_path, "type": "excel"}
            )
            return self.text_splitter.split_documents([doc])
        except Exception as e:
            print(f"Error loading Excel {file_path}: {e}")
            return []
    
    def load_csv(self, file_path: str, max_rows: int = 500) -> List[Document]:
        """
        Load CSV documents - smart detection for social media datasets
        Extracts only useful marketing-related columns
        """
        try:
            filename = os.path.basename(file_path).lower()
            
            # Limit rows for large files (blogtext.csv is 800MB!)
            if 'blogtext' in filename:
                max_rows = 200  # Very large file, limit more
            
            df = pd.read_csv(file_path, nrows=max_rows)
            documents = []
            
            # Platform-specific column mappings (only useful marketing columns)
            platform_configs = {
                'facebook': {
                    'text_col': 'comment_text',
                    'engagement': ['num_likes', 'num_replies'],
                    'platform': 'Facebook'
                },
                'instagram': {
                    'text_col': 'comment',
                    'engagement': ['likes_number', 'replies_number'],
                    'extra': ['hashtag_comment'],
                    'platform': 'Instagram'
                },
                'tiktok': {
                    'text_col': 'comment_text',
                    'engagement': ['num_likes', 'num_replies'],
                    'platform': 'TikTok'
                },
                'twitter': {
                    'text_col': 'description',
                    'engagement': ['likes', 'replies', 'reposts', 'views'],
                    'extra': ['hashtags'],
                    'platform': 'Twitter'
                },
                'blogtext': {
                    'text_col': 'text',
                    'extra': ['topic'],
                    'platform': 'Blog'
                }
            }
            
            # Detect platform from filename
            config = None
            detected_platform = 'Unknown'
            for platform, cfg in platform_configs.items():
                if platform in filename:
                    config = cfg
                    detected_platform = cfg['platform']
                    break
            
            # Fallback: find any text column
            if not config:
                text_cols = ['text', 'content', 'body', 'message', 'description', 'comment', 'comment_text']
                for col in text_cols:
                    if col in df.columns:
                        config = {'text_col': col, 'platform': 'Generic'}
                        break
            
            if not config or config['text_col'] not in df.columns:
                print(f"  Skipping {filename}: No suitable text column found")
                return []
            
            text_col = config['text_col']
            
            for idx, row in df.iterrows():
                text = str(row[text_col])
                
                # Skip empty or very short entries
                if pd.isna(row[text_col]) or len(text) < 30:
                    continue
                
                # Build metadata with engagement metrics
                metadata = {
                    "source": file_path,
                    "platform": detected_platform,
                    "type": "social_media",
                    "row": idx
                }
                
                # Add engagement metrics if available
                for eng_col in config.get('engagement', []):
                    if eng_col in df.columns and pd.notna(row[eng_col]):
                        metadata[eng_col] = str(row[eng_col])
                
                # Add extra useful columns
                for extra_col in config.get('extra', []):
                    if extra_col in df.columns and pd.notna(row[extra_col]):
                        metadata[extra_col] = str(row[extra_col])[:100]  # Limit length
                
                doc = Document(page_content=text, metadata=metadata)
                documents.append(doc)
            
            print(f"  {detected_platform}: Loaded {len(documents)} documents from {filename}")
            return self.text_splitter.split_documents(documents)
            
        except Exception as e:
            print(f"Error loading CSV {file_path}: {e}")
            return []
    
    def load_json(self, file_path: str, max_items: int = 500) -> List[Document]:
        """Load JSON documents - handles LinkedIn ads format"""
        try:
            import json
            filename = os.path.basename(file_path).lower()
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = []
            
            # Handle list of items (like LinkedIn ads)
            if isinstance(data, list):
                for idx, item in enumerate(data[:max_items]):
                    # LinkedIn ads format
                    if 'body' in item:
                        text = item.get('body', '')
                        if len(text) < 20:
                            continue
                        
                        metadata = {
                            "source": file_path,
                            "platform": "LinkedIn",
                            "type": "ad",
                            "advertiser": item.get('advertiserName', ''),
                            "ctas": str(item.get('ctas', [])),
                            "impressions": str(item.get('impressions', '')),
                        }
                        
                        doc = Document(page_content=text, metadata=metadata)
                        documents.append(doc)
            
            print(f"  LinkedIn: Loaded {len(documents)} ads from {filename}")
            return self.text_splitter.split_documents(documents)
            
        except Exception as e:
            print(f"Error loading JSON {file_path}: {e}")
            return []
    
    def load_docx(self, file_path: str) -> List[Document]:
        """Load Word documents"""
        try:
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            return self.text_splitter.split_documents(documents)
        except Exception as e:
            print(f"Error loading DOCX {file_path}: {e}")
            return []
    
    def scrape_website(self, url: str) -> List[Document]:
        """Scrape content from a website URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            doc = Document(
                page_content=text,
                metadata={"source": url, "type": "website"}
            )
            
            return self.text_splitter.split_documents([doc])
        except Exception as e:
            print(f"Error scraping website {url}: {e}")
            return []
    
    def load_directory(self, directory_path: str) -> List[Document]:
        """Load all supported files from a directory"""
        all_documents = []
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_extension = os.path.splitext(file)[1].lower()
                
                if file_extension == '.pdf':
                    all_documents.extend(self.load_pdf(file_path))
                elif file_extension == '.txt':
                    all_documents.extend(self.load_txt(file_path))
                elif file_extension in ['.xlsx', '.xls']:
                    all_documents.extend(self.load_excel(file_path))
                elif file_extension == '.docx':
                    all_documents.extend(self.load_docx(file_path))
                elif file_extension == '.csv':
                    all_documents.extend(self.load_csv(file_path))
                elif file_extension == '.json':
                    all_documents.extend(self.load_json(file_path))
        
        return all_documents
    
    def load_from_urls(self, urls: List[str]) -> List[Document]:
        """Load content from multiple URLs"""
        all_documents = []
        
        for url in urls:
            print(f"Scraping: {url}")
            documents = self.scrape_website(url)
            all_documents.extend(documents)
        
        return all_documents


if __name__ == "__main__":
    # Test the data ingestion
    ingestion = DataIngestion()
    
    # Example: Load from directory
    docs = ingestion.load_directory("./data/documents")
    print(f"Loaded {len(docs)} document chunks from directory")
    
    # Example: Load from URLs
    urls = [
        "https://blog.hubspot.com/marketing/ad-copy-examples",
        "https://neilpatel.com/blog/ad-copy/"
    ]
    web_docs = ingestion.load_from_urls(urls)
    print(f"Loaded {len(web_docs)} document chunks from websites")