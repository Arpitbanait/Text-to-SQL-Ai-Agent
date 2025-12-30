# Text-to-SQL Generator

An AI-powered application that converts natural language queries into SQL statements using Large Language Models (LLM) with Retrieval Augmented Generation (RAG).

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![React](https://img.shields.io/badge/react-18.3-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.104+-green.svg)

## 🌟 Overview

This project provides an intelligent interface for converting natural language questions into accurate SQL queries. It combines the power of modern LLMs with RAG technology to understand your database schema and generate optimized SQL statements.

**Key Highlights:**
- 🤖 Natural language understanding with Claude/Anthropic AI
- 🔍 Context-aware SQL generation using RAG
- 💾 Vector database for efficient schema retrieval
- 🎨 Modern React frontend with real-time results
- ⚡ High-performance FastAPI backend
- 🐳 Docker-ready deployment
- 🔒 Built-in SQL validation and security

## 🏗️ Architecture

```
text2sql/
├── backend/              # FastAPI backend service
│   ├── app/             # Application code
│   ├── data/            # Schemas and vector database
│   ├── scripts/         # Utility scripts
│   └── tests/           # Test suite
│
├── frontend/            # React frontend application
│   └── attentive-ai-sql/
│       ├── src/         # Source code
│       └── public/      # Static assets
│
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites

- **Backend**: Python 3.9+, Redis (optional)
- **Frontend**: Node.js 18+, npm/yarn/pnpm/bun
- **API Keys**: Anthropic API key (or other LLM provider)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/text2sql.git
cd text2sql
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Create .env file with your settings (see backend/README.md)

# Initialize vector database
python scripts/setup_vector_db.py
python scripts/index_schemas.py

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

📖 **Detailed backend setup**: See [backend/README.md](backend/README.md)

### 3. Setup Frontend

```bash
cd frontend/attentive-ai-sql

# Install dependencies
npm install

# Configure environment
# Create .env file with VITE_API_BASE_URL (see frontend/attentive-ai-sql/README.md)

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

📖 **Detailed frontend setup**: See [frontend/attentive-ai-sql/README.md](frontend/attentive-ai-sql/README.md)

## 💡 Usage

1. **Start the backend server** (FastAPI)
2. **Start the frontend application** (React)
3. **Open your browser** to `http://localhost:5173`
4. **Select your database** from the dropdown
5. **Enter a natural language query** (e.g., "Show all customers who made purchases in the last 30 days")
6. **Get your SQL query** instantly!

### Example Queries

```
"List all patients admitted in the last week"
→ SELECT * FROM patients WHERE admission_date >= NOW() - INTERVAL '7 days'

"Show total sales by product category"
→ SELECT category, SUM(sales) FROM products GROUP BY category

"Find customers who haven't made a purchase in 6 months"
→ SELECT * FROM customers WHERE last_purchase_date < NOW() - INTERVAL '6 months'
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI
- **LLM**: LangChain + Anthropic Claude
- **Vector DB**: ChromaDB
- **Database**: SQLAlchemy (PostgreSQL, MySQL support)
- **Caching**: Redis
- **Validation**: Pydantic v2

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI**: Shadcn UI + Tailwind CSS
- **State**: TanStack Query
- **Routing**: React Router v6

## 🐳 Docker Deployment

### Backend

```bash
cd backend
docker build -t text2sql-backend .
docker run -p 8000:8000 --env-file .env text2sql-backend
```

### Frontend

```bash
cd frontend/attentive-ai-sql
docker build -t text2sql-frontend .
docker run -p 80:80 text2sql-frontend
```

### Docker Compose (Full Stack)

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend/data:/app/data

  frontend:
    build: ./frontend/attentive-ai-sql
    ports:
      - "80:80"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api
```

Run with: `docker-compose up -d`

## 📚 Documentation

- [Backend Documentation](backend/README.md) - API setup, endpoints, configuration
- [Frontend Documentation](frontend/attentive-ai-sql/README.md) - UI setup, customization, deployment

## 🔧 Configuration

### Backend Environment Variables

```env
# LLM Configuration
ANTHROPIC_API_KEY=your_key_here
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_TEMPERATURE=0.0

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
```

### Frontend Environment Variables

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_TITLE=Text-to-SQL Generator
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ --cov=app
```

### Frontend Tests

```bash
cd frontend/attentive-ai-sql
npm run test
```

## 📊 Features

### ✅ Current Features
- Natural language to SQL conversion
- Multiple database support (PostgreSQL, MySQL)
- Schema auto-detection and indexing
- Vector-based schema retrieval (RAG)
- SQL syntax validation
- Query caching with Redis
- Dark/Light theme UI
- Real-time query generation
- SQL syntax highlighting
- Copy to clipboard

### 🔜 Roadmap
- [ ] Query history and favorites
- [ ] Multiple LLM provider support
- [ ] Advanced SQL optimization suggestions
- [ ] Query explanation feature
- [ ] Batch query processing
- [ ] Excel/CSV upload support
- [ ] Custom prompt templates
- [ ] User authentication

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow existing code style
- Write tests for new features
- Update documentation
- Keep commits atomic and descriptive

## 🔒 Security

- Never commit `.env` files
- Use environment variables for sensitive data
- Implement rate limiting in production
- Validate and sanitize all inputs
- Use read-only database connections when possible
- Keep dependencies updated

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [LangChain](https://www.langchain.com/) - LLM orchestration
- [Anthropic](https://www.anthropic.com/) - Claude AI models
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Shadcn UI](https://ui.shadcn.com/) - UI components
- [Vite](https://vitejs.dev/) - Build tool

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/text2sql/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/text2sql/discussions)

## 🌐 Links

- **Documentation**: [Full Documentation](https://github.com/yourusername/text2sql/wiki)
- **API Docs**: `http://localhost:8000/docs` (when running)
- **Live Demo**: [Coming Soon]

---

Made with ❤️ by [Your Name]

**Star ⭐ this repository if you find it helpful!**
