import os
from pypdf import PdfReader
from rank_bm25 import BM25Okapi
import chromadb
from dotenv import load_dotenv

load_dotenv()