# Bill Genius: AI-Powered Invoice Extraction Pipeline

A production-ready full-stack application that automates the extraction of invoice data from PDFs and saves it to Google Sheets.

## Architecture
- **Frontend**: Next.js 16 (Static Export) deployed to **Firebase Hosting**.
- **Backend**: FastAPI + Docling (Python 3.13) deployed to **Google Cloud Run**.
- **Data Store**: Google Sheets.

## Key Features
- **High-Precision Parsing**: Uses Docling's layout-aware engine for reliable field extraction.
- **Service Account Impersonation**: Secure, per-request identity management for Google Cloud integrations.
- **Glassmorphism UI**: Premium dashboard designed for clarity and speed.

## Quick Start (Local Development)

### Backend
1. Go to `backend-extraction/`.
2. Install dependencies: `uv pip install -r requirements.txt`.
3. Create `.env` based on `.env.example`.
4. Run: `python main.py`.

### Frontend
1. Go to `frontend/`.
2. Install dependencies: `npm install`.
3. Create `.env.local` with `NEXT_PUBLIC_BACKEND_URL=http://localhost:8000`.
4. Run: `npm run dev`.

## Deployment
Refer to [deployment_guide.md](./deployment_guide.md) for detailed instructions on deploying to Google Cloud and Firebase.
