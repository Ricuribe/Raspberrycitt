# Tutorial: Desplegar aplicación Flask en Raspberry Pi con Gunicorn y Nginx

## Requisitos previos
- Raspberry Pi con sistema operativo instalado
- Entorno virtual Python configurado
- Dependencias instaladas (requirements.txt)
- Aplicación Flask funcional

## 1. Crear archivos de configuración systemd

### Configuración para la aplicación Flask (Gunicorn)
```bash
sudo nano /etc/systemd/system/raspberryftp.service
```

```ini
[Unit]
Description=RaspberryFTP Flask app (Gunicorn)
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/Raspberryftp
Environment="PATH=/home/pi/Raspberryftp/venv/bin"
Environment="UPLOAD_PASSWORD=tu_contraseña_aqui"
ExecStart=/home/pi/Raspberryftp/venv/bin/gunicorn --workers 3 --bind unix:/home/pi/Raspberryftp/raspberryftp.sock app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Configuración para el monitor (feh)
```bash
sudo nano /etc/systemd/system/raspberryftp-monitor.service
```

```ini
[Unit]
Description=RaspberryFTP monitor (watch folder and feh)
After=graphical.target

[Service]
User=pi
WorkingDirectory=/home/pi/Raspberryftp
Environment="PATH=/home/pi/Raspberryftp/venv/bin"
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/pi/.Xauthority"
ExecStart=/home/pi/Raspberryftp/venv/bin/python /home/pi/Raspberryftp/monitor.py
Restart=always

[Install]
WantedBy=graphical.target
```

## 2. Configurar Nginx

### Crear archivo de configuración
```bash
sudo nano /etc/nginx/sites-available/raspberryftp
```

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://unix:/home/pi/Raspberryftp/raspberryftp.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /home/pi/Raspberryftp/static/;
    }
}
```

### Activar configuración
```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/raspberryftp /etc/nginx/sites-enabled/

# Eliminar configuración default (opcional)
sudo rm /etc/nginx/sites-enabled/default

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

## 3. Iniciar servicios

```bash
# Recargar configuraciones systemd
sudo systemctl daemon-reload

# Habilitar y arrancar servicios
sudo systemctl enable --now raspberryftp.service
sudo systemctl enable --now raspberryftp-monitor.service
```

## 4. Acceso a la aplicación

- Localmente en Raspberry Pi: http://localhost
- Desde red local: http://[IP-DE-TU-RASPBERRY]
  - Para obtener IP: `hostname -I`
  - Ejemplo: http://192.168.1.100

## Comandos útiles

### Ver logs
```bash
# Logs de la aplicación Flask
sudo journalctl -u raspberryftp.service -f

# Logs del monitor
sudo journalctl -u raspberryftp-monitor.service -f
```

### Gestión de servicios
```bash
# Reiniciar servicios
sudo systemctl restart raspberryftp.service raspberryftp-monitor.service

# Detener servicios
sudo systemctl stop raspberryftp.service raspberryftp-monitor.service

# Ver estado
sudo systemctl status raspberryftp.service
sudo systemctl status raspberryftp-monitor.service
```

## Solución de problemas

### Permisos
- Verificar que el usuario (pi) tiene permisos en la carpeta del proyecto
- Verificar permisos de escritura en static/uploads
- Verificar acceso a .Xauthority para feh

### Logs y depuración
- Revisar logs con journalctl
- Verificar que el socket de Gunicorn se crea correctamente
- Comprobar logs de Nginx: `sudo tail -f /var/log/nginx/error.log`

### Display
Si feh no muestra imágenes:
- Verificar DISPLAY está configurado correctamente
- Comprobar permisos de X11
- Verificar que el servicio inicia después de graphical.target

## Notas importantes
- Reemplazar rutas según tu instalación
- Ajustar usuario si no es 'pi'
- Configurar contraseña segura
- La aplicación solo será accesible en red local por defecto