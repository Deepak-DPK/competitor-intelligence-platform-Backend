# CompeteIQ Backend — Travel Agency Intelligence API

This is the backend service for the CompeteIQ Travel Intelligence Platform. It is a high-performance REST API built with FastAPI, designed to orchestrate data extraction, process analytics, and serve real-time insights to the [Frontend Application](https://github.com/Deepak-DPK/Competitor-Intelligence-Platform).

## System Architecture Overview

The backend acts as the central brain of the platform, coordinating between external services and the internal database:
- **Framework**: Python 3.12+ with FastAPI.
- **Database**: PostgreSQL with `asyncpg` for non-blocking database queries, managed by SQLAlchemy ORM and Alembic migrations.
- **Authentication**: Supabase Auth (JWT validation).
- **Data Scraping**: Integrated with the Firecrawl API to extract HTML DOM changes and pricing data from competitor websites.
- **AI Processing**: Integrated with Google Gemini 1.5 Pro via `google-genai` to generate strategic insights from scraped data.

## Features
- **Travel Workspaces API**: Full CRUD operations to manage intelligence projects by market or region.
- **Competitor Tracking API**: Endpoints to manage OTA and Travel Agency tracking targets.
- **Real-Time Data Pipelines**: Endpoints designed to trigger background scraping tasks via Firecrawl.
- **Alerts & Reporting System**: APIs to manage rate parity violation notifications and configure PDF/CSV scheduled reports.

## Local Development Setup

### Prerequisites
- Python 3.12+
- PostgreSQL (or use the configured SQLite fallback for simple testing)
- API Keys: Supabase, Firecrawl, and Google Gemini.

### Installation & Execution

1. **Set up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file based on the required variables:
   ```env
   # API Configuration
   SECRET_KEY=your_secure_secret_string
   CORS_ORIGINS=http://localhost:5173
   
   # Database (Render PostgreSQL URL)
   DATABASE_URL=postgresql+asyncpg://user:password@host/dbname
   
   # External Integrations
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   GEMINI_API_KEY=your-gemini-key
   FIRECRAWL_API_KEY=your-firecrawl-key
   ```

4. **Run Database Migrations**:
   Ensure your database schema is up-to-date:
   ```bash
   alembic upgrade head
   ```

5. **Start the Development Server**:
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be accessible at `http://localhost:8000`. You can view the interactive Swagger API documentation at `http://localhost:8000/docs`.

## Cloud Deployment

This backend is pre-configured for deployment on **Render.com**.
- A `render.yaml` blueprint is provided in the repository.
- A multi-stage `Dockerfile` handles the installation of OS-level dependencies (like `libpq-dev` for PostgreSQL and Playwright browser binaries) alongside Python packages.
- During deployment on Render, ensure you provide all the necessary environment variables detailed in the setup section.
