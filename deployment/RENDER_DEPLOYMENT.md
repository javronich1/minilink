# Render Deployment Configuration

**Service Type:** Web Service  
**Source:** GitHub → main branch  
**Runtime:** Docker (uses Dockerfile in repository root)  
**Region:** Global  
**Auto-Deploy:** Enabled (only on main branch updates)  

**Environment Variables:**
- `SESSION_SECRET` — required for session middleware
- `ENV=production`

**Build Process:**  
Render automatically detects and uses the repository’s Dockerfile.

**Start Command:**  
Automatically handled by `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]` in Dockerfile.