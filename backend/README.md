# Text-to-SQL Backend API

A powerful AI-powered API that converts natural language queries into SQL statements using Large Language Models (LLM) with Retrieval Augmented Generation (RAG).

## Features

- 🤖 Natural language to SQL conversion using LLMs (GPT-4, Claude, Anthropic)
- 🔍 RAG-based schema retrieval for accurate context
- 💾 Vector database (ChromaDB) for efficient schema storage and retrieval
- 🔒 SQL validation and security checks
- ⚡ Fast API with async support
- 🐳 Docker support for easy deployment
- 📊 Support for multiple database types (PostgreSQL, MySQL, etc.)
- 🚀 Redis caching for improved performance

## Tech Stack

- **Framework**: FastAPI
- **LLM Integration**: LangChain with Anthropic Claude
- **Vector Database**: ChromaDB
- **Embeddings**: Sentence Transformers
- **Database**: SQLAlchemy (PostgreSQL, MySQL)
- **Caching**: Redis
- **Validation**: Pydantic v2

## Prerequisites

- Python 3.9 or higher
- pip or conda
- Redis server (optional, for caching)
- Anthropic API key (or other LLM provider)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd text2sql/backend
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the `backend` directory with the following variables:

```env
# LLM Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=2000

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
# Or for MySQL:
# DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Vector Database
VECTOR_DB_PATH=./data/vector_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### 5. Initialize Vector Database

Index your database schemas and examples:

```bash
python scripts/setup_vector_db.py
python scripts/index_schemas.py
```

### 6. Run the Application

**Development Mode:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production Mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

### 7. API Documentation

Once running, access the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Docker Deployment

### Build and Run with Docker

```bash
# Build the image
docker build -t text2sql-backend .

# Run the container
docker run -p 8000:8000 --env-file .env text2sql-backend
```

### Using Docker Compose

Create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./backend/data:/app/data
```

Run with:
```bash
docker-compose up -d
```

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes and endpoints
│   │   └── routes/       # Individual route handlers
│   ├── core/             # Core business logic
│   │   ├── database/     # Database connections and schema extraction
│   │   ├── llm/          # LLM clients, chains, and prompts
│   │   ├── rag/          # RAG indexing and retrieval
│   │   └── sql/          # SQL generation and validation
│   ├── models/           # Pydantic models for request/response
│   ├── services/         # Business logic services
│   └── utils/            # Utility functions and helpers
├── data/
│   ├── examples/         # Example queries and patterns
│   ├── schemas/          # Database schema files
│   └── vector_db/        # ChromaDB storage
├── scripts/              # Utility scripts
├── tests/                # Test suite
├── requirements.txt      # Python dependencies
└── Dockerfile           # Docker configuration
```

## API Endpoints

### Health Check
```http
GET /api/health
```

### Generate SQL from Natural Language
```http
POST /api/query/generate
Content-Type: application/json

{
  "query": "Show me all patients admitted in the last 30 days",
  "database_name": "hospital_db"
}
```

### Get Database Schema
```http
GET /api/schema/{database_name}
```

### Index New Schema
```http
POST /api/schema/index
Content-Type: application/json

{
  "database_name": "my_db",
  "connection_string": "postgresql://..."
}
```

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api/test_query.py
```

## Troubleshooting

### Common Issues

**1. ChromaDB initialization fails**
- Ensure the `data/vector_db` directory exists
- Run `python scripts/setup_vector_db.py`

**2. LLM API errors**
- Verify your API key is correct in `.env`
- Check your API quota/credits

**3. Database connection errors**
- Verify DATABASE_URL format
- Ensure database server is running
- Check firewall settings

**4. Redis connection fails**
- Redis is optional; the app will work without it
- To use Redis, ensure Redis server is running
- Update REDIS_URL in `.env`

## Performance Optimization

- Enable Redis caching for repeated queries
- Use connection pooling for database connections
- Increase `--workers` for production deployment
- Index frequently used schemas

## Security Notes

- Never commit `.env` file to version control
- Use environment variables for sensitive data
- Implement rate limiting in production
- Validate and sanitize all SQL outputs
- Use read-only database connections when possible

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions, please open an issue on GitHub

```bash
python scripts/setup_vector_db.py
```

### 4. Index Database Schemas

```bash
python scripts/index_schemas.py
```

### 5. Run the Application

```bash
uvicorn app.main:app --reload
```

API will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

## Docker Deployment

```bash
docker build -t text2sql-api .
docker run -p 8000:8000 --env-file .env text2sql-api
```

## API Endpoints

### Convert Text to SQL
```
POST /api/v1/query/text-to-sql
Body: {
  "query": "Show me all active users",
  "database": "main_db"
}
```

### Index Database Schema
```
POST /api/v1/schema/index
Body: {
  "connection_string": "postgresql://...",
  "database_name": "my_database"
}
```

## Technology Stack

- **FastAPI**: Modern web framework
- **LangChain**: LLM application framework
- **Anthropic Claude**: LLM provider (Claude 3.5 Sonnet)
- **HuggingFace**: Embedding models (sentence-transformers)
- **ChromaDB**: Vector database
- **SQLAlchemy**: Database toolkit
- **Redis**: Caching layer

## Development

### Run Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
flake8 app/
```

## License

MIT License
