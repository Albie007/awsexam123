"""
Gunicorn configuration for TaskFlow on EC2.
Run: gunicorn -c gunicorn.conf.py awsproject.wsgi:application
"""

import multiprocessing

# ── Binding ──────────────────────────────────────────────────
# Use Unix socket for Nginx integration (faster than TCP)
bind    = "unix:/run/taskflow/gunicorn.sock"
backlog = 2048

# ── Workers ──────────────────────────────────────────────────
# Rule of thumb: (2 × CPU cores) + 1
workers    = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"       # use 'gevent' if you install it
threads    = 2
timeout    = 60             # kill worker after 60s of silence
keepalive  = 5

# ── Logging ──────────────────────────────────────────────────
accesslog  = "/var/log/taskflow/access.log"
errorlog   = "/var/log/taskflow/error.log"
loglevel   = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)ss'

# ── Process naming ───────────────────────────────────────────
proc_name = "taskflow_gunicorn"

# ── Security ─────────────────────────────────────────────────
limit_request_line   = 4096
limit_request_fields = 100

# ── Hooks ────────────────────────────────────────────────────
def on_starting(server):
    server.log.info("TaskFlow Gunicorn starting...")

def worker_exit(server, worker):
    server.log.info(f"Worker {worker.pid} exited.")
