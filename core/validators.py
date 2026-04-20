"""
Validadores personalizados de contraseñas para EstanyJobs
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re


class SequencePasswordValidator:
    """
    Valida que la contraseña no contenga secuencias consecutivas largas.
    - Secuencias de 3 caracteres o menos: OK
    - Secuencias de 4-6 caracteres: Seguridad media (permitido pero advertencia)
    - Secuencias de 7+ caracteres: Rechazado
    """

    def __init__(self, max_sequence_length=3):
        self.max_sequence_length = max_sequence_length

    def _get_max_sequence_length(self, password):
        """Calcula la longitud máxima de secuencia en la contraseña"""
        password_lower = password.lower()
        max_seq = 0

        # Secuencias numéricas ascendentes
        for i in range(len(password) - 1):
            seq_len = 1
            for j in range(i, len(password) - 1):
                if password[j].isdigit() and password[j + 1].isdigit():
                    if int(password[j]) + 1 == int(password[j + 1]):
                        seq_len += 1
                    else:
                        break
                else:
                    break
            max_seq = max(max_seq, seq_len)

        # Secuencias numéricas descendentes
        for i in range(len(password) - 1):
            seq_len = 1
            for j in range(i, len(password) - 1):
                if password[j].isdigit() and password[j + 1].isdigit():
                    if int(password[j]) - 1 == int(password[j + 1]):
                        seq_len += 1
                    else:
                        break
                else:
                    break
            max_seq = max(max_seq, seq_len)

        # Secuencias alfabéticas ascendentes
        for i in range(len(password_lower) - 1):
            seq_len = 1
            for j in range(i, len(password_lower) - 1):
                if password_lower[j].isalpha() and password_lower[j + 1].isalpha():
                    if ord(password_lower[j]) + 1 == ord(password_lower[j + 1]):
                        seq_len += 1
                    else:
                        break
                else:
                    break
            max_seq = max(max_seq, seq_len)

        # Secuencias alfabéticas descendentes
        for i in range(len(password_lower) - 1):
            seq_len = 1
            for j in range(i, len(password_lower) - 1):
                if password_lower[j].isalpha() and password_lower[j + 1].isalpha():
                    if ord(password_lower[j]) - 1 == ord(password_lower[j + 1]):
                        seq_len += 1
                    else:
                        break
                else:
                    break
            max_seq = max(max_seq, seq_len)

        # Secuencias de teclado comunes
        keyboard_sequences = ['qwerty', 'asdfgh', 'zxcvbn', 'qwertz', 'azerty']
        for seq in keyboard_sequences:
            if seq in password_lower:
                max_seq = max(max_seq, len(seq))

        return max_seq

    def validate(self, password, user=None):
        max_seq_length = self._get_max_sequence_length(password)

        # Rechazar contraseñas con secuencias de 7 o más caracteres
        if max_seq_length >= 7:
            raise ValidationError(
                _("La contrasenya conté seqüències massa llargues (%(length)d caràcters consecutius). "
                  "Màxim permès: 6 caràcters."),
                code='sequence_too_long',
                params={'length': max_seq_length},
            )

    def get_help_text(self):
        return _(
            "La teva contrasenya no pot contenir seqüències de més de 6 caràcters consecutius "
            "(com 1234567, abcdefg, etc.)."
        )


class ComplexityPasswordValidator:
    """
    Valida que la contraseña contenga al menos:
    - 1 mayúscula
    - 1 carácter especial
    """

    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("La contrasenya ha de contenir almenys una lletra majúscula."),
                code='no_uppercase',
            )

        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            raise ValidationError(
                _("La contrasenya ha de contenir almenys un caràcter especial (!@#$%^&*, etc.)."),
                code='no_special',
            )

        # ========== VALIDACIONES COMENTADAS (complejidad reducida) ==========
        # if not re.search(r'[a-z]', password):
        #     raise ValidationError(
        #         _("La contrasenya ha de contenir almenys una lletra minúscula."),
        #         code='no_lowercase',
        #     )
        #
        # if not re.search(r'[0-9]', password):
        #     raise ValidationError(
        #         _("La contrasenya ha de contenir almenys un número."),
        #         code='no_digit',
        #     )

    def get_help_text(self):
        return _(
            "La teva contrasenya ha de contenir almenys una majúscula i un caràcter especial."
        )


class RepeatedCharacterValidator:
    """
    Valida que la contraseña no tenga más de 3 caracteres repetidos consecutivos
    """

    def __init__(self, max_repeated=3):
        self.max_repeated = max_repeated

    def validate(self, password, user=None):
        for i in range(len(password) - self.max_repeated):
            sequence = password[i:i + self.max_repeated + 1]
            if len(set(sequence)) == 1:
                raise ValidationError(
                    _("La contrasenya no pot tenir més de %(max)d caràcters repetits consecutius."),
                    code='repeated_characters',
                    params={'max': self.max_repeated},
                )

    def get_help_text(self):
        return _(
            f"La teva contrasenya no pot tenir més de {self.max_repeated} "
            "caràcters repetits consecutius (com 'aaaa' o '1111')."
        )


class CommonPatternsValidator:
    """
    Valida que la contraseña no contenga patrones comunes peligrosos
    """

    def validate(self, password, user=None):
        password_lower = password.lower()

        dangerous_patterns = [
            'password', 'contraseña', 'contrasenya',
            '12345', '54321',
            'admin', 'root', 'user',
            'qwerty', 'asdfgh',
            'letmein', 'welcome',
            'monkey', 'dragon',
        ]

        for pattern in dangerous_patterns:
            if pattern in password_lower:
                raise ValidationError(
                    _("La contrasenya no pot contenir patrons comuns insegurs."),
                    code='common_pattern',
                )

    def get_help_text(self):
        return _(
            "La teva contrasenya no pot contenir paraules comuns "
            "com 'password', 'admin', '12345', etc."
        )