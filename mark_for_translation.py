"""
Script para marcar automáticamente textos en templates de Django para traducción
Uso: python mark_for_translation.py
"""

import os
import re
from pathlib import Path

# Configuración
TEMPLATES_DIR = Path('templates/core')
BACKUP_SUFFIX = '.backup'

# Patrones de texto a traducir
PATTERNS = [
    # Textos entre > y < en HTML
    (r'>([^<>{%]+)<', r'>{% trans "\1" %}<'),
    # Atributos title, placeholder, alt
    (r'(title|placeholder|alt)="([^"]+)"', r'\1="{% trans "\2" %}"'),
    # value en inputs (cuidado con esto, puede romper cosas)
    # (r'value="([^"]+)"', r'value="{% trans "\1" %}"'),
]

# Patrones a IGNORAR (no traducir)
IGNORE_PATTERNS = [
    r'^\s*$',  # Líneas vacías
    r'^[\d\s\.,]+$',  # Solo números y puntuación
    r'^[{%#]',  # Ya es código Django
    r'^\s*</?\w+',  # Tags HTML solos
    r'url\s+',  # URLs de Django
    r'static\s+',  # Static files
    r'^\w+\.\w+',  # Variables con punto (user.username)
    r'^[A-Z_]+$',  # Variables en mayúsculas
]


def should_ignore(text):
    """Verifica si un texto debe ser ignorado"""
    text = text.strip()

    if not text:
        return True

    for pattern in IGNORE_PATTERNS:
        if re.match(pattern, text):
            return True

    return False


def add_load_i18n(content):
    """Añade {% load i18n %} al principio si no existe"""
    if '{% load i18n %}' not in content:
        # Buscar después de {% extends %}
        extends_match = re.search(r'({%\s*extends\s+[^%]+%})', content)
        if extends_match:
            insert_pos = extends_match.end()
            content = (content[:insert_pos] +
                       '\n{% load i18n %}' +
                       content[insert_pos:])
        else:
            # Si no hay extends, añadir al principio
            content = '{% load i18n %}\n' + content

    return content


def mark_text_for_translation(content):
    """Marca textos en el contenido para traducción"""
    lines = content.split('\n')
    modified_lines = []

    for line in lines:
        original_line = line

        # Buscar textos entre > y <
        matches = re.finditer(r'>([^<>{%]+)<', line)
        replacements = []

        for match in matches:
            text = match.group(1).strip()

            # Ignorar si ya está traducido o debe ignorarse
            if '{% trans' in text or should_ignore(text):
                continue

            # Guardar reemplazo
            replacements.append((match.group(0), f'>{{% trans "{text}" %}}<'))

        # Aplicar reemplazos
        for old, new in replacements:
            line = line.replace(old, new, 1)

        # Marcar atributos (title, placeholder, alt)
        for attr in ['title', 'placeholder', 'alt']:
            # Buscar atributo="texto" que NO esté ya dentro de {% trans %}
            pattern = f'{attr}="([^"{{%]+)"'
            matches = re.finditer(pattern, line)

            for match in matches:
                text = match.group(1).strip()
                if should_ignore(text):
                    continue

                old = f'{attr}="{text}"'
                new = f'{attr}="{{% trans "{text}" %}}"'
                line = line.replace(old, new, 1)

        modified_lines.append(line)

    return '\n'.join(modified_lines)


def process_template(filepath):
    """Procesa un archivo template"""
    print(f"Procesando: {filepath}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Crear backup
        backup_path = str(filepath) + BACKUP_SUFFIX
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Backup creado: {backup_path}")

        # Añadir {% load i18n %}
        content = add_load_i18n(content)

        # Marcar textos
        content = mark_text_for_translation(content)

        # Guardar archivo modificado
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✓ Archivo procesado correctamente")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Función principal"""
    print("🌍 Script de marcado automático para traducción")
    print("=" * 50)

    if not TEMPLATES_DIR.exists():
        print(f"❌ Error: No se encuentra el directorio {TEMPLATES_DIR}")
        return

    # Buscar todos los archivos .html
    templates = list(TEMPLATES_DIR.rglob('*.html'))

    if not templates:
        print(f"❌ No se encontraron templates en {TEMPLATES_DIR}")
        return

    print(f"\n📁 Encontrados {len(templates)} templates")
    print("\n¿Continuar? (s/n): ", end='')

    # Para testing, comentar estas líneas y descomentar la siguiente
    # response = input().lower()
    response = 's'  # Auto-confirmar para testing

    if response != 's':
        print("❌ Operación cancelada")
        return

    print("\n" + "=" * 50)

    # Procesar cada template
    success_count = 0
    for template in templates:
        if process_template(template):
            success_count += 1
        print()

    print("=" * 50)
    print(f"\n✅ Procesados {success_count}/{len(templates)} archivos")
    print(f"\n📝 Siguientes pasos:")
    print("1. Revisar los archivos modificados")
    print("2. Ejecutar: python manage.py makemessages -l es -l en")
    print("3. Traducir archivos .po en locale/")
    print("4. Ejecutar: python manage.py compilemessages")
    print("\n💡 Los backups están guardados con extensión .backup")


if __name__ == '__main__':
    main()