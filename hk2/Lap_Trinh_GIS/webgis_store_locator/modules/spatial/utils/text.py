import unicodedata


def strip_accents(text: str) -> str:
    if not text:
        return ''
    norm = unicodedata.normalize('NFD', text)
    norm = ''.join(ch for ch in norm if unicodedata.category(ch) != 'Mn')
    return unicodedata.normalize('NFC', norm)
