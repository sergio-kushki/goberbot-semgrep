# EC2 Deployment Guide

Complete guide for deploying the Custom Semgrep MCP Server on AWS EC2.

## Prerequisites

- AWS Account with EC2 access
- AWS CLI installed (optional, but recommended)
- SSH key pair for EC2 access

---

## Step 1: Launch EC2 Instance

### Instance Specifications

| Setting | Recommended Value |
|---------|------------------|
| **Instance Type** | `t3.small` or `t3.medium` |
| **OS** | Amazon Linux 2023 or Ubuntu 22.04 LTS |
| **Storage** | 20 GB gp3 |
| **vCPUs** | 2 |
| **Memory** | 2-4 GB |

### Using AWS Console

1. Go to **EC2 Dashboard** → **Launch Instance**
2. Configure:
   - **Name**: `semgrep-mcp-server`
   - **AMI**: Amazon Linux 2023 or Ubuntu 22.04
   - **Instance type**: `t3.small`
   - **Key pair**: Select or create new
   - **Network**: Default VPC (or your custom VPC)
   - **Storage**: 20 GB gp3

3. **Security Group** - Create new with:
   - **SSH (22)**: Your IP address
   - **Custom TCP (8000)**: Your IP address (or VPN CIDR)

4. Click **Launch Instance**

### Using AWS CLI

```bash
# Create security group
aws ec2 create-security-group \
  --group-name semgrep-mcp-sg \
  --description "Security group for Semgrep MCP Server"

# Add rules (replace YOUR_IP with your actual IP)
aws ec2 authorize-security-group-ingress \
  --group-name semgrep-mcp-sg \
  --protocol tcp --port 22 \
  --cidr YOUR_IP/32

aws ec2 authorize-security-group-ingress \
  --group-name semgrep-mcp-sg \
  --protocol tcp --port 8000 \
  --cidr YOUR_IP/32

# Launch instance
aws ec2 run-instances \
  --image-id ami-XXXXXXXX \  # Get latest Amazon Linux 2023 AMI ID
  --instance-type t3.small \
  --key-name your-key-pair \
  --security-groups semgrep-mcp-sg \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=semgrep-mcp-server}]'
```

---

## Step 2: Connect to EC2 Instance

### Get Instance Public IP

```bash
# From AWS Console: EC2 → Instances → Select your instance → Copy Public IPv4

# Or via CLI
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=semgrep-mcp-server" \
  --query "Reservations[0].Instances[0].PublicIpAddress" \
  --output text
```

### SSH Connection

**Amazon Linux:**
```bash
ssh -i ~/.ssh/your-key.pem ec2-user@YOUR_EC2_PUBLIC_IP
```

**Ubuntu:**
```bash
ssh -i ~/.ssh/your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

---

## Step 3: Install Docker on EC2

### Amazon Linux 2023

```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install docker -y

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (no sudo needed)
sudo usermod -a -G docker ec2-user

# Apply group changes (logout and login, or run)
newgrp docker

# Verify installation
docker --version
docker ps
```

### Ubuntu 22.04

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Docker
sudo apt install docker.io docker-compose -y

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -a -G docker ubuntu
newgrp docker

# Verify installation
docker --version
docker ps
```

---

## Step 4: Deploy Semgrep MCP Server

### Option A: Clone from Repository (If using Git)

```bash
# Install git (if not already installed)
# Amazon Linux
sudo yum install git -y

# Ubuntu
sudo apt install git -y

# Clone repository
git clone https://github.com/yourorg/goberbot-semgrep.git
cd goberbot-semgrep/mcp-server
```

### Option B: Copy Files Manually

**From your local machine:**

```bash
# Create tarball of mcp-server directory
cd /Users/sergio.arancibia/CursorProjects/goberbot-semgrep
tar -czf mcp-server.tar.gz mcp-server/ custom-rules/

# Copy to EC2
scp -i ~/.ssh/your-key.pem mcp-server.tar.gz ec2-user@YOUR_EC2_IP:/home/ec2-user/

# SSH and extract
ssh -i ~/.ssh/your-key.pem ec2-user@YOUR_EC2_IP
tar -xzf mcp-server.tar.gz
cd mcp-server
```

---

## Step 5: Build and Run Container

### Basic Deployment (Bundled Rules)

```bash
cd mcp-server

# Build image
docker build -t semgrep-mcp-server -f Dockerfile ..

# Run container
docker run -d \
  --name semgrep-mcp \
  -p 8000:8000 \
  --restart unless-stopped \
  semgrep-mcp-server

# Check logs
docker logs -f semgrep-mcp
```

### Using Docker Compose (Recommended)

```bash
# Start server
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### With External Rules URL

```bash
docker run -d \
  --name semgrep-mcp \
  -p 8000:8000 \
  -e CUSTOM_RULES_URL="https://raw.githubusercontent.com/yourorg/rules/main/security.yaml" \
  --restart unless-stopped \
  semgrep-mcp-server
```

---

## Step 6: Verify Deployment

### Health Check

```bash
# From EC2 instance
curl http://localhost:8000/health

