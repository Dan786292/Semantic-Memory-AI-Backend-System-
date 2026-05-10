AI Conversational Backend

Backend service for an AI-powered conversational assistant with semantic memory retrieval, contextual prompt generation, and JWT-based authentication.

Features
FastAPI-based REST API
JWT authentication and protected routes
Semantic memory retrieval using embeddings
Context-aware prompt construction
External LLM integration
Structured logging and retry handling
Modular backend architecture
Persistent chat history storage
Tech Stack
Python
FastAPI
SQLAlchemy
SQLite
Sentence Transformers
JWT Authentication
Pydantic
Passlib / bcrypt
Architecture Overview

The system is divided into modular backend components:

Client
   |
FastAPI Routes
   |
Business Logic
   |
Database + Embedding Pipeline
   |
External LLM Service

Main modules:

auth.py — authentication and JWT handling
chat.py — chat flow and semantic retrieval
models.py — SQLAlchemy ORM models
schemas.py — API validation schemas
utils.py — embeddings, similarity search, LLM calls, sanitization
database.py — database session management
Semantic Memory Retrieval

The application stores vector embeddings for user messages and retrieves relevant historical context using cosine similarity scoring.

Retrieval Flow
User message is sanitized
Embedding vector is generated
Relevant historical messages are ranked by semantic similarity
Short-term and semantic memories are merged
Context-aware prompt is sent to the LLM
Authentication

Authentication is implemented using:

JWT access tokens
OAuth2 password flow
bcrypt hashing for verification codes
Protected API endpoints
API Endpoints
Auth
Method	Endpoint	Description
POST	/auth/register	Register user
POST	/auth/login	Login and receive JWT
Chat
Method	Endpoint	Description
POST	/chat/message	Send chat message
GET	/chat/history	Retrieve chat history
Running Locally
Clone repository
git clone <repo-url>
cd <repo-name>
Install dependencies
pip install -r requirements.txt
Configure environment

Create .env file:

JWT_SECRET=your_secret
APIFREE_LLM_URL=your_llm_endpoint
Run server
uvicorn main:app --reload
Example Technologies Demonstrated
REST API design
Authentication and authorization
AI application backend development
Embedding-based retrieval systems
Context engineering
Error handling and resiliency
Backend modularization
Future Improvements
PostgreSQL integration
Docker deployment
Async request handling
Redis caching
Vector database integration
Streaming LLM responses
Automated testing