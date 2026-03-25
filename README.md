Chat App (SaaS MVP)

Full-stack SaaS chat application with authentication and AI-powered responses.

Overview

This project implements a minimal SaaS-style chat system where users can:

Register and log in using email + verification code
Send messages to an AI service
View persistent chat history

The backend handles authentication, message storage, and AI interaction.
The frontend provides a simple interface for user interaction.

Tech Stack

Backend

Python (FastAPI)
SQLAlchemy (ORM)
SQLite (database)
JWT authentication

Frontend

React (TypeScript)
Axios (API client)
Vite (build tool)
Architecture
Stateless JWT-based authentication
Relational data model (users ↔ messages)
Backend integrates with external LLM API
Chat context limited to recent messages for scalability
Project Structure
backend/
├─ main.py
├─ database.py
├─ models.py
├─ schemas.py
├─ auth.py
├─ chat.py
├─ utils.py
├─ requirements.txt

frontend/
├─ src/
│  ├─ api/
│  ├─ components/
│  ├─ App.tsx
│  └─ main.tsx
├─ package.json
Setup & Run
1. Clone repository
git clone <repo-url>
cd chat-app
2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

Create .env file:

JWT_SECRET=your_secret_key

Run server:

uvicorn main:app --reload

Backend runs on:

http://127.0.0.1:8000
3. Frontend setup
cd frontend
npm install
npm run dev

Frontend runs on:

http://127.0.0.1:5173
API Overview
Auth
POST /auth/register → register user (returns code for demo)
POST /auth/login → returns JWT token
Chat
POST /chat/message → send message (auth required)
GET /chat/history → retrieve chat history
Key Implementation Details
Passwordless login using one-time code (hashed with bcrypt)
JWT used for stateless authentication
Chat messages persisted before and after AI response
Context window limited (MAX_CONTEXT_MESSAGES) to control cost and latency
External LLM API call includes retry logic for resilience
Notes
.env, database files, and dependencies are excluded from version control
Registration returns the login code directly (demo purpose only)
Future Improvements
Replace demo auth with email delivery
Add streaming responses for better UX
Improve error handling and validation
Add tests and API documentation