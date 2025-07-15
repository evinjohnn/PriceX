# Enterprise Scraping System Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the enterprise-grade web scraping system with multi-tiered anti-blocking architecture. The system includes:

- **Tier 1**: Stealth Playwright browser automation (primary)
- **Tier 2**: AWS Lambda serverless IP rotation (fallback)
- **Tier 3**: Automated CAPTCHA solving (final escalation)

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **PostgreSQL**: 12.x or higher
- **Redis**: 6.x or higher
- **AWS Account**: For Lambda deployment (optional but recommended)

### Required Accounts/Services

1. **AWS Account** (for Tier 2 functionality)
2. **2Captcha Account** (for CAPTCHA solving)
3. **Domain/Server** (for production deployment)

## Installation Steps

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Playwright Browsers

```bash
# Install Playwright browsers
playwright install chromium

# For production/Docker environments
playwright install-deps
```

### 3. Set Up Environment Variables

Create `backend/.env` with the following configuration:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/pricecompare
UPSTASH_REDIS_URL=redis://localhost:6379

# Google Gemini API (for future LLM integration)
GEMINI_API_KEY=your_gemini_api_key_here

# AWS Configuration (Tier 2 - Optional but recommended)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
AWS_LAMBDA_FUNCTION_NAME=web-scraper-function

# 2Captcha Configuration (Tier 3 - Optional)
2CAPTCHA_API_KEY=your_2captcha_api_key

# Logging Configuration
LOG_LEVEL=INFO
```

### 4. Initialize Database

```bash
cd backend
python database.py
```

## AWS Lambda Deployment (Tier 2)

### Step 1: Create Lambda Function

1. **Navigate to AWS Lambda Console**
   - Go to https://console.aws.amazon.com/lambda/
   - Click "Create function"

2. **Function Configuration**
   - **Function name**: `web-scraper-function`
   - **Runtime**: Python 3.11
   - **Architecture**: x86_64
   - **Memory**: 1024 MB (minimum for Playwright)
   - **Timeout**: 5 minutes

### Step 2: Create Lambda Layer for Playwright

Playwright requires a custom layer due to its size and dependencies.

```bash
# Create layer directory
mkdir lambda-layer
cd lambda-layer

# Create layer structure
mkdir -p python/lib/python3.11/site-packages

# Install dependencies
pip install playwright playwright-stealth -t python/lib/python3.11/site-packages

# Install browsers (for Lambda)
cd python/lib/python3.11/site-packages
playwright install chromium

# Create layer zip
zip -r playwright-layer.zip python/
```

#### Upload Layer to AWS

1. Go to AWS Lambda Console → Layers
2. Click "Create layer"
3. **Layer name**: `playwright-layer`
4. **Upload**: `playwright-layer.zip`
5. **Compatible runtimes**: Python 3.11

### Step 3: Deploy Lambda Function

```bash
# Create deployment package
cd backend
zip -r lambda-deployment.zip lambda_function.py

# Upload to AWS Lambda
aws lambda update-function-code \
  --function-name web-scraper-function \
  --zip-file fileb://lambda-deployment.zip
```

### Step 4: Configure Lambda Function

1. **Add the Playwright layer**
   - In Lambda console, go to your function
   - Scroll to "Layers" section
   - Click "Add a layer"
   - Choose "Custom layers"
   - Select `playwright-layer`

2. **Set Environment Variables**
   ```
   PLAYWRIGHT_BROWSERS_PATH=/opt/python/lib/python3.11/site-packages/playwright/driver
   ```

3. **Configure IAM Role**
   
   Create IAM role with these permissions:
   
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "logs:CreateLogGroup",
           "logs:CreateLogStream",
           "logs:PutLogEvents"
         ],
         "Resource": "arn:aws:logs:*:*:*"
       }
     ]
   }
   ```

### Step 5: Create API Gateway (Optional)

For HTTP access to Lambda:

1. **Create API Gateway**
   - Go to AWS API Gateway Console
   - Create new REST API
   - **API name**: `web-scraper-api`

2. **Create Resource and Method**
   - Create resource: `/scrape`
   - Create method: `POST`
   - **Integration type**: Lambda Function
   - **Lambda function**: `web-scraper-function`

3. **Enable CORS**
   - Select the method
   - Actions → Enable CORS
   - Configure as needed

4. **Deploy API**
   - Actions → Deploy API
   - **Stage**: `prod`
   - Note the API endpoint URL

## 2Captcha Service Setup

### Step 1: Create Account

1. Go to https://2captcha.com/
2. Create an account
3. Add funds to your account
4. Get your API key from the dashboard

### Step 2: Configure API Key

Add to your `.env` file:

```env
2CAPTCHA_API_KEY=your_api_key_here
```

### Step 3: Test CAPTCHA Service

```bash
cd backend
python -c "
from captcha_solver import captcha_solver
print('CAPTCHA configured:', captcha_solver.is_configured())
"
```

## Production Deployment

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright dependencies
RUN pip install playwright
RUN playwright install-deps
RUN playwright install chromium

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "main.py"]
```

Build and run:

```bash
docker build -t enterprise-scraper .
docker run -p 8000:8000 --env-file .env enterprise-scraper
```

### Kubernetes Deployment

Create `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: enterprise-scraper
spec:
  replicas: 3
  selector:
    matchLabels:
      app: enterprise-scraper
  template:
    metadata:
      labels:
        app: enterprise-scraper
    spec:
      containers:
      - name: scraper
        image: enterprise-scraper:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: scraper-secrets
              key: database-url
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: scraper-secrets
              key: aws-access-key
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: scraper-secrets
              key: aws-secret-key
        - name: 2CAPTCHA_API_KEY
          valueFrom:
            secretKeyRef:
              name: scraper-secrets
              key: captcha-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: enterprise-scraper-service
