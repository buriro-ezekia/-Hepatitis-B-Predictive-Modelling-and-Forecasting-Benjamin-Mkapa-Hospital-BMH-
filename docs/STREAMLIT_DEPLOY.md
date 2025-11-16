# Streamlit Deployment Guide

This document provides instructions for deploying the Hepatitis B Forecasting Streamlit dashboard locally, with Docker, and on Streamlit Community Cloud.

## Prerequisites

- Python 3.10+
- Docker and Docker Compose (for containerized deployments)
- Git

## Running Locally

### Option 1: Using Virtual Environment

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note:** If `streamlit` is not in `requirements.txt`, install it manually:
   ```bash
   pip install streamlit
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

4. Open your browser to `http://localhost:8501`

## Running with Docker

### Option 1: Docker Build and Run

1. Build the Docker image:
   ```bash
   docker build -t hep-forecast:latest .
   ```

2. Run the container:
   ```bash
   docker run -p 8501:8501 hep-forecast:latest
   ```

3. Access the app at `http://localhost:8501`

**Note:** If the entrypoint is different from `app.py`, update the `CMD` line in the `Dockerfile`:
```dockerfile
CMD ["streamlit", "run", "your_entrypoint.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Option 2: Docker Compose

1. Start the application:
   ```bash
   docker-compose up
   ```

2. Access the app at `http://localhost:8501`

3. Stop the application:
   ```bash
   docker-compose down
   ```

**Optional: Enable PostgreSQL**

The `docker-compose.yml` includes a commented-out PostgreSQL service for data persistence. To enable it:

1. Uncomment the `db` service and `volumes` section in `docker-compose.yml`
2. Update the `web` service's `depends_on` to include `db`
3. Configure your application to connect to PostgreSQL using:
   - Host: `db`
   - Port: `5432`
   - Database: `forecasts`
   - User: `postgres`
   - Password: `postgres`

## Deploying to Streamlit Community Cloud

### Steps

1. **Fork or push this repository** to your GitHub account

2. **Sign in to Streamlit Community Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

3. **Deploy your app**
   - Click "New app"
   - Select your repository
   - Choose the branch (e.g., `main` or `chore/deploy/streamlit`)
   - Set the main file path: `app.py`
   - Click "Deploy"

4. **Configure secrets (if needed)**
   - In the app settings, go to "Advanced settings"
   - Add any required secrets in TOML format:
     ```toml
     [secrets]
     API_KEY = "your-api-key"
     DATABASE_URL = "your-database-url"
     ```

5. **Your app will be live** at a URL like `https://your-app-name.streamlit.app`

### Requirements

Ensure `requirements.txt` includes all dependencies:
- If `streamlit` is missing, add it to `requirements.txt` before deploying
- Streamlit Community Cloud will automatically install all packages listed

## Troubleshooting

### Docker build fails

- Check that `requirements.txt` is present and contains `streamlit`
- If missing, either add `streamlit` to `requirements.txt` or modify the Dockerfile to install it directly:
  ```dockerfile
  RUN pip install --no-cache-dir streamlit -r requirements.txt
  ```

### Port conflicts

- If port 8501 is already in use, change the port mapping:
  - Docker: `docker run -p 8502:8501 hep-forecast:latest`
  - Docker Compose: Edit `docker-compose.yml` to use `"8502:8501"`

### Application doesn't start

- Verify the entrypoint file exists: `app.py`
- Check logs: `docker logs <container-id>` or `docker-compose logs`

## CI/CD

The repository includes a GitHub Actions workflow (`.github/workflows/docker-ci.yml`) that:
- Builds the Docker image on every push to `main`
- Validates that the image builds successfully
- Runs on pull requests to ensure changes don't break the build

## Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Docker Documentation](https://docs.docker.com)
- [Streamlit Community Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
