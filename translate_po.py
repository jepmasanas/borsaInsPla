"""
Script para traducir automáticamente archivos .po usando Google Translate
Uso: python translate_po.py
"""

import os
from pathlib import Path

try:
    from googletrans import Translator
    import polib
except ImportError:
    print("❌ Faltan dependencias. Instala con:")
    print("   pip install googletrans==4.0.0-rc1 polib")
    exit(1)

# Configuración
LOCALE_DIR = Path('locale')
SOURCE_LANG = 'ca'  # Idioma original (catalán)
TARGET_LANGS = ['es', 'en']  # Idiomas objetivo


def translate_po_file(po_path, target_lang):
    """Traduce un archivo .po completo"""
    print(f"\n📄 Traduciendo: {po_path}")
    print(f"   {SOURCE_LANG.upper()} → {target_lang.upper()}")

    translator = Translator()
    po = polib.pofile(str(po_path))

    total = len([e for e in po if not e.obsolete])
    translated = 0
    skipped = 0
    errors = 0

    for entry in po:
        if entry.obsolete:
            continue

        # Si ya tiene traducción, saltarla
        if entry.msgstr and entry.msgstr.strip():
            skipped += 1
            continue

        try:
            # Traducir el texto
            text_to_translate = entry.msgid

            # Saltar textos vacíos
            if not text_to_translate.strip():
                continue

            translation = translator.translate(
                text_to_translate,
                src=SOURCE_LANG,
                dest=target_lang
            )

            entry.msgstr = translation.text
            translated += 1

            # Mostrar progreso
            if translated % 10 == 0:
                print(f"   ⏳ {translated}/{total} traducidos...")

        except Exception as e:
            errors += 1
            print(f"   ⚠️  Error traduciendo: {entry.msgid[:50]}...")
            continue

    # Guardar archivo traducido
    po.save()

    print(f"   ✅ Traducidos: {translated}")
    print(f"   ⏭️  Saltados (ya traducidos): {skipped}")
    if errors > 0:
        print(f"   ❌ Errores: {errors}")
    print(f"   📁 Guardado: {po_path}")

    return translated


def main():
    """Función principal"""
    print("🌍 Script de traducción automática de archivos .po")
    print("=" * 60)

    if not LOCALE_DIR.exists():
        print(f"\n❌ Error: No existe el directorio {LOCALE_DIR}")
        print("   Primero ejecuta: python manage.py makemessages -l es -l en")
        return

    total_translated = 0

    for lang in TARGET_LANGS:
        po_path = LOCALE_DIR / lang / 'LC_MESSAGES' / 'django.po'

        if not po_path.exists():
            print(f"\n⚠️  No se encuentra: {po_path}")
            print(f"   Ejecuta: python manage.py makemessages -l {lang}")
            continue

        try:
            count = translate_po_file(po_path, lang)
            total_translated += count
        except Exception as e:
            print(f"\n❌ Error procesando {lang}: {e}")

    print("\n" + "=" * 60)
    print(f"✅ Total de traducciones: {total_translated}")
    print("\n📝 Siguientes pasos:")
    print("1. Revisar traducciones en locale/*/LC_MESSAGES/django.po")
    print("2. Ejecutar: python manage.py compilemessages")
    print("3. Reiniciar servidor: python manage.py runserver")


if __name__ == '__main__':
    main()