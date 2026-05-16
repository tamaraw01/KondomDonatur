import re
import unicodedata


LEETSPEAK_MAP = {
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
    "8": "b",
    "@": "a",
    "$": "s",
    "!": "i",
}
DECORATIVE_LATIN_RE = re.compile(r"LATIN (?:CAPITAL|SMALL) LETTER ([A-Z])")
DIGIT_NAME_MAP = {
    "ZERO": "0",
    "ONE": "1",
    "TWO": "2",
    "THREE": "3",
    "FOUR": "4",
    "FIVE": "5",
    "SIX": "6",
    "SEVEN": "7",
    "EIGHT": "8",
    "NINE": "9",
}
CONFUSABLE_CHAR_MAP = {
    "ㄖ": "o",
    "๒": "b",
    "Δ": "a",
    "Ɨ": "i",
    "к": "k",
    "К": "k",
    "Ħ": "h",
    "ħ": "h",
    "几": "n",
    "ᗪ": "d",
    "η": "n",
    "Η": "h",
}


def _safe_text(text: object) -> str:
    if text is None:
        return ""
    return str(text)


def normalize_nfkc(text: object) -> str:
    return unicodedata.normalize("NFKC", _safe_text(text))


def ascii_fold(text: object) -> str:
    normalized = unicodedata.normalize("NFKD", _safe_text(text))
    return normalized.encode("ascii", "ignore").decode("ascii")


def is_emoji(char: str) -> bool:
    codepoint = ord(char)
    return (
        0x1F000 <= codepoint <= 0x1FAFF
        or 0x2600 <= codepoint <= 0x26FF
    )


def is_suspicious_text_char(char: str) -> bool:
    if not char or char.isspace() or is_emoji(char):
        return False
    if ord(char) <= 127:
        return False
    category = unicodedata.category(char)
    if category.startswith(("L", "N", "M")):
        return True
    name = unicodedata.name(char, "")
    return any(token in name for token in ["LETTER", "DIGIT", "CIRCLED", "SQUARED", "MODIFIER"])


def fold_decorative_unicode(text: object) -> str:
    folded_chars: list[str] = []
    for char in _safe_text(text):
        if char in CONFUSABLE_CHAR_MAP:
            folded_chars.append(CONFUSABLE_CHAR_MAP[char])
            continue
        normalized = unicodedata.normalize("NFKC", char)
        if normalized != char and normalized.isascii():
            folded_chars.append(normalized)
            continue
        name = unicodedata.name(char, "")
        if "DIGIT" in name:
            for digit_name, digit_value in DIGIT_NAME_MAP.items():
                if digit_name in name:
                    folded_chars.append(digit_value)
                    break
            else:
                folded_chars.append(char)
            continue
        match = DECORATIVE_LATIN_RE.search(name)
        if match:
            folded_chars.append(match.group(1))
            continue
        folded_chars.append(char)
    return "".join(folded_chars)


def normalize_leetspeak(text: object) -> str:
    value = _safe_text(text)
    result: list[str] = []
    for index, char in enumerate(value):
        replacement = LEETSPEAK_MAP.get(char)
        if replacement is None:
            result.append(char)
            continue

        prev_char = value[index - 1] if index > 0 else ""
        next_char = value[index + 1] if index + 1 < len(value) else ""
        is_symbol_leet = char in {"@", "$", "!"}
        is_embedded_digit = char.isdigit() and prev_char.isalpha() and next_char.isalpha()
        if is_symbol_leet or is_embedded_digit:
            result.append(replacement)
        else:
            result.append(char)
    return "".join(result)


def collapse_separated_letters(text: object) -> str:
    value = _safe_text(text)
    # Handles "s-l-o-t", "s.l.o.t", and symbol-spaced decorative text after folding.
    return re.sub(
        r"(?<![a-z0-9])(?:[a-z][\s\W_]+){2,}[a-z](?![a-z0-9])",
        lambda match: re.sub(r"[^a-z]", "", match.group(0)),
        value,
        flags=re.I,
    )


def remove_extra_spaces(text: object) -> str:
    return re.sub(r"\s+", " ", _safe_text(text)).strip()


def reconstruct_spaced_tokens(text: object) -> str:
    value = _safe_text(text)

    def join_letters(match: re.Match[str]) -> str:
        token = match.group(0)
        return token.replace(" ", "")

    # Rebuild runs such as "s l o t", "g a c o r", and "r t p".
    return re.sub(r"(?<!\w)(?:[a-zA-Z]\s+){2,}[a-zA-Z](?!\w)", join_letters, value)


def deobfuscate_text(text: object) -> str:
    value = fold_decorative_unicode(text)
    value = normalize_nfkc(value)
    value = ascii_fold(value)
    value = value.lower()
    value = normalize_leetspeak(value)
    value = value.replace("_", " ")
    value = re.sub(r"[\u200b-\u200f\u202a-\u202e]", "", value)
    value = re.sub(r"([a-z])[\.\-~`'\"|]+(?=[a-z])", r"\1", value)
    value = collapse_separated_letters(value)
    value = reconstruct_spaced_tokens(value)
    value = remove_extra_spaces(value)
    return value


def compute_unicode_symbol_ratio(text: object) -> float:
    value = _safe_text(text)
    if not value:
        return 0.0
    suspicious = 0
    for char in value:
        category = unicodedata.category(char)
        if ord(char) > 127 or category.startswith(("S", "M")):
            suspicious += 1
    return round(suspicious / len(value), 4)


def compute_suspicious_text_char_ratio(text: object) -> float:
    value = _safe_text(text)
    if not value:
        return 0.0
    return round(sum(is_suspicious_text_char(char) for char in value) / len(value), 4)


def compute_digit_ratio(text: object) -> float:
    value = _safe_text(text)
    if not value:
        return 0.0
    return round(sum(char.isdigit() for char in value) / len(value), 4)


def compute_obfuscation_score(raw_text: object, deobfuscated_text: object) -> float:
    raw = _safe_text(raw_text)
    deobfuscated = _safe_text(deobfuscated_text)
    if not raw:
        return 0.0

    digit_ratio = compute_digit_ratio(raw)
    unicode_ratio = compute_unicode_symbol_ratio(raw)
    symbol_ratio = sum(
        1
        for char in raw
        if not char.isalnum() and not char.isspace()
    ) / max(len(raw), 1)
    length_delta = abs(len(raw) - len(deobfuscated)) / max(len(raw), 1)
    raw_simple = remove_extra_spaces(ascii_fold(normalize_nfkc(fold_decorative_unicode(raw))).lower())
    difference_ratio = 0.0 if raw_simple == deobfuscated else 0.25

    score = (
        (digit_ratio * 0.25)
        + (unicode_ratio * 0.30)
        + (symbol_ratio * 0.20)
        + (min(length_delta, 1.0) * 0.15)
        + difference_ratio
    )
    return round(max(0.0, min(score, 1.0)), 4)
