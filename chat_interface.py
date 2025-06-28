#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script starts the watchdog file monitoring and RAG-based chat interface simultaneously.
Watchdog monitors file changes and keeps Chroma vector DB in sync.
Chat interface queries Chroma DB for relevant documents and uses Gemini for response generation.
"""
from rich.console import Console
from rich.markdown import Markdown

console = Console()

import threading
import os
import time
from google import genai
from embedding_pipeline import collection, embedding  # Uses same chroma & Gemini config
from Handler import start_watching
from google.genai import types

#API_KEY = os.getenv("GEMINI_API_KEY") #API is now taken from the environmnet by default.
#if not API_KEY:
#    raise EnvironmentError("GEMINI_API_KEY not found in environment variables.")

#genai.configure(api_key=API_KEY)

# Background Watchdog Thread

def start_watchdog_thread():
    thread = threading.Thread(target=start_watching, args=(os.path.expanduser("~/OneDrive - Cape Peninsula University of Technology/My Scripts/PlayGround"),))
    thread.daemon = True
    thread.start()
    print("Watchdog started in background...")


# Chat Interface

def start_chat():
    print("\nChat Interface is ready. Type 'exit' to quit.")
    while True:
        query = input("\nAsk something: ")
        if query.lower() in ["exit", "quit"]:
            break

        try:
            print('Embedding...')
            query_embedding = embedding(query)
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=5
            )
            
            # print('trying to get documents')
            documents = results.get("documents", [[]])[0]
            sources = results.get("metadatas", [[]])[0]
            # print('checking if documents is not empty')
            if documents:
                # print('documents not empty')
                context = "\n\n".join(documents)
                prompt = f"""You are an academic assistant for a computer engineering student. Provide focused, practical answers.

                        CONTEXT: {context}

                        QUERY: {query}

                        Instructions:
                        - Use the context above as your primary source
                        - If context is insufficient, apply relevant computer engineering principles
                        - Focus on technical accuracy and practical application
                        - Provide step-by-step solutions for problems
                        - Include relevant formulas, algorithms, or code snippets when applicable
                        - Avoid generic conclusions - be specific and actionable
                        - If it's an essay question, structure with clear technical points
                        - For problem-solving, show methodology and reasoning
                        - If you don't know the answer, say "I don't know" instead of guessing
                        - If you need more information, ask for it
                        """
            else:
                prompt = query
            client = genai.Client()
            print('parsing to LLM')
            response = client.models.generate_content(
                    model = "gemini-2.5-flash",
                    contents = prompt,
                    config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0) # Disable thinking budget 
    ),
                    )

            console.print(Markdown(f"\nResponse: {response.text}"))
            # console.print(Markdown(response.text))
        except Exception as e:
            print(f"[!] Error generating response: {e}")


# Main Execution

if __name__ == "__main__":
    try:
        start_watchdog_thread()
        start_chat()
    except KeyboardInterrupt:
        print("\nExiting chat interface...")
    except Exception as e:
        print(f"[!] An error occurred: {e}")
    finally:
        print("Shutting down...")
        # All the necessary cleanup can will be done here. 
        #  Closing of openned connections, files etc...
        # client.close()
        print("Goodbye!")
        exit(0)

