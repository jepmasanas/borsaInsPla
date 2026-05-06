# Guia de Desplegament amb Gunicorn i Systemd

## 1. Instal·lació de Gunicorn

```bash
# Activar l'entorn virtual
source venv/bin/activate

# Instal·lar Gunicorn
pip install gunicorn

# Actualitzar requirements.txt
pip freeze > requirements.txt
```

## 2. Crear directori de logs

```bash
mkdir -p /home/server/borsaInsPla/logs
```

## 3. Configurar el servei systemd

```bash
# Copiar el fitxer de servei a systemd
sudo cp borsaInsPla.service /etc/systemd/system/

# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar el servei per iniciar automàticament
sudo systemctl enable borsaInsPla

# Iniciar el servei
sudo systemctl start borsaInsPla
```

## 4. Comandes útils

### Gestió del servei

```bash
# Iniciar el servei
sudo systemctl start borsaInsPla

# Aturar el servei
sudo systemctl stop borsaInsPla

# Reiniciar el servei
sudo systemctl restart borsaInsPla

# Veure l'estat del servei
sudo systemctl status borsaInsPla

# Veure els logs en temps real
sudo journalctl -u borsaInsPla -f

# Veure els últims logs
sudo journalctl -u borsaInsPla -n 100
```

### Logs de Gunicorn

```bash
# Veure logs d'accés
tail -f /home/server/borsaInsPla/logs/gunicorn_access.log

# Veure logs d'errors
tail -f /home/server/borsaInsPla/logs/gunicorn_error.log
```

## 5. Després de fer canvis al codi

```bash
# Fer pull dels canvis
git pull

# Aplicar migracions (si n'hi ha)
python manage.py migrate

# Col·lectar fitxers estàtics (si han canviat)
python manage.py collectstatic --noinput

# Reiniciar el servei
sudo systemctl restart borsaInsPla
```

## 6. Configurar Nginx (recomanat per producció)

Si vols utilitzar Nginx com a proxy invers davant de Gunicorn:

```bash
# Instal·lar Nginx
sudo apt install nginx

# Crear configuració de Nginx
sudo nano /etc/nginx/sites-available/borsaInsPla
```

Contingut del fitxer:

```nginx
server {
    listen 80;
    server_name el_teu_domini.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/server/borsaInsPla/staticfiles/;
    }
    
    location /media/ {
        alias /home/server/borsaInsPla/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Activar la configuració
sudo ln -s /etc/nginx/sites-available/borsaInsPla /etc/nginx/sites-enabled/

# Verificar la configuració
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

## 7. Ajustaments al settings.py per producció

Assegura't que tens aquestes configuracions:

```python
# DEBUG ha de ser False en producció
DEBUG = False

# ALLOWED_HOSTS amb el teu domini
ALLOWED_HOSTS = ['el_teu_domini.com', 'www.el_teu_domini.com', 'IP_DEL_SERVIDOR']

# Configuració de fitxers estàtics
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

## 8. SSL/HTTPS amb Let's Encrypt (recomanat)

```bash
# Instal·lar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir certificat SSL
sudo certbot --nginx -d el_teu_domini.com -d www.el_teu_domini.com

# Renovació automàtica (Certbot la configura automàticament)
sudo certbot renew --dry-run
```

## Troubleshooting

### El servei no arranca

```bash
# Veure errors detallats
sudo journalctl -u borsaInsPla -n 50

# Verificar permisos
ls -la /home/server/borsaInsPla

# Verificar que l'entorn virtual existeix
ls -la /home/server/borsaInsPla/venv
```

### Port ja en ús

```bash
# Trobar què utilitza el port 8000
sudo lsof -i :8000

# Matar el procés si cal
sudo kill -9 <PID>
```

### Problemes de permisos amb logs

```bash
# Ajustar permisos del directori de logs
sudo chown -R server:server /home/server/borsaInsPla/logs
chmod -R 755 /home/server/borsaInsPla/logs
```
