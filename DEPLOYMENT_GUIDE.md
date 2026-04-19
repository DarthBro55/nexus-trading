# Deployment Guide

This guide provides comprehensive step-by-step instructions for deploying the Nexus Trading application to Streamlit Cloud and Railway. Follow each section closely to set up secrets, environment variables, API keys, and troubleshoot issues.

## Table of Contents
1. [Deployment to Streamlit Cloud](#deployment-to-streamlit-cloud)
2. [Deployment to Railway](#deployment-to-railway)
3. [Setting Up Secrets and Environment Variables](#setting-up-secrets-and-environment-variables)
4. [API Key Configuration](#api-key-configuration)
5. [Security Best Practices](#security-best-practices)
6. [Troubleshooting](#troubleshooting)
7. [Verification Checklist](#verification-checklist)

## Deployment to Streamlit Cloud
1. Go to [Streamlit Cloud](https://streamlit.io/cloud).
2. Click on "+ New app" and connect your GitHub account.
3. Select the `DarthBro55/nexus-trading` repository.
4. Choose the main branch and specify the path to your Streamlit app (e.g., `app.py`).
5. Click on "Deploy". Streamlit will install the required dependencies listed in `requirements.txt`.
6. **Setting Up Secrets**: After deployment, navigate to the app settings and add your API keys as secrets.

## Deployment to Railway
1. Visit [Railway](https://railway.app/) and create an account or log in.
2. Click on "+ New Project" and choose "+ Import from GitHub".
3. Select the `DarthBro55/nexus-trading` repository and connect it.
4. Railway will automatically detect the service and set up a Dockerfile. If you don't have a Dockerfile, you may need to configure it manually.
5. Set environment variables by navigating to the project's settings.
6. **Setting Up Secrets**: Add your API keys as secrets in the environment variables section.

## Setting Up Secrets and Environment Variables
- **Streamlit Cloud**:
  - Access secrets in your Streamlit app settings under "Secrets".
  - Enter the keys in a JSON format:
    ```
    {"POLYGON_API_KEY": "your_polygon_key",
     "ALPACA_API_KEY": "your_alpaca_key",
     "BINANCE_API_KEY": "your_binance_key",
     "COINBASE_API_KEY": "your_coinbase_key"}
    ```

- **Railway**:
  - Go to the environment section in your project settings.
  - Add each API key as a new variable using the same naming conventions.

## API Key Configuration
### Polygon.io
1. Sign up at [Polygon.io](https://polygon.io/).
2. Go to your account dashboard and get your API key.
3. Add the key to the environment variables on Streamlit Cloud or Railway as `POLYGON_API_KEY`.

### Alpaca
1. Create an account on [Alpaca](https://alpaca.markets/).
2. Find your API key and secret in your dashboard.
3. Add these as `ALPACA_API_KEY` and `ALPACA_SECRET_KEY`.

### Binance
1. Register on [Binance](https://www.binance.com/).
2. Go to API Management and create a new API key.
3. Enter the API key as `BINANCE_API_KEY`.

### Coinbase
1. Create a Coinbase account at [Coinbase](https://www.coinbase.com/).
2. Generate an API key in the API settings section.
3. Set the API key as `COINBASE_API_KEY`.

## Security Best Practices
- Never expose your API keys in public repositories.
- Use GitHub secrets for any sensitive information.
- Regularly rotate your API keys.
- Monitor for unauthorized access to your accounts.

## Troubleshooting
- **Common Issues**:
  - If the app fails to deploy, check the logs in your deployment platform for error messages.
  - Ensure that all dependencies are correctly listed in `requirements.txt`.
  - Verify that all environment variables and secrets are correctly set up.

## Verification Checklist
- Ensure the app is accessible after deployment.
- Check that all required API keys are correctly configured and working.
- Run several test trades or queries to ensure connectivity to trading APIs.
- Review logs for any runtime errors or warnings.

---