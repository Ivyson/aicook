#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import sqlite3
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from embedding_pipeline import delete_from_vector_db, add_to_vector_db
import warnings

# Suppress specific warnings Form Watchdog
warnings.filterwarnings("ignore", category=UserWarning, module='watchdog')
DB_PATH = "./database/index.db"
WATCHED_DIR = os.path.expanduser("""~/OneDrive - Cape Peninsula University of Technology/My Scripts/PlayGround""")



def init_db():
    '''
    Checks if the database exists, and creates it if not existing
    This database will be used to Track and store changes
    '''
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                filepath TEXT PRIMARY KEY,
                last_modified REAL,
                file_hash TEXT
            )
        ''')
        conn.commit()

def get_file_record(path):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT last_modified, file_hash FROM files WHERE filepath = ?", (path,))
        return cursor.fetchone()

def upsert_file_record(path, modified, hash):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO files (filepath, last_modified, file_hash)
            VALUES (?, ?, ?)
            ON CONFLICT(filepath) DO UPDATE SET
                last_modified=excluded.last_modified,
                file_hash=excluded.file_hash
        ''', (path, modified, hash))
        conn.commit()

def delete_file_record(path):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM files WHERE filepath = ?", (path,))
        conn.commit()

def compute_file_hash(path):
    hasher = hashlib.md5()
    try:
        with open(path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"[!] Error hashing file {path}: {e}")
        return None

# Watchdog Event Handler
class RAGFileEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            self.process(event.src_path, event_type='created')


    def on_modified(self, event):
        if not event.is_directory:
            self.process(event.src_path, event_type='modified')

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"[-] File deleted: {event.src_path}")
            delete_file_record(event.src_path)
            # TODO: Delete from vector DB
            delete_from_vector_db(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            print(f"[→] File moved from {event.src_path} to {event.dest_path}")
            delete_file_record(event.src_path)
            delete_from_vector_db(event.src_path)
            self.process(event.dest_path, event_type='moved')

    def process(self, path, event_type):
        if not os.path.exists(path):
            print(f"[!] Skipped missing file: {path}")
            return

        try:
            current_modified = os.path.getmtime(path)
            current_hash = compute_file_hash(path)
        except Exception as e:
            print(f"[!] Error accessing file {path}: {e}")
            return

        if current_hash is None:
            print(f"[!] Could not hash file: {path}")
            return

        record = get_file_record(path)

        if record is None:
            print(f"[+] New file: {path}")
            upsert_file_record(path, current_modified, current_hash)


            add_to_vector_db(path)
        else:
            last_modified, last_hash = record
            if current_hash != last_hash:
                print(f"[*] Modified content: {path}")
                upsert_file_record(path, current_modified, current_hash)
              
                add_to_vector_db(path)
            else:
                print(f"[=] Unchanged file: {path} (skip)")


def start_watching(folder_path):
    init_db()

    if not os.path.exists(folder_path):
        print(f"Error: Watched directory does not exist: {folder_path}")
        return
   
    print(f"Watching: {folder_path}")
    event_handler = RAGFileEventHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping watcher...")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watching(WATCHED_DIR)

