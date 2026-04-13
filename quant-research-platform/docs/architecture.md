# Architecture

Single VM deployment with Docker Compose:
- Nginx reverse proxy
- agent-api (FastAPI)
- worker (RQ/Celery-ready skeleton)
- dashboard
- quantengine-bridge
- Postgres + Redis

Scale-out path:
1. split worker to separate VM
2. isolate DB/control-plane
3. optional GPU VM for embedding/fine-tuning