spec:
  selector:
    app: enterprise-scraper
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy:

```bash
kubectl apply -f deployment.yaml
```

## Configuration Options

### Scraping Configuration

Edit `backend/config.py` to adjust:

```python
# Timeouts
PAGE_LOAD_TIMEOUT = 30
ELEMENT_WAIT_TIMEOUT = 10
NAVIGATION_TIMEOUT = 30

# Retry settings
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_BASE = 2
RETRY_DELAY_MAX = 30

# Browser settings
BROWSER_HEADLESS = True
BROWSER_SLOW_MO = 0

# Rate limiting
MIN_REQUEST_DELAY = 2
MAX_REQUEST_DELAY = 8
```

### AWS Lambda Configuration

```python
# Lambda settings
LAMBDA_TIMEOUT = 60
LAMBDA_MEMORY_SIZE = 1024
```

### CAPTCHA Configuration

```python
# CAPTCHA settings
CAPTCHA_SOLVE_TIMEOUT = 120
CAPTCHA_POLL_INTERVAL = 5
```

## Monitoring and Logging

### Application Logs

```bash
# View application logs
tail -f /var/log/enterprise-scraper/app.log

# View Celery worker logs
tail -f /var/log/enterprise-scraper/celery.log
```

### AWS CloudWatch

Monitor Lambda function:

1. Go to CloudWatch Console
2. Navigate to Log Groups
3. Find `/aws/lambda/web-scraper-function`
4. Monitor execution logs and errors

### Health Checks

Create health check endpoint:

```python
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })
```

## Security Considerations

### Environment Variables

- Never commit `.env` files to version control
- Use secrets management in production
- Rotate API keys regularly

### AWS Security

- Use IAM roles with minimal permissions
- Enable VPC for Lambda functions
- Use AWS Secrets Manager for sensitive data

### Network Security

- Use HTTPS for all communications
- Implement rate limiting
- Use WAF for production APIs

## Troubleshooting

### Common Issues

1. **Playwright Browser Not Found**
   ```bash
   # Reinstall browsers
   playwright install chromium
   ```

2. **Lambda Timeout**
   ```bash
   # Increase timeout in Lambda configuration
   aws lambda update-function-configuration \
     --function-name web-scraper-function \
     --timeout 300
   ```

3. **CAPTCHA Solving Fails**
   ```bash
   # Check API key and balance
   python -c "
   from captcha_solver import captcha_solver
   print('Balance:', captcha_solver.get_balance())
   "
   ```

4. **High Memory Usage**
   ```bash
   # Monitor memory usage
   docker stats enterprise-scraper
   ```

### Performance Optimization

1. **Browser Pool Management**
   - Reuse browser contexts
   - Implement connection pooling
   - Use browser instance caching

2. **Lambda Optimization**
   - Use provisioned concurrency
   - Optimize package size
   - Implement connection keep-alive

3. **Database Optimization**
   - Use connection pooling
   - Implement query optimization
   - Use read replicas for scaling

## Scaling Considerations

### Horizontal Scaling

1. **Multiple Worker Processes**
   ```bash
   # Run multiple Celery workers
   celery -A worker.celery_app worker --concurrency=4
   ```

2. **Load Balancing**
   - Use nginx for load balancing
   - Implement health checks
   - Configure session affinity

3. **Database Scaling**
   - Use read replicas
   - Implement sharding
   - Use connection pooling

### Vertical Scaling

1. **Increase Resources**
   - More CPU cores
   - More memory
   - Faster storage

2. **Optimize Code**
   - Async/await patterns
   - Efficient data structures
   - Minimize database queries

## Maintenance

### Regular Tasks

1. **Update Dependencies**
   ```bash
   pip freeze > requirements.txt
   pip install -r requirements.txt --upgrade
   ```

2. **Clean Browser Cache**
   ```bash
   # Clear Playwright cache
   playwright cache clear
   ```

3. **Monitor API Quotas**
   - Check 2Captcha balance
   - Monitor AWS usage
   - Review scraping success rates

### Backup Strategy

1. **Database Backups**
   ```bash
   pg_dump pricecompare > backup.sql
   ```

2. **Configuration Backups**
   - Backup environment files
   - Document configuration changes
   - Version control configurations

## Support

### Getting Help

1. **Documentation**: Check this guide first
2. **Logs**: Review application and service logs
3. **Monitoring**: Check health and performance metrics
4. **Community**: Consult relevant documentation for each service

### Contact Information

- **Technical Issues**: Check logs and configuration
- **Service Issues**: Contact respective service providers
- **Performance Issues**: Review monitoring and scaling options

---

## Quick Start Checklist

- [ ] Install Python dependencies
- [ ] Install Playwright browsers
- [ ] Configure environment variables
- [ ] Set up database
- [ ] Deploy AWS Lambda (optional)
- [ ] Configure 2Captcha (optional)
- [ ] Test local deployment
- [ ] Set up monitoring
- [ ] Configure production deployment
- [ ] Test end-to-end functionality

This deployment guide provides a comprehensive overview of setting up the enterprise scraping system. Follow the steps carefully and adjust configurations based on your specific requirements.