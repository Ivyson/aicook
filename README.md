# AICook

AICook is your personal academic sidekick crafted for computer engineering students. It automatically watches the folders you work in, transforms new and updated documents into semantic embeddings, and delivers context-aware help through an easy-to-use chat interface.

## What AICook offers

- **Live Document Monitoring**: Keeps tabs on your specified folders and processes files as soon as they change.
- **Broad Format Compatibility**: Extracts content from over 25 types of files—PDFs, Word docs, images (with OCR), code snippets, databases, and more.
- **Efficient Semantic Search**: Stores embeddings in ChromaDB for lightning-fast retrieval.
- **AI-Driven Assistance**: Provides precise, practical answers using Google’s Gemini models.
- **Student-Focused Guidance**: Optimized prompts to help with essays, problem solving, code examples, and technical explanations.
- **Built-In Database Explorer**: Inspect SQLite databases directly within the tool.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   File Watcher  │───▶│  File Processor  │───▶│   Embedding     │
│   (Handler.py)  │    │ (FileHandler.py) │    │ (embedding_     │
└─────────────────┘    └──────────────────┘    │  pipeline.py)   │
                                               └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Chat Interface │◀───│   Vector Query   │◀───│   ChromaDB      │
│(chat_interface) │    │                  │    │   Storage       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Project Structure

```
aicook/
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies 
├── .gitignore               # Git ignore rules
├── chat_interface.py        # Main chat application
├── embedding_pipeline.py    # Text embedding and vector storage
├── FileHandler.py           # Multi-format file processing
├── Handler.py               # File system monitoring
├── DbViewer.py             # SQLite database inspection
└── database/
    ├── index.db            # File tracking database
    └── CHROMA_STORE/       # Vector database storage
        └── chroma.sqlite3
```

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Google Gemini API key
- Git (for cloning)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Ivyson/aicook.git
cd aicook
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
```

### 2. Setup API Key


- Set your Gemini API key as an environment variable

### On macOS/Linux:
```bash
export GEMINI_API_KEY="your_api_key_here"
# Or add to your shell profile (.bashrc, .zshrc, etc.)
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.zshrc
```

### On Windows (Command Prompt):
```cmd
set GEMINI_API_KEY=your_api_key_here
```

### On Windows (PowerShell):
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
# To make it permanent, add it to your profile script
Add-Content -Path $PROFILE -Value 'Set-Item -Path Env:GEMINI_API_KEY -Value "your_api_key_here"'
```


### 3. Configure Watched Directory

Edit the path in `Handler.py` line 9:
```python
WATCHED_DIR = os.path.expanduser("~/YourDocuments/Path")
```

### 4. Run the Application

```bash
python chat_interface.py
```

## Usage Guide

### Basic Chat Commands

```
Ask something: explain, Fourier Transform using the complex notation.
Ask something: What is the time complexity of Binary Search
Ask something: exit  # Quit the application
```

### Supported File Types

| Category | Extensions | Processing Method |
|----------|------------|------------------|
| **Text** | .txt, .md, .rst, .log | Direct text reading |
| **Documents** | .pdf, .docx, .odt | Text extraction |
| **Data** | .json, .csv, .tsv, .xml, .html | Structured parsing |
| **Code** | .py, .js, .java, .cpp, .c, .sql | Syntax-aware reading |
| **Office** | .xlsx, .xls, .pptx | Content extraction |
| **Images** | .jpg, .png, .bmp, .tiff | OCR text recognition |
| **Archives** | .zip, .tar, .gz | Content listing |
| **Databases** | .db, .sqlite, .sqlite3 | Schema and data analysis |

### How It Works

1. **File Monitoring**: The system watches your configured directory for changes. Whenever a new file is added, or and existing file is mortified, the system detects these changes automatically using `watchdog`
2. **Content Extraction**: When new or updated file is detected, the system processes it to extract the text content. Currently, the content being pulled out of a file is just text.
3. **Embedding Creation**: The extracted text is then converted into a numerical format called "vector embeddings." These embeddings are created using a model called `gemini-embedding-exp-03-07`, this step transforms the text into a format that a computer can understand and use for advanced tasks like searching or comparing meanings.
4. **Storage**: The generated embeddings are stored in a database called ChromaDB. This database is optimized for semantic search, it can quickly find embeddings that are similar in meaning to a given query.
5. **Query Processing**: When you ask a question or make a query, the system searches the stored embeddings in ChromaDB to find the most relevant documents. This is done by comparing the query's embedding with the stored embeddings to identify matches 
6. **Response Generation**: Finally, the system combines the context from the retrieved documents with your query and sends it to Gemini, which generates a detailed, academic-style response. This ensures that the answers are both accurate and contextually relevant.

## Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional
CHROMA_TELEMETRY_ENABLED=false  # Disable ChromaDB telemetry
```

### Customization Options

**In `embedding_pipeline.py`:**
```python
CHROMA_DIR = './database/CHROMA_STORE'  # Vector DB location
EMBEDDING_MODEL = 'gemini-embedding-exp-03-07'  # Embedding model
```

**In `Handler.py`:**
```python
WATCHED_DIR = "your/documents/path"  # Directory to monitor
DB_PATH = "./database/index.db"  # File tracking database
```

**In `chat_interface.py`:**
```python
model = "gemini-2.5-flash"  # Chat model
n_results = 5  # Number of Relevant documents to retrieve
```

## Advanced Usage

### Database Inspection

```python
# View ChromaDB contents
from DbViewer import SQLiteReader

reader = SQLiteReader('database/CHROMA_STORE/chroma.sqlite3')
print(reader.to_text())
```

### Manual File Processing

```python
from embedding_pipeline import add_to_vector_db, delete_from_vector_db

# Add specific file
add_to_vector_db("/path/to/document.pdf")

# Remove file from database
delete_from_vector_db("/path/to/document.pdf")
```

### Custom File Handlers

Add new file type support in `FileHandler.py`:

```python
# In FileProcessor.__init__
self.handlers['.your_extension'] = self._read_your_format

def _read_your_format(self, file_path: str) -> str:
    # Your custom processing logic
    return extracted_text
```

## Contributing

We welcome contributions! Here's how to get started:

### Contribution Areas

#### High Priority
- [ ] Add comprehensive test suite
- [ ] Implement configuration file (YAML/JSON)
- [ ] Add retry logic for API failures
- [ ] Improve error handling and logging
- [ ] Add progress indicators for large file processing

#### Enhancements
- [ ] Support for more file formats (epub, mobi, etc.)
- [ ] Web interface using Streamlit/Gradio
- [ ] Batch processing for existing document collections
- [ ] Document similarity and clustering features
- [ ] Export/import functionality for embeddings

#### Bug Fixes
- [ ] Handle large files more efficiently
- [ ] Fix memory leaks in file processing
- [ ] Improve Unicode handling in text extraction
- [ ] Better handling of corrupted files

#### Documentation
- [ ] Add API documentation
- [ ] Create video tutorials
- [ ] Write troubleshooting guide
- [ ] Add performance optimization tips


## Troubleshooting

### Common Issues

#### API Key Errors
```bash
# Error: GEMINI_API_KEY not found
export GEMINI_API_KEY="your_key"
# Or add to your shell profile permanently
```

#### Permission Errors
```bash
# If files can't be accessed
chmod +r /path/to/your/documents
# Ensure Python has read access to watched directories
```

#### Memory Issues with Large Files
```python
# In FileHandler.py, adjust the size limit
max_size = 10 * 1024 * 1024  # Reduce to 10MB instead of 50MB
```

#### ChromaDB Issues
```bash
# Clear the database if corrupted
rm -rf database/CHROMA_STORE
# Restart the application to recreate
```

### Performance Tips

1. **Exclude Unnecessary Directories**: Configure `.gitignore` to exclude directories that are not relevant to the project, such as temporary files or large datasets. This prevents the git watcher from monitoring unnecessary changes.

2. **Limit File Sizes**: Adjust the `MAX_FILE_SIZE` parameter in `FileHandler` to avoid processing excessively large files. Large files can significantly slow down the system, consume more memory, and potentially cause crashes. By setting a reasonable size limit, you ensure that the application remains responsive and efficient. Also, google gemini has a cap of tokens that can be processed per minute, so confirm those and ensure that you remain within the free tier if that is what suits your needs.
