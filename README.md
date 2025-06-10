---
title: Intent Oracle
emoji: ✨🔮
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "5.33.1"
app_file: app.py
pinned: false
---

# New Project

*Automatically synced with your [v0.dev](https://v0.dev) deployments*

[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com/bachinskis-projects/v0-new-project-rzgelhjki8i)
[![Built with v0](https://img.shields.io/badge/Built%20with-v0.dev-black?style=for-the-badge)](https://v0.dev/chat/projects/RzGElHJKI8i)

## Overview

This repository will stay in sync with your deployed chats on [v0.dev](https://v0.dev).
Any changes you make to your deployed app will be automatically pushed to this repository from [v0.dev](https://v0.dev).

## Deployment

Your project is live at:

**[https://vercel.com/bachinskis-projects/v0-new-project-rzgelhjki8i](https://vercel.com/bachinskis-projects/v0-new-project-rzgelhjki8i)**

## Build your app

Continue building your app on:

**[https://v0.dev/chat/projects/RzGElHJKI8i](https://v0.dev/chat/projects/RzGElHJKI8i)**

## How It Works

1. Create and modify your project using [v0.dev](https://v0.dev)
2. Deploy your chats from the v0 interface
3. Changes are automatically pushed to this repository
4. Vercel deploys the latest version from this repository

## Running with Gradio

This application can also be run locally using a Gradio interface.

**Prerequisites:**
- Python 3.8+
- pip

**Setup:**

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    Make sure you are in the root directory of the project where `requirements.txt` is located.
    ```bash
    pip install -r requirements.txt
    ```
    This will install Gradio along with other necessary packages like Flask, NumPy, etc.

**Running the Gradio App:**

1.  **Ensure the data artifact `oracle_ocean.npz` is present in the `data/` directory.**
    This file is crucial for the oracle to function.

2.  **Run the `app.py` script:**
    ```bash
    python app.py
    ```

3.  **Open your browser:**
    Gradio will typically print a local URL (e.g., `http://127.0.0.1:7860` or `http://0.0.0.0:7860`). Open this URL in your web browser to interact with the application.

This will start a local web server hosting the Gradio interface, allowing you to input your "intent" and receive the "crystal" from the oracle.