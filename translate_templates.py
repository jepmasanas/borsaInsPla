"""
Script SIMPLIFICADO para traducir solo los templates HTML
del catalán al castellano e inglés usando Google Translate.

UBICACIÓN: Guarda este archivo en la raíz del proyecto (mismo nivel que manage.py)

Uso:
    python translate_templates.py

Requisitos:
    pip install googletrans==4.0.0-rc1
"""

import os
import re
from pathlib import Path
from googletrans import Translator
import time


class SimpleTemplateTranslator:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.translator = Translator()
        self.templates_dir = self.base_dir / 'templates'
        self.locale_dir = self.base_dir / 'locale'

        # Diccionario para traducciones
        self.translations = {
            'es': {},
            'en': {}
        }

    def should_skip_text(self, text):
        """Determina si un texto debe ser omitido"""
        if not text or not text.strip():
            return True

        text = text.strip()

        # Ignorar si es muy corto
        if len(text) < 3:
            return True

        # Ignorar variables Django
        if '{{' in text or '{%' in text or '{#' in text:
            return True

        # Ignorar URLs, atributos, etc.
        skip_patterns = [
            r'^[.,;:!?]+$',  # Solo puntuación
            r'^\d+$',  # Solo números
            r'^https?://',  # URLs
            r'^class=',  # Atributos CSS
            r'^id=',  # IDs
        ]

        for pattern in skip_patterns:
            if re.search(pattern, text):
                return True

        return False

    def translate_text(self, text, dest_lang):
        """Traduce un texto usando Google Translate"""
        try:
            result = self.translator.translate(text, src='ca', dest=dest_lang)
            time.sleep(0.3)  # Evitar rate limiting
            return result.text
        except Exception as e:
            print(f"⚠️ Error traduciendo: {e}")
            return text

    def extract_texts_from_html(self, content):
        """Extrae textos traducibles de HTML"""
        texts = set()

        # Patrón 1: Texto entre tags HTML simples
        # >Texto aquí<
        pattern1 = r'>([^<>{}\n]+?)<'
        for match in re.finditer(pattern1, content):
            text = match.group(1).strip()
            if text and not self.should_skip_text(text):
                texts.add(text)

        # Patrón 2: Placeholders
        pattern2 = r'placeholder=["\']([^"\']+)["\']'
        for match in re.finditer(pattern2, content):
            text = match.group(1).strip()
            if text and not self.should_skip_text(text):
                texts.add(text)

        # Patrón 3: Títulos y alt
        pattern3 = r'(?:title|alt)=["\']([^"\']+)["\']'
        for match in re.finditer(pattern3, content):
            text = match.group(1).strip()
            if text and not self.should_skip_text(text):
                texts.add(text)

        return texts

    def create_locale_structure(self):
        """Crea la estructura de carpetas locale"""
        print("\n📁 Creando estructura de localización...")

        for lang in ['es', 'en']:
            lang_dir = self.locale_dir / lang / 'LC_MESSAGES'
            lang_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ {lang_dir}")

        print("✅ Estructura creada")

    def create_po_files(self):
        """Crea archivos .po iniciales"""
        print("\n📝 Creando archivos .po...")

        for lang_code, lang_name in [('es', 'Español'), ('en', 'English')]:
            po_file = self.locale_dir / lang_code / 'LC_MESSAGES' / 'django.po'

            header = f'''# TRANSLATION FILE FOR EstanyJobs
# Copyright (C) 2025
msgid ""
msgstr ""
"Project-Id-Version: EstanyJobs 1.0\\n"
"Language: {lang_code}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

'''
            with open(po_file, 'w', encoding='utf-8') as f:
                f.write(header)

            print(f"✅ {po_file}")

    def process_templates(self):
        """Procesa todos los templates HTML"""
        print("\n🔍 Buscando templates HTML...")

        html_files = list(self.templates_dir.rglob('*.html'))
        print(f"📄 Encontrados {len(html_files)} archivos")

        all_texts = set()

        # Extraer todos los textos
        for html_file in html_files:
            print(f"   📖 {html_file.relative_to(self.base_dir)}")

            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            texts = self.extract_texts_from_html(content)
            all_texts.update(texts)

        print(f"\n📊 Total de textos únicos encontrados: {len(all_texts)}")

        # Traducir todos
        print("\n🌍 Traduciendo textos...")
        for i, text in enumerate(sorted(all_texts), 1):
            if len(text) > 50:
                display_text = text[:50] + '...'
            else:
                display_text = text

            print(f"\n[{i}/{len(all_texts)}] {display_text}")

            # Traducir a español
            self.translations['es'][text] = self.translate_text(text, 'es')
            print(f"   🇪🇸 ES: {self.translations['es'][text]}")

            # Traducir a inglés
            self.translations['en'][text] = self.translate_text(text, 'en')
            print(f"   🇬🇧 EN: {self.translations['en'][text]}")

        # Guardar traducciones
        self.save_translations()

    def save_translations(self):
        """Guarda las traducciones en archivos .po"""
        print("\n💾 Guardando traducciones...")

        for lang_code in ['es', 'en']:
            po_file = self.locale_dir / lang_code / 'LC_MESSAGES' / 'django.po'

            with open(po_file, 'a', encoding='utf-8') as f:
                for original, translated in sorted(self.translations[lang_code].items()):
                    if original and translated:
                        # Escapar comillas
                        original_clean = original.replace('"', '\\"').replace('\n', '\\n')
                        translated_clean = translated.replace('"', '\\"').replace('\n', '\\n')

                        f.write(f'msgid "{original_clean}"\n')
                        f.write(f'msgstr "{translated_clean}"\n\n')

            print(f"✅ {po_file} - {len(self.translations[lang_code])} traducciones")

    def show_next_steps(self):
        """Muestra los siguientes pasos"""
        print("\n" + "="*60)
        print("✅ ¡TRADUCCIÓN COMPLETADA!")
        print("="*60)
        print("\n📋 PRÓXIMOS PASOS:\n")
        print("1️⃣  Actualizar config/settings.py:")
        print("    - Agregar LocaleMiddleware")
        print("    - Configurar LANGUAGES y LOCALE_PATHS")
        print()
        print("2️⃣  Actualizar config/urls.py:")
        print("    - Agregar: path('i18n/', include('django.conf.urls.i18n'))")
        print()
        print("3️⃣  Compilar traducciones:")
        print("    python manage.py compilemessages")
        print()
        print("4️⃣  Agregar selector de idioma en tu navbar")
        print()
        print("5️⃣  Reiniciar el servidor Django")
        print()
        print("="*60)
        print("\n💡 IMPORTANTE:")
        print("   Los templates NO han sido modificados.")
        print("   Solo se han generado los archivos de traducción (.po)")
        print("   Para que funcione, necesitas usar {% trans %} en templates.")
        print("="*60)


def main():
    print("="*60)
    print("🌍 TRADUCTOR DE TEMPLATES HTML")
    print("   EstanyJobs - Català → Español/English")
    print("="*60)

    # Detectar directorio base
    base_dir = Path(__file__).resolve().parent

    print(f"\n📂 Directorio del proyecto: {base_dir}")

    translator = SimpleTemplateTranslator(base_dir)

    # Verificar que exista la carpeta templates
    if not translator.templates_dir.exists():
        print(f"\n❌ ERROR: No se encuentra la carpeta {translator.templates_dir}")
        print("   Asegúrate de ejecutar el script desde la raíz del proyecto")
        return

    # Proceso
    translator.create_locale_structure()
    translator.create_po_files()
    translator.process_templates()
    translator.show_next_steps()


if __name__ == '__main__':
    main()