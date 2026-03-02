# crab-spyd3r-bot

<img width="736" height="624" alt="crab-spyd3r" src="https://github.com/user-attachments/assets/0f5a2a42-3746-48c1-aacc-360dcb00364f" />


Crab-Spyder-Bot is a powerful automation tool that seamlessly integrates Nmap and Metasploit commands with popular messaging platforms. 
Users can execute sophisticated network scans and penetration tests directly through Telegram, Discord, or WhatsApp. 
The bot simplifies complex security operations by translating simple chat commands into precise Nmap enumeration or Metasploit exploitation frameworks. 
Whether conducting quick port scans or launching Metasploit modules, security professionals can manage reconnaissance and vulnerability assessment remotely. 
This innovative solution bridges the gap between command-line interfaces and instant messaging, making security testing more accessible and efficient. 
Perfect for cybersecurity experts seeking convenience without compromising on powerful scanning and exploitation capabilities.

Or using wget:

``` bash
wget -qO- https://raw.githubusercontent.com/iank/crab-spyd3r-bot/main/install.sh | bash
```
# 📥 Manual Installation

Clone Repository
```bash
clone git https://github.com/Iankulani/crab-spyd3r-bot.git 
cd crab-spyd3r-bot
```
# 2. System Dependencies
Ubuntu/Debian/Kali
bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
```bash
sudo apt install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    git \
    curl \
    wget \
    nmap \
    netcat-openbsd \
    tcpdump \
    iputils-ping \
    traceroute \
    dnsutils \
    whois \
    sqlite3 \
    redis-server \
    postgresql \
    nginx \
    docker.io \
    docker-compose \
    chromium-browser \
    chromium-chromedriver \
    libssl-dev \
    libffi-dev \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev
```
# Install Metasploit (optional but recommended)
```bash
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod 755 msfinstall
./msfinstall
```
macOS
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
# Install packages
```bash
brew install \
    python3 \
    git \
    nmap \
    netcat \
    tcpdump \
    sqlite3 \
    redis \
    postgresql \
    nginx \
    docker \
    docker-compose \
    chromedriver \
    chromium
```

# Install Metasploit
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod 755 msfinstall
./msfinstall
Windows (WSL2)
powershell
# In PowerShell as Administrator
```bash
wsl --install -d Ubuntu
```
# Then follow Ubuntu instructions inside WSL
3. Python Environment
bash
# Create virtual environment
```bash
python3 -m venv venv
```
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Python dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
```bash
pip install -r requirements-dev.txt
```
# Create configuration directory

# 4. Configuration
```bash

mkdir -p ~/.crabbot/{config,data,logs,payloads,workspaces,scans,sessions}
```
# Copy example configuration
cp config.example.yaml ~/.crabbot/config/config.yaml

# Edit configuration
nano ~/.crabbot/config/config.yaml
5. Database Setup
```bash
# Initialize SQLite database

python3 -c "
from crab_spyd3r_bot import DatabaseManager
db = DatabaseManager()
db.init_tables()
print('✅ Database initialized')
"
```
# Or use PostgreSQL
sudo -u postgres psql
CREATE DATABASE crabdb;
CREATE USER crabuser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE crabdb TO crabuser;
\q
🐳 Docker Installation
Using Docker Compose (Recommended)
bash
# Clone repository
```bash
https://github.com/Iankulani/crab-spyd3r-bot.git
cd crab-spyd3r-bot
```
# Create environment file
```bash
cp .env.example .env
nano .env  # Edit with your settings
```

# Build and start all services
```bash
docker-compose up -d
```
# View logs
```bash
docker-compose logs -f
```
# Stop services
docker-compose down
Using Docker Only
bash
# Build image
docker build -t crab-spyd3r-bot .

# Run container
docker run -d \
  --name crab-bot \
  -p 5000:5000 \
  -p 8080:8080 \
  -p 8443:8443 \
  -v $(pwd)/config:/app/.crabbot/config \
  -v $(pwd)/data:/app/.crabbot/data \
  -v $(pwd)/logs:/app/.crabbot/logs \
  --cap-add=NET_ADMIN \
  --cap-add=NET_RAW \
  crab-spyd3r-bot

# Run with specific mode
```bash
docker run -it --rm crab-spyd3r-bot web  # Web interface
docker run -it --rm crab-spyd3r-bot api   # API server
docker run -it --rm crab-spyd3r-bot cli   # CLI mode
```
# 🔧 Platform-Specific Setup
Discord Bot Setup
```bash
Go to https://discord.com/developers/applications

Click "New Application" and name it "Crab-Spyd3r-Bot"

Go to "Bot" section and click "Add Bot"

Copy the bot token

# Enable these Privileged Gateway Intents:

✅ MESSAGE CONTENT INTENT

✅ SERVER MEMBERS INTENT

Add to config.yaml:
```
yaml
discord:
  token: "YOUR_BOT_TOKEN_HERE"
  enabled: true
Telegram Bot Setup
Message @BotFather on Telegram

Send /newbot and follow instructions

Copy the bot token

Get API ID and Hash from https://my.telegram.org

Add to config.yaml:

```bash
yaml
telegram:

  api_id: "YOUR_API_ID"
  api_hash: "YOUR_API_HASH"
  bot_token: "YOUR_BOT_TOKEN"
  enabled: true
```
# WhatsApp Bot Setup
```bash
# Install Chrome/Chromium
# Selenium will handle webdriver automatically
```
# Configure in config.yaml
whatsapp:
  enabled: true
  headless: false  # Set true for server environments
  qr_timeout: 60
Slack Bot Setup
Go to https://api.slack.com/apps

Click "Create New App"

Add Bot Token Scopes:

chat:write

commands

app_mentions:read

Install app to workspace

Add to config.yaml:

yaml
slack:
  bot_token: "xoxb-YOUR-TOKEN"
  app_token: "xapp-YOUR-TOKEN"  # For socket mode
  enabled: true
Signal Bot Setup
bash
# Install signal-cli
wget https://github.com/AsamK/signal-cli/releases/latest/download/signal-cli-*.tar.gz
tar xf signal-cli-*.tar.gz
sudo cp signal-cli-*/bin/signal-cli /usr/local/bin/

# Register phone number
signal-cli -u +1234567890 register

# Verify with code
signal-cli -u +1234567890 verify CODE

# Add to config.yaml
signal:
  phone_number: "+1234567890"
  enabled: true
🔒 Security Configuration
Generate SSL Certificates (for HTTPS)
bash
# Self-signed certificate
openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem \
  -out cert.pem \
  -days 365 \
  -nodes

# Or use Let's Encrypt
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com
Configure Firewall
bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 5000/tcp    # Web UI
sudo ufw allow 8080/tcp    # API
sudo ufw allow 8443/tcp    # HTTPS
sudo ufw allow 4444/tcp    # Metasploit
sudo ufw enable

# FirewallD (RHEL/CentOS)
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=8443/tcp
sudo firewall-cmd --reload
🧪 Testing Installation
bash
# Test Python environment
python3 -c "import sys; print(f'Python {sys.version}')"

# Test dependencies
python3 -c "
import discord, telethon, selenium, slack_sdk
print('✅ All imports successful')
"

# Test database
python3 -c "
from crab_spyd3r_bot import DatabaseManager
db = DatabaseManager()
print('✅ Database connection successful')
"

# Test nmap
nmap --version

# Test Metasploit
msfconsole --version

# Run the bot in test mode
python3 crab-spyd3r-bot.py --test
🚦 Running the Bot
Production Mode (Systemd)
Create service file /etc/systemd/system/crab-bot.service:

ini
[Unit]
Description=Crab-Spyd3r-Bot
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=crabuser
WorkingDirectory=/opt/crab-spyd3r-bot
Environment="PATH=/opt/crab-spyd3r-bot/venv/bin"
ExecStart=/opt/crab-spyd3r-bot/venv/bin/python crab-spyd3r-bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
Enable and start:

bash
sudo systemctl daemon-reload
sudo systemctl enable crab-bot
sudo systemctl start crab-bot
sudo systemctl status crab-bot
Development Mode
bash
# Run with auto-reload
python3 crab-spyd3r-bot.py --debug

# Run specific platforms
python3 crab-spyd3r-bot.py --platform discord,telegram

# Run web interface
python3 crab-spyd3r-bot.py --web --port 5000

# Run API server
python3 crab-spyd3r-bot.py --api --port 8080
Screen/Tmux (for long-running sessions)
bash
# Using tmux
tmux new -s crab
python3 crab-spyd3r-bot.py
# Detach: Ctrl+B, D
# Reattach: tmux attach -t crab

# Using screen
screen -S crab
python3 crab-spyd3r-bot.py
# Detach: Ctrl+A, D
# Reattach: screen -r crab
📊 Monitoring & Logs
Access Logs
bash
# View logs
tail -f ~/.crabbot/logs/crabbot.log

# Docker logs
docker-compose logs -f crab-bot

# Journal logs (systemd)
sudo journalctl -u crab-bot -f
Metrics Dashboard
Access Grafana at http://localhost:3000 (admin/admin)

Prometheus metrics at http://localhost:9090

Elasticsearch at http://localhost:9200

Kibana at http://localhost:5601

🔄 Updates
bash
# Update via git
git pull
pip install -r requirements.txt --upgrade

# Update Docker
docker-compose pull
docker-compose up -d

# Update system packages
sudo apt update && sudo apt upgrade -y
🐛 Troubleshooting
Common Issues
"Module not found"

bash
pip install -r requirements.txt --force-reinstall
Permission denied

bash
sudo chown -R $USER:$USER ~/.crabbot/
Port already in use

bash
sudo lsof -i :5000
sudo kill -9 <PID>
Docker connection refused

bash
# Check if Docker is running
sudo systemctl status docker
# Restart Docker
sudo systemctl restart docker
Nmap not found

bash
sudo apt install nmap  # Linux
brew install nmap      # macOS
📚 Additional Resources
Documentation: https://docs.crab-spyd3r-bot.com

GitHub: https://github.com/iank/crab-spyd3r-bot

Discord Support: https://discord.gg/crabspyd3r

API Reference: https://api.crab-spyd3r-bot.com/docs

✅ Verification Checklist
Python 3.7+ installed

All dependencies installed

Database initialized

Configuration file created

Discord bot token configured (optional)

Telegram API credentials configured (optional)

WhatsApp Selenium setup (optional)

Slack tokens configured (optional)

Signal phone number registered (optional)

Firewall rules applied

SSL certificates generated (for HTTPS)

Systemd service created (production)

Backup strategy implemented

🎉 Installation Complete!
Your Crab-Spyd3r-Bot is now ready to use!

Type !help in any connected platform to see available commands

Visit http://localhost:5000 for the web interface

Check logs at ~/.crabbot/logs/crabbot.log

For support, join our Discord server or open an issue on GitHub.

Happy Hacking! 🦀

