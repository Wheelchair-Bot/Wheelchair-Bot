# Getting Started with Wheelchair Bot

This guide will help you set up and run the Wheelchair Bot project on your local machine.

## Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- npm 9 or higher

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/mrhegemon/Wheelchair-Bot.git
cd Wheelchair-Bot
```

### 2. Install Python dependencies

Install the shared library first:

```bash
cd packages/shared
pip install -e ".[dev]"
cd ../..
```

Install the backend:

```bash
cd packages/backend
pip install -e ".[dev]"
cd ../..
```

### 3. Install Node.js dependencies

```bash
npm install
```

This will install dependencies for all workspaces.

## Running the Application

### Start the Backend

In one terminal:

```bash
cd packages/backend
python -m wheelchair_bot.main
```

The API will be available at `http://localhost:8000`

### Start the Frontend

In another terminal:

```bash
cd packages/frontend
npm run dev
```

The web interface will be available at `http://localhost:3000`

## Development

### Running Tests

Backend tests:

```bash
cd packages/backend
pytest
```

Shared library tests:

```bash
cd packages/shared
pytest
```

### Code Formatting

Format Python code:

```bash
black packages/
```

### Linting

Lint Python code:

```bash
ruff check packages/
```

Lint frontend code:

```bash
cd packages/frontend
npm run lint
```

## Project Structure

```
Wheelchair-Bot/
├── packages/
│   ├── backend/           # FastAPI backend service
│   ├── frontend/          # React web interface
│   └── shared/            # Shared utilities and types
├── docs/                  # Documentation
├── pyproject.toml         # Root Python configuration
├── package.json           # Root Node.js configuration
└── README.md              # Main README
```

## Next Steps

- Check out the [API Documentation](./api.md)
- Read the [Architecture Guide](./architecture.md)
- Learn about [Contributing](../CONTRIBUTING.md)
