# SentientEcho Troubleshooting Guide 🔧

**Complete troubleshooting guide for SentientEcho deployment, configuration, and usage issues.**

## 🚨 **Quick Diagnosis**

### **Is SentientEcho Working?**
Run these quick checks:

```bash
# 1. Health Check
curl http://localhost:8000/health

# 2. Basic Query Test
curl -X POST http://localhost:8000/assist \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "query": "test query"}'

# 3. Check Logs
docker-compose logs sentientecho
```

**Expected Results**:
- Health check returns `{"status": "healthy"}`
- Query returns SSE stream with events
- Logs show no ERROR messages

## 🔍 **Common Issues & Solutions**

### **1. Deployment Issues**

#### **❌ "Container won't start"**
**Symptoms**: Docker container exits immediately
**Causes**: Missing environment variables, port conflicts

**Solutions**:
```bash
# Check environment variables
cat .env

# Verify required variables exist:
# FIREWORKS_API_KEY=your_key
# SERPER_API_KEY=your_key
# JINA_AI_API_KEY=your_key

# Check port availability
netstat -an | grep 8000

# If port is busy, change in docker-compose.yml:
# ports:
#   - "8001:8000"  # Use different external port
```

#### **❌ "Permission denied errors"**
**Symptoms**: Docker build fails with permission errors
**Solutions**:
```bash
# On Windows, run as administrator
# On Linux/Mac, check Docker permissions
sudo usermod -aG docker $USER
# Then logout and login again

# Alternative: Use sudo
sudo docker-compose up -d
```

#### **❌ "Build context too large"**
**Symptoms**: Docker build is very slow or fails
**Solutions**:
```bash
# Check .dockerignore exists and contains:
echo "__pycache__
*.pyc
.git
.env
tests/
*.md" > .dockerignore

# Clean Docker cache
docker system prune -f
```

### **2. API Key Issues**

#### **❌ "Invalid API key for Fireworks"**
**Symptoms**: 401 Unauthorized errors in logs
**Solutions**:
```bash
# 1. Verify API key format
echo $FIREWORKS_API_KEY
# Should start with "fw_" and be ~40 characters

# 2. Test API key directly
curl -H "Authorization: Bearer $FIREWORKS_API_KEY" \
  https://api.fireworks.ai/inference/v1/models

# 3. Check environment loading
python -c "import os; print(os.getenv('FIREWORKS_API_KEY'))"

# 4. Regenerate key if needed
# Go to https://fireworks.ai/account/api-keys
```

#### **❌ "Serper API quota exceeded"**
**Symptoms**: 429 Too Many Requests errors
**Solutions**:
```bash
# Check quota usage
curl -H "X-API-KEY: $SERPER_API_KEY" \
  https://google.serper.dev/account

# Solutions:
# 1. Wait for quota reset (usually monthly)
# 2. Upgrade Serper plan
# 3. Use fallback Twitter provider (snscrape)
```

#### **❌ "Jina AI authentication failed"**
**Symptoms**: Embedding requests fail
**Solutions**:
```bash
# Test Jina API key
curl -H "Authorization: Bearer $JINA_AI_API_KEY" \
  https://api.jina.ai/v1/embeddings

# If invalid, get new key from:
# https://jina.ai/embeddings/
```

### **3. Performance Issues**

#### **❌ "Responses are very slow (>30 seconds)"**
**Symptoms**: Queries take longer than expected
**Diagnosis**:
```bash
# Check component health
curl http://localhost:8000/health?detailed=true

# Check logs for timeouts
docker-compose logs | grep -i timeout
```

**Solutions**:
```bash
# 1. Increase timeouts in .env
echo "REQUEST_TIMEOUT=30
AI_TIMEOUT=20
CACHE_TTL_SECONDS=600" >> .env

# 2. Enable more aggressive caching
echo "ENABLE_AGGRESSIVE_CACHING=true" >> .env

# 3. Reduce content limits
echo "MAX_REDDIT_POSTS=5
MAX_TWITTER_POSTS=5" >> .env

# 4. Restart with new config
docker-compose restart
```

#### **❌ "High memory usage"**
**Symptoms**: Container uses >1GB RAM
**Solutions**:
```bash
# 1. Reduce cache size
echo "CACHE_MAX_SIZE=100
CACHE_TTL_SECONDS=300" >> .env

# 2. Limit concurrent requests
echo "MAX_CONCURRENT_REQUESTS=5" >> .env

# 3. Monitor memory usage
docker stats sentientecho
```

#### **❌ "Cache not working"**
**Symptoms**: Same queries always take full time
**Diagnosis**:
```bash
# Check cache metrics
curl http://localhost:8000/metrics | grep cache

# Should show cache_hits > 0 for repeated queries
```

**Solutions**:
```bash
# 1. Verify cache is enabled
echo "ENABLE_CACHING=true" >> .env

# 2. Check cache TTL
echo "CACHE_TTL_SECONDS=300" >> .env

# 3. Clear and restart cache
docker-compose restart
```

### **4. Content Quality Issues**

#### **❌ "No relevant content found"**
**Symptoms**: Queries return empty or irrelevant results
**Solutions**:
```bash
# 1. Check if APIs are working
curl http://localhost:8000/health

# 2. Try broader keywords
# Instead of: "iPhone 15 Pro Max camera quality"
# Try: "iPhone 15 camera" or "iPhone camera"

# 3. Check search parameters
# Verify time ranges and filters in logs
```

