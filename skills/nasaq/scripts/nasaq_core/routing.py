"""Normalize command names only. Payloads and paths are never normalized."""
import unicodedata

ALIASES = {'الحالة': 'status', 'حاله': 'status', 'حالة': 'status', 'ابدأ': 'start',
           'ابدا': 'start', 'توقف': 'pause', 'استأنف': 'resume', 'استانف': 'resume',
           'الملخص': 'summary', 'ملخص': 'summary', 'اللغة': 'language',
           'افحص البيئة': 'doctor', 'doctor': 'doctor', 'inspect': 'inspect',
           'افحص المشروع': 'inspect', 'معاينة التثبيت': 'installation_preview'}


def command(value):
    if not isinstance(value, str):
        raise ValueError('invalid_action')
    normalized = ''.join(c for c in unicodedata.normalize('NFD', value.strip().lower())
                         if unicodedata.category(c) != 'Mn')
    if normalized.startswith('نسق '):
        normalized = normalized[4:].strip()
    if normalized.startswith('nasaq '):
        normalized = normalized[6:].strip()
    return ALIASES.get(normalized, normalized)