# From your local machine
curl http://YOUR_EC2_PUBLIC_IP:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "semgrep-mcp-server",
  "rules_source": "bundled:/app/custom-rules"
}
```

### Test Scan

```bash
curl -X POST http://YOUR_EC2_PUBLIC_IP:8000/mcp/v1/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "scan_code",
    "arguments": {
      "code": "eval(userInput);",
      "language": "javascript"
    }
  }'
```

---

## Step 7: Configure Cursor IDE

Add to `~/.cursor/mcp.json` on your **local machine**:

```json
{
  "mcpServers": {
    "semgrep_custom": {
      "type": "streamable-http",
      "url": "http://YOUR_EC2_PUBLIC_IP:8000"
    }
  }
}
```

**Restart Cursor IDE** to apply changes.

---

## Security Hardening (Optional but Recommended)

### 1. Use HTTPS with Nginx Reverse Proxy

```bash
# Install nginx
sudo yum install nginx -y  # Amazon Linux
# or
sudo apt install nginx -y  # Ubuntu

# Configure nginx
sudo tee /etc/nginx/conf.d/semgrep-mcp.conf > /dev/null <<EOF
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 2. Add Authentication Token

Update Docker run command:

```bash
docker run -d \
  --name semgrep-mcp \
  -p 8000:8000 \
  -e MCP_AUTH_TOKEN="your-secret-token-here" \
  semgrep-mcp-server
```

Then in Cursor config:
```json
{
  "mcpServers": {
    "semgrep_custom": {
      "type": "streamable-http",
      "url": "http://YOUR_EC2_IP:8000",
      "headers": {
        "Authorization": "Bearer your-secret-token-here"
      }
    }
  }
}
```

### 3. Use VPN or SSH Tunnel (Most Secure)

**SSH Tunnel:**
```bash
# On your local machine
ssh -i ~/.ssh/your-key.pem -L 8000:localhost:8000 ec2-user@YOUR_EC2_IP -N

# Then in Cursor, use localhost
{
  "mcpServers": {
    "semgrep_custom": {
      "type": "streamable-http",
      "url": "http://localhost:8000"
    }
  }
}
```

---

## Monitoring & Maintenance

### View Logs

```bash
# Real-time logs
docker logs -f semgrep-mcp

# Last 100 lines
docker logs --tail 100 semgrep-mcp
```

### Restart Server

```bash
docker restart semgrep-mcp

# Or with docker-compose
docker-compose restart
```

### Update Server

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Check Resource Usage

```bash
# Container stats
docker stats semgrep-mcp

# EC2 instance metrics
top
htop  # if installed
df -h  # disk usage
free -h  # memory usage
```

---

## Troubleshooting

### Issue: Cannot connect from Cursor

**Check security group:**
```bash
aws ec2 describe-security-groups \
  --group-names semgrep-mcp-sg
```

Ensure port 8000 is open to your IP.

**Test from local machine:**
```bash
telnet YOUR_EC2_IP 8000
# or
curl -v http://YOUR_EC2_IP:8000/health
```

### Issue: Container crashes

**Check logs:**
```bash
docker logs semgrep-mcp
```

**Check resource limits:**
```bash
docker stats semgrep-mcp
```

**Restart with more memory:**
```bash
docker run -d \
  --name semgrep-mcp \
  -p 8000:8000 \
  --memory="2g" \
  semgrep-mcp-server
```

### Issue: Rules not loading

**Check rules in container:**
```bash
docker exec semgrep-mcp ls -la /app/custom-rules/
docker exec semgrep-mcp cat /app/custom-rules/security.yaml
```

**Check rules source:**
```bash
curl http://YOUR_EC2_IP:8000/health | jq .rules_source
```

---

## Cost Estimation

**Monthly AWS Costs (US-East-1):**

| Resource | Specs | Cost |
|----------|-------|------|
| EC2 t3.small | 2 vCPU, 2 GB RAM | ~$15/month |
| EBS Storage | 20 GB gp3 | ~$2/month |
| Data Transfer | First 100 GB free | $0 (typical usage) |
| **Total** | | **~$17/month** |

For production with higher availability:
- **t3.medium**: ~$30/month
- **Load Balancer**: +$18/month
- **Multiple AZs**: 2x instance cost

---

## Cleanup (When Done Testing)

```bash
# Stop and remove containers
docker-compose down

# Remove images
docker rmi semgrep-mcp-server

# Terminate EC2 instance (via console or CLI)
aws ec2 terminate-instances --instance-ids i-XXXXX

# Delete security group
aws ec2 delete-security-group --group-name semgrep-mcp-sg
```

---

## Next Steps

- [ ] Set up automated backups
- [ ] Configure CloudWatch monitoring
- [ ] Add auto-scaling group (if needed)
- [ ] Implement CI/CD pipeline
- [ ] Set up SSL/TLS certificates
- [ ] Configure custom domain

---

**Questions or Issues?**  
Refer to main [README.md](README.md) or create an issue in the repository.

