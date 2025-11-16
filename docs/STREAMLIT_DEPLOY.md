# Streamlit Deployment Guide

This guide provides instructions for running the Hepatitis B Forecasting Dashboard locally, with Docker, and deploying to Streamlit Community Cloud.

---

## Prerequisites

- Python 3.10 or higher (for local runs)
- Docker and Docker Compose (for containerized runs)
- GitHub account (for Streamlit Community Cloud deployment)

---

## Option 1: Run Locally

### Steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/buriro-ezekia/-Hepatitis-B-Predictive-Modelling-and-Forecasting-Benjamin-Mkapa-Hospital-BMH-.git
   cd -Hepatitis-B-Predictive-Modelling-and-Forecasting-Benjamin-Mkapa-Hospital-BMH-
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

4. **Access the app:**
   Open your browser and navigate to `http://localhost:8501`

---

## Option 2: Run with Docker

### Steps:

1. **Clone the repository (if not already done):**
   ```bash
   git clone https://github.com/buriro-ezekia/-Hepatitis-B-Predictive-Modelling-and-Forecasting-Benjamin-Mkapa-Hospital-BMH-.git
   cd -Hepatitis-B-Predictive-Modelling-and-Forecasting-Benjamin-Mkapa-Hospital-BMH-
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

   Alternatively, build and run manually:
   ```bash
   docker build -t hep-forecast .
   docker run -p 8501:8501 hep-forecast
   ```

3. **Access the app:**
   Open your browser and navigate to `http://localhost:8501`

4. **Stop the container:**
   Press `Ctrl+C` or run:
   ```bash
   docker-compose down
   ```

---

## Option 3: Deploy to Streamlit Community Cloud

Streamlit Community Cloud is a free hosting service for Streamlit apps connected to GitHub repositories.

### Steps:

1. **Prepare your repository:**
   - Ensure your repository is public (or private with appropriate permissions)
   - Make sure `app.py` and `requirements.txt` are in the root directory
   - Push all changes to your GitHub repository

2. **Sign in to Streamlit Community Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

3. **Deploy a new app:**
   - Click **"New app"**
   - Select your GitHub repository: `buriro-ezekia/-Hepatitis-B-Predictive-Modelling-and-Forecasting-Benjamin-Mkapa-Hospital-BMH-`
   - Choose the branch (typically `main`)
   - Set the main file path: `app.py`
   - Click **"Advanced settings"** if you need to:
     - Set environment variables or secrets
     - Adjust Python version
     - Configure custom domains

4. **Deploy:**
   - Click **"Deploy!"**
   - Streamlit will build and deploy your app
   - You'll receive a public URL (e.g., `https://your-app-name.streamlit.app`)

5. **Managing your app:**
   - Any push to your chosen branch will automatically redeploy the app
   - You can manage settings, view logs, and reboot the app from the Streamlit dashboard

### Setting Secrets (Optional)

If your app requires API keys or sensitive configuration:

1. In the Streamlit Cloud dashboard, click on your app
2. Go to **"Settings"** → **"Secrets"**
3. Add secrets in TOML format:
   ```toml
   # Example secrets
   api_key = "your-api-key"
   database_url = "your-database-url"
   ```
4. Access secrets in your app using:
   ```python
   import streamlit as st
   api_key = st.secrets["api_key"]
   ```

---

## Troubleshooting

### Local Run Issues

- **Import errors:** Ensure all dependencies in `requirements.txt` are installed
- **Port already in use:** Change the port with `streamlit run app.py --server.port=8502`

### Docker Issues

- **Build fails:** Check that `requirements.txt` is present and correctly formatted
- **Container exits immediately:** Check logs with `docker logs <container-id>`
- **Permission errors:** On Linux, you may need to run Docker commands with `sudo` or add your user to the `docker` group

### Streamlit Cloud Issues

- **Build fails:** Check the build logs in the Streamlit dashboard
- **App crashes:** Review the logs and ensure all dependencies are in `requirements.txt`
- **Secrets not working:** Verify secrets are correctly formatted in TOML and accessible in your code

---

## Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Docker Documentation](https://docs.docker.com)
- [Streamlit Community Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)

---

## Support

For issues specific to this project, please open an issue on the [GitHub repository](https://github.com/buriro-ezekia/-Hepatitis-B-Predictive-Modelling-and-Forecasting-Benjamin-Mkapa-Hospital-BMH-/issues).
