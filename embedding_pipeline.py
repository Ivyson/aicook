#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Create a chroma db file and store it persistently in the disk
import os
import mimetypes
import fitz
import docx2txt
from PIL import Image
import pytesseract
from google import genai
from FileHandler import open_file

os.environ['CHROMA_TELEMETRY_ENABLED'] = 'false'

from chromadb import PersistentClient
#from chromadb.config import Settings
import chromadb as db
CHROMA_DIR = './database/CHROMA_STORE'
EMBEDDING_MODEL = 'gemini-embedding-exp-03-07'
# Set up the chroma db client persistenly..
client = PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(
        name='local_rag',
        metadata={'hnsw:space':'cosine'}
        )

# Embedding function

def embedding(text):
    """
    Will fill in the docstrong later on,
    """
    try:
        model_client = genai.Client()
        results =model_client.models.embed_content(
                contents = text,
                model = EMBEDDING_MODEL
                )
        return results.embeddings[0].values
    except Exception as e:
        print(f'[!] Error, Failed to embed the text: {text}')
        print(f'Error Caught: {e}')
        return None


# Now, a function to add the embeddings to the vectordb

def add_to_vector_db(filepath):
    """
    Reads a file, extracts text, generates an embedding,
    and stores it in the local Chroma vector database.

    Args:
        filepath (str): Path to the file.

    Returns:
        bool: True on success, False other-wise.
    """
    text = open_file(filepath)
    if not text:
        return False

    embedded = embedding(text)
    if embedded:
        collection.add(
            documents=[text],
            metadatas=[{"source": filepath}],
            embeddings=[embedded] ,
            ids=[filepath]  # using full path as unique ID
        )
        print(f"[+] Embedded and stored in Chroma: {filepath}")
        return True
    return False


# nOW, Deleting from vector

def delete_from_vector_db(filepath):
    """
    Removes an entry from the Chroma vector database.

    Args:
        filepath (str): Path used as the document ID.
    """
    try:
        collection.delete(ids=[filepath])
        print(f"[-] Removed from Chroma: {filepath}")
    except Exception as e:
        print(f"[!] Delete failed: {e}")


# client.persist()
