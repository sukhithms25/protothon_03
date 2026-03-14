# AI-Powered GitHub Issue Fixer

A FastAPI-based platform that automatically fixes GitHub issues using AI and creates pull requests.

## Features

- **AI Issue Analysis**: Uses Gemini AI to understand and fix issues.
- **GitHub Integration**: Connects with GitHub to fetch issues and create PRs.
- **Database Persistence**: Stores repository data, issues, and PRs.
- **Authentication**: Secure JWT-based authentication.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file in the root directory with the following variables:

    ```env
    GITHUB_TOKEN=your_github_token
    GITHUB_OWNER=your_github_username
    GITHUB_REPO=your_repo_name
    GEMINI_API_KEY=your_gemini_api_key
    DATABASE_URL=sqlite:///./test.db
    ```

3.  **Database Initialization**:
    Run the following commands to create the database tables:

    ```bash
    python -c "from database import init_db; init_db()"
    ```

## Usage

### Start the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

### API Endpoints

#### Authentication

-   **POST /api/auth/register** - Register a new user.
-   **POST /api/auth/login** - Login and get an access token.

#### GitHub Integration

-   **GET /api/github/repo** - Get repository information.
-   **GET /api/github/issues** - Get open issues.
-   **GET /api/github/prs** - Get open pull requests.
-   **POST /api/github/issues** - Create a new issue.

#### AI Agents

-   **POST /api/agents/fix-issue** - Fix an issue using AI.
    -   **Body**: `{"issue_number": 123}`

## Project Structure

-   `main.py`: FastAPI application entry point.
-   `config.py`: Configuration settings.
-   `auth.py`: Authentication logic.
-   `database.py`: Database setup and models.
-   `services/`: Service layer (GitHub, LLM, Agents).
-   `agents/`: AI agent implementations.
-   `models/`: SQLAlchemy database models.