import sqlite3
from typing import Optional, List, Dict, Any

class SQLiteReader:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_tables(self) -> List[str]:
        """Get List of all Tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            return [row[0] for row in cursor.fetchall()]

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get Table information"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Get Columns
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            
            return {
                'columns': columns,
                'row_count': row_count,
                'column_names': [col[1] for col in columns]
            }
            
    def query(self, sql: str, limit: int = 100) -> List[tuple]:
        """Execute custom query"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            return cursor.fetchmany(limit)
    
    def to_text(self, include_data: bool = True, max_rows: int = 10) -> str:
        """Convert database to readable text format"""
        text_parts = [f"SQLite Database: {self.db_path}"]
        
        tables = self.get_tables()
        text_parts.append(f"Tables: {len(tables)}")
        
        for table in tables:
            info = self.get_table_info(table)
            text_parts.append(f"\n=== {table} ===")
            text_parts.append(f"Columns: {', '.join(info['column_names'])}")
            text_parts.append(f"Rows: {info['row_count']}")
            
            if include_data and info['row_count'] > 0:
                rows = self.query(f"SELECT * FROM {table} LIMIT {max_rows}")
                text_parts.append("\nSample data:")
                for row in rows:
                    text_parts.append(" | ".join(str(cell) for cell in row))
        
        return '\n'.join(text_parts)

reader = SQLiteReader('database/CHROMA_STORE/chroma.sqlite3')
content = reader.to_text()
print(content)