# borsaInsPla 💼
Una plataforma web de borsa de treball per l'Institut Pla de l'Estany, conectant alumnes, exalumnes i empreses de Banyoles.

---

## 🌐 Acceso en Línea
La plataforma está disponible en: **http://estanyjobs.raspberryip.com:8000/** (abans)

Dump Base de dates actual: https://drive.google.com/file/d/1FFB-8FuY7AtbTOpLZhh1sik-TuAJozXA/view?usp=drive_link

### Credenciales de Prueba
Todos los usuarios utilizan la siguiente contraseña: `97v6M2!pe<`

| Usuario | Rol | Contraseña |
|---------|-----|-----------|
| `admin` | Administrador | `97v6M2!pe<` |
| `Hicham` | Alumno DAM | `97v6M2!pe<` |
| `Pau` | Alumno ESO | `97v6M2!pe<` |
| `Adam` | Empresa | `97v6M2!pe<` |
| `Sergi` | Empresa | `97v6M2!pe<` |
| `Jordi` | No creado | `97v6M2!pe<` |

---

## 🛠️ Tecnologies Utilitzades
- **Django** - Framework web backend
- **Python** - Lenguaje principal
- **HTML5** - Estructura web
- **Tailwind CSS** - Framework CSS
- **PostgreSQL** - Base de datos (producción)
- **SQLite** - Base de datos (desarrollo)

---

## 🚀 Instalació Local

### Requisitos Previos
- Python 3.8+
- pip

### Pasos

1. **Clonar el repositorio**
```bash
git clone https://github.com/jepmasanas/borsaInsPla.git
cd borsaInsPla
```

2. **Crear entorno virtual**
```bash
 apt install python3.12-venv
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp env.example .env
```
Edita el archivo `.env` y rellena los valores necesarios, especialmente `EMAIL_HOST_PASSWORD`:

5. **Accecir base de dades**

## base de dades ###

Entrar amb: 

```bash
    sudo su
    sudo -u postgres psql
```
```bash
    \l
    \c borsainspla_db
```

i ara ja pots fer-hi consultes amb sql interatiu, del tipus select * from academy…

si vols saber els noms de les taules, pots fer-ho amb

```bash
    \dt
```

i si vols veure la descripció d’una taula concreta

```bash
 \dt nom taula
```


-- Crear el usuario

```bash
    CREATE USER borsainspla_user WITH PASSWORD '1234';
```

-- Crear la base de datos

```bash
    CREATE DATABASE borsainspla_db OWNER borsainspla_user;
```
-- Dar permisos

```bash
    GRANT ALL PRIVILEGES ON DATABASE borsainspla_db TO borsainspla_user;
```


#### 🔑 Configurar SMTP para notificaciones
**⚠️ Sin configurar el SMTP, el sistema de notificaciones no funcionará.**

1. Ve a https://myaccount.google.com/security
2. Activa la verificación en dos pasos
3. Ve a **Contraseñas de aplicaciones**
4. Selecciona "Correo" → "Otro (nombre personalizado)" → "Django"
5. Copia la contraseña de 16 caracteres
6. Pégala en `EMAIL_HOST_PASSWORD` del `.env`

5. **Migraciones**
```bash
python manage.py migrate
```

6. **Crear superusuari**
```bash
python manage.py createsuperuser
```

7. **Executar servidor**
```bash
python manage.py runserver
```
Accede a `http://localhost:8000`

---

## 🌍 Internacionalització (i18n)

borsaInsPla soporta tres idiomas:
- 🇪🇸 **Català** (idioma por defecto)
- 🇪🇸 **Español**
- 🇬🇧 **English**

### Fluxe de Trabajo para Traducciones

#### 1. Marcar templates para traducción
Este script modifica tus templates HTML para envolver textos con `{% trans %}`:
```bash
python scripts/mark_for_translation.py
```
**⚠️ Crea backups automáticos con extensión `.backup`**

#### 2. Generar archivos de traducción
Extrae todos los textos marcados y crea archivos `.po`:
```bash
python manage.py makemessages -l es -l en
```

#### 3. Traducir los archivos `.po`
Edita manualmente los archivos en `locale/*/LC_MESSAGES/django.po` o usa el script de traducción automática:
```bash
python scripts/translate_po.py
```
**Nota:** Requiere `googletrans==4.0.0-rc1` y `polib` (no incluidos en requirements.txt)

#### 4. Compilar traducciones
Convierte los archivos `.po` a formato binario `.mo`:
```bash
python manage.py compilemessages
```