#### **❌ "Content seems outdated"**
**Symptoms**: Results are from months ago
**Solutions**:
```bash
# 1. Adjust time ranges in .env
echo "REDDIT_TIME_RANGE=week
TWITTER_TIME_RANGE=week" >> .env

# 2. Clear cache for fresh results
curl -X POST http://localhost:8000/admin/clear-cache

# 3. Check if topic is actively discussed
# Some topics may not have recent content
```

#### **❌ "AI summaries are poor quality"**
**Symptoms**: Summaries don't match content
**Solutions**:
```bash
# 1. Check AI provider health
curl http://localhost:8000/health | grep ai_provider

# 2. Verify model configuration
echo "FIREWORKS_MODEL_ID=accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new" >> .env

# 3. Adjust AI parameters
echo "AI_TEMPERATURE=0.3
AI_MAX_TOKENS=500" >> .env
```

### **5. Network & Connectivity Issues**

#### **❌ "Connection timeouts"**
**Symptoms**: Requests fail with timeout errors
**Solutions**:
```bash
# 1. Check internet connectivity
ping google.com
ping api.fireworks.ai

# 2. Check firewall/proxy settings
# Ensure outbound HTTPS (443) is allowed

# 3. Increase timeout values
echo "REQUEST_TIMEOUT=30
CONNECTION_TIMEOUT=10" >> .env

# 4. Test direct API access
curl -v https://api.fireworks.ai/inference/v1/models
```

#### **❌ "SSL certificate errors"**
**Symptoms**: SSL verification failures
**Solutions**:
```bash
# 1. Update certificates (Linux)
sudo apt-get update && sudo apt-get install ca-certificates

# 2. For development only (NOT production):
echo "VERIFY_SSL=false" >> .env

# 3. Check system time
date
# Ensure system time is correct
```

### **6. Rate Limiting Issues**

#### **❌ "Rate limit exceeded"**
**Symptoms**: 429 errors, requests blocked
**Solutions**:
```bash
# 1. Check current rate limits
curl http://localhost:8000/metrics | grep rate_limit

# 2. Adjust rate limits in .env
echo "RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_BURST=10" >> .env

# 3. Implement request queuing
echo "ENABLE_REQUEST_QUEUE=true
MAX_QUEUE_SIZE=50" >> .env

# 4. For development, disable rate limiting
echo "ENABLE_RATE_LIMITING=false" >> .env
```

## 🔍 **Diagnostic Commands**

### **Health Diagnostics**
```bash
# Comprehensive health check
curl "http://localhost:8000/health?detailed=true&include_metrics=true"

# Component-specific checks
curl http://localhost:8000/health | jq '.components'

# Performance metrics
curl http://localhost:8000/metrics
```

### **Log Analysis**
```bash
# View recent logs
docker-compose logs --tail=100 sentientecho

# Follow logs in real-time
docker-compose logs -f sentientecho

# Search for errors
docker-compose logs sentientecho | grep -i error

# Search for specific issues
docker-compose logs sentientecho | grep -i "timeout\|failed\|error"
```

### **Configuration Verification**
```bash
# Check environment variables
docker-compose exec sentientecho env | grep -E "(FIREWORKS|SERPER|JINA)"

# Verify configuration loading
docker-compose exec sentientecho python -c "
from src.config import validate_config
validate_config()
print('Configuration valid!')
"

# Test basic functionality
python test_agent_simple.py
```

## 🚨 **Emergency Procedures**

### **Complete Reset**
If everything is broken:
```bash
# 1. Stop all containers
docker-compose down

# 2. Remove containers and volumes
docker-compose down -v

# 3. Clean Docker cache
docker system prune -f

# 4. Rebuild from scratch
docker-compose build --no-cache

# 5. Start fresh
docker-compose up -d

# 6. Verify health
curl http://localhost:8000/health
```

### **Rollback to Previous Version**
```bash
# 1. Check git history
git log --oneline -10

# 2. Rollback to previous commit
git checkout HEAD~1

# 3. Rebuild and deploy
docker-compose build
docker-compose up -d
```

### **Debug Mode**
```bash
# 1. Enable debug logging
echo "LOG_LEVEL=DEBUG" >> .env

# 2. Restart with debug
docker-compose restart

# 3. Monitor debug logs
docker-compose logs -f sentientecho | grep DEBUG
```

## 📞 **Getting Help**

### **Self-Diagnosis Checklist**
Before seeking help, verify:
- [ ] All API keys are valid and properly set
- [ ] Health endpoint returns "healthy"
- [ ] No ERROR messages in logs
- [ ] Internet connectivity is working
- [ ] Docker has sufficient resources (2GB+ RAM)
- [ ] Ports are not blocked by firewall

### **Information to Collect**
When reporting issues, include:
1. **Error Messages**: Exact error text from logs
2. **Configuration**: Sanitized .env file (remove API keys)
3. **Environment**: OS, Docker version, available resources
4. **Steps to Reproduce**: Exact commands that cause the issue
5. **Expected vs Actual**: What should happen vs what happens

### **Log Collection**
```bash
# Collect comprehensive logs
docker-compose logs sentientecho > sentientecho-logs.txt

# Collect system info
docker info > docker-info.txt
docker-compose version > compose-version.txt

# Collect health status
curl http://localhost:8000/health > health-status.json
curl http://localhost:8000/metrics > metrics.json
```

### **Support Channels**
- **GitHub Issues**: https://github.com/Panchu11/sentientecho/issues
- **Documentation**: Check all .md files in the repository
- **Community**: SentientChat Discord/forums

---

**Most issues can be resolved by checking API keys, restarting containers, and reviewing logs. When in doubt, try the complete reset procedure!** 🔧
