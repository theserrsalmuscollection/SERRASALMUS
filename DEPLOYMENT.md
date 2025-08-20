# SERRA ORGIN Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional but recommended)
- Git

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd serra-orgin

# Run the automated installer
./install.sh

# Or with additional options
./install.sh --download-models --run-tests --docker
```

### Configuration
1. Copy `.env.example` to `.env`
2. Edit `.env` with your specific settings
3. Set up contact emails:
   - `ADMIN_EMAIL=polerbear1973@gmail.com`
   - `ORGANIZATION_EMAIL=theserralmuscollectionllc@gmail.com`

## 🐳 Docker Deployment (Recommended)

### Development
```bash
docker-compose up -d
```

### Production
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with production configuration
docker-compose -f docker-compose.prod.yml up -d
```

Access the application at:
- Web UI: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

## 🖥️ Manual Deployment

### Backend (Python)
```bash
# Activate virtual environment
source venv/bin/activate

# Start the core framework
python -m serra_orgin.main

# Or use CLI
serra start
```

### Frontend (React)
```bash
# Navigate to web UI directory
cd web_ui

# Install dependencies
npm install

# Start development server
npm run dev

# Or build for production
npm run build
npm run preview
```

## 📦 Desktop Application

### Development
```bash
cd desktop
npm install
npm run dev
```

### Build
```bash
npm run build
```

## 🌐 Browser Extension

### Development
```bash
cd extension
npm install
npm run build
```

### Installation
1. Open Chrome/Edge extension management
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `extension/dist` folder

## ☁️ Cloud Deployment

### AWS
```bash
# Deploy to AWS ECS
serra deploy --provider aws --environment production

# Or using Docker
docker build -t serra-orgin .
# Push to ECR and deploy
```

### Google Cloud
```bash
# Deploy to Google Cloud Run
serra deploy --provider gcp --environment production
```

### Azure
```bash
# Deploy to Azure Container Instances
serra deploy --provider azure --environment production
```

## 🔧 Configuration Options

### Environment Variables
```bash
# Core Settings
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
DATABASE_URL=postgresql://user:pass@localhost/serra_db

# AI Settings
USE_LOCAL_MODELS=true
DEFAULT_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=your_key_here

# Features
MAX_AGENTS=20
MCP_ENABLED_TOOLS=github,filesystem,web_search,code_execution
AUTO_DEPLOY=false
```

### UI Theme
```bash
UI_THEME=dark
WEB_UI_PORT=3000
```

## 🏗️ Architecture Overview

```
SERRA ORGIN Production Architecture
├── Load Balancer (Nginx)
├── Web UI (React + Vite)
├── API Gateway (FastAPI)
├── Core Framework (Python)
│   ├── Agent Swarm
│   ├── MCP Server
│   ├── RAG System
│   └── Web Scraper
├── Database (PostgreSQL)
├── Cache (Redis)
├── Message Queue (Redis)
└── Monitoring (Prometheus + Grafana)
```

## 🔒 Security

### Production Security Checklist
- [ ] Change default `SECRET_KEY`
- [ ] Use strong database passwords
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Enable audit logging
- [ ] Configure backup strategy

### HTTPS Setup
```bash
# Using Let's Encrypt
certbot --nginx -d your-domain.com

# Update nginx configuration
# SSL certificates will be auto-renewed
```

## 📊 Monitoring

### Health Checks
```bash
# Check system status
serra status

# View logs
serra logs --follow

# Monitor agents
serra agents --list
```

### Metrics Endpoints
- Health: `/health`
- Metrics: `/metrics`
- System Info: `/api/v1/system/info`

## 🔄 CI/CD Pipeline

### GitHub Actions (Example)
```yaml
# .github/workflows/deploy.yml
name: Deploy SERRA ORGIN
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: |
          ./install.sh --docker
          serra deploy --auto --environment production
```

### Automated Deployment
```bash
# Set up automated deployment
serra config --set auto_deploy=true
serra config --set deployment_webhook=https://your-webhook.com
```

## 🌐 Scaling

### Horizontal Scaling
```bash
# Scale agents
serra agents --create --type full_stack_developer --count 5

# Scale containers
docker-compose up --scale serra-core=3 --scale serra-scraper=2
```

### Database Scaling
```bash
# Configure read replicas
DATABASE_READ_URL=postgresql://readonly:user@replica/serra_db
```

## 📝 Maintenance

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Backup Strategy
```bash
# Automated backups
serra backup --schedule daily --retention 30d
```

### Updates
```bash
# Update SERRA ORGIN
git pull origin main
./install.sh --update

# Restart services
serra restart
```

## 🎯 Performance Tuning

### Python Optimization
```bash
# Use gunicorn for production
gunicorn -w 4 -k uvicorn.workers.UvicornWorker serra_orgin.main:app

# Configure caching
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
```

### Database Optimization
```sql
-- Create indexes
CREATE INDEX idx_memories_agent_timestamp ON memories(agent_id, timestamp);
CREATE INDEX idx_memories_type_importance ON memories(memory_type, importance);
```

## 🆘 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find and kill process
   lsof -ti:8000 | xargs kill -9
   ```

2. **Database Connection Error**
   ```bash
   # Check database status
   serra status
   # Reset database
   serra reset --database
   ```

3. **Memory Issues**
   ```bash
   # Clean up old memories
   serra cleanup --older-than 30d
   ```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
serra start
```

## 📧 Support

For support and questions:
- Primary: polerbear1973@gmail.com
- Organization: theserralmuscollectionllc@gmail.com
- Documentation: https://docs.serra-orgin.dev
- Issues: https://github.com/serra-orgin/serra-orgin/issues

## 📄 License

MIT License - Build the future freely.

---

**SERRA ORGIN** - From concept to deployment, autonomously. 🌊
