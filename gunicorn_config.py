# Configuració de Gunicorn per a borsaInsPla

# Adreça i port
bind = "0.0.0.0:8000"

# Nombre de workers (recomanat: 2-4 x nombre de CPUs)
workers = 4

# Tipus de workers
worker_class = "sync"

# Timeout (segons)
timeout = 120

# Mantenir connexions keep-alive
keepalive = 5

# Logs
accesslog = "/home/server/borsaInsPla/logs/gunicorn_access.log"
errorlog = "/home/server/borsaInsPla/logs/gunicorn_error.log"
loglevel = "info"

# Reload automàtic en desenvolupament (desactivar en producció)
# reload = True

# Nom del procés
proc_name = "borsaInsPla"

# Directori de treball
chdir = "/home/server/borsaInsPla"

# Daemon mode (systemd ho gestiona, així que False)
daemon = False

# User i group (ajusta segons el teu usuari)
# user = "server"
# group = "server"
