import unittest

from core.views import sanitize_notificacion_mensaje


class NotificacionEmojiTests(unittest.TestCase):
    def test_sanitize_notificacion_mensaje_removes_four_byte_characters(self):
        mensaje = "🎓 Alumne inscrit a la teva oferta 'Pràctiques'"

        sanitized = sanitize_notificacion_mensaje(mensaje)

        self.assertNotIn('🎓', sanitized)
        self.assertIn('Alumne inscrit a la teva oferta', sanitized)
