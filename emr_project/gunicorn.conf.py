"""
Gunicorn configuration file for MediCore EMR production deployment.
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "medicore_emr"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment for HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Preload app for better performance
preload_app = True

def when_ready(server):
    """Run when the server is ready."""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Run when a worker receives SIGINT or SIGQUIT."""
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Run before forking the worker subprocess."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Run after forking the worker subprocess."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Run after initializing the worker subprocess."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Run when a worker receives SIGABRT."""
    worker.log.info("Worker aborted (pid: %s)", worker.pid)

def pre_exec(server):
    """Run before execing the worker subprocess."""
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    """Run when the server is ready."""
    server.log.info("Server is ready. Spawning workers")

def on_starting(server):
    """Run when the server is starting."""
    server.log.info("Server is starting.")

def on_reload(server):
    """Run when the server is reloading."""
    server.log.info("Server is reloading.")

def on_exit(server):
    """Run when the server is exiting."""
    server.log.info("Server is exiting.") 