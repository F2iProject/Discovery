# Contributing to Discovery

Thanks for your interest in contributing! Discovery is an open-source lab organization platform built by F2i Partners.

## Getting Started

1. Fork the repo
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Discovery.git`
3. Start the stack: `docker compose up -d`
4. Make your changes
5. Submit a pull request

## Development Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env      # adjust values if needed
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Code Style

- Python: Follow PEP 8. Type hints required on all function signatures.
- TypeScript: Use strict mode. Prefer functional components.
- Commit messages: Short, imperative mood. "Add equipment model" not "Added equipment model."

## Architecture

- All models use tenant isolation via `tenant_id`
- All deletions are soft deletes
- API follows RESTful conventions
- Every module gets: model → schema → endpoint → frontend page

## What We Need Help With

- Tests for all endpoints
- Documentation improvements
- Accessibility improvements
- Internationalization (i18n)
- UI polish and responsive design
- Docker Compose improvements

## License

By contributing, you agree that your contributions will be licensed under Apache 2.0.
