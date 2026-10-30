# Artcraft Web Deployment Automation

A lightweight, robust, and automated deployment pipeline designed for the **Artcraft** project suite running on any Linux environment (e.g., Docker-compatible NAS or servers). It automatically fetches the latest GitHub releases, unpacks and flattens them, switches active versions using atomic relative symlinks, and maintains a rolling history with automatic cleanup.

## Architecture & Features

- **Designed for Artcraft:** Tailored to automatically manage and synchronize multiple Artcraft web applications effortlessly.
- **Containerized Execution:** Runs inside a transient `python:3` Docker container to keep the host system clean and independent.
- **Atomic Symlink Switching:** Zero downtime and instant manual rollbacks by using relative symbolic links.
- **Smart Archive Flattening:** Automatically handles GitHub's wrapper directory structure during extraction.
- **Disk Space Management:** Automatically retains only the latest 3 releases per project.
- **DRY Configuration:** Centralized settings with a clean list of repository names.

---

## Files Overview

1. **`deploy.py`**  
   The core Python script that queries the GitHub API, downloads the correct web assets (`*-web-*.zip`), extracts them into structured release folders, updates the symlink, and cleans up old versions.

2. **`dockerCallArtcraftDeploy.sh`**  
   A clean shell wrapper script that mounts the required volumes and triggers the containerized Python deployment.

---

## Setup & Usage

### 1. Directory Structure
Ensure your web root and container script paths are set up:
- Script location: `/path/to/container/artcraft/deploy.py`
- Wrapper script: `/path/to/container/artcraft/dockerCallArtcraftDeploy.sh`
- Web root / Symlinks: `/path/to/webroot/`

### 2. Cronjob Setup
Add a nightly execution (e.g., every day at 3:00 AM) to your system crontab:
```cron
0 3 * * * /path/to/container/artcraft/dockerCallArtcraftDeploy.sh >> /path/to/container/artcraft/deploy.log 2>&1

### 3. Adding New Projects
PROJECT_REPOS = [
    "vectorcraft",
    "cadcraft",
    "your-new-artcraft-project",
]
