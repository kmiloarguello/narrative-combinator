"""Language-specific settings for Fragment Weaver."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageRules:
    """Vocabulary used by the lightweight coherence checks for one language."""

    name: str
    stop_words: frozenset[str]
    past_indicators: frozenset[str]
    future_indicators: frozenset[str]


LANGUAGE_RULES: dict[str, LanguageRules] = {
    "en": LanguageRules(
        name="English",
        stop_words=frozenset({"a", "an", "the", "and", "but", "or", "in", "on", "at", "to", "of", "is", "was", "be", "been", "have", "has", "had", "will", "would", "can", "not", "with", "from", "for", "as", "it", "that", "this", "she", "he", "they", "we", "you", "i", "when", "where", "what", "who", "if", "while", "are", "were", "also"}),
        past_indicators=frozenset({"yesterday", "ago", "had", "was", "were", "before", "once", "last", "long"}),
        future_indicators=frozenset({"tomorrow", "will", "soon", "eventually", "someday", "next"}),
    ),
    "fr": LanguageRules(
        name="French",
        stop_words=frozenset({"le", "la", "les", "un", "une", "des", "et", "ou", "mais", "dans", "sur", "à", "de", "du", "est", "était", "être", "avec", "pour", "par", "ce", "cette", "il", "elle", "ils", "nous", "vous", "je", "que", "qui", "si", "comme", "son", "sa", "ses", "plus", "pas", "rien", "chose", "quelque", "sans", "été", "durant"}),
        past_indicators=frozenset({"hier", "avait", "était", "étaient", "avant", "jadis", "dernier"}),
        future_indicators=frozenset({"demain", "sera", "seront", "bientôt", "prochain"}),
    ),
    "es": LanguageRules(
        name="Spanish",
        stop_words=frozenset({"el", "la", "los", "las", "un", "una", "unos", "unas", "y", "o", "pero", "en", "sobre", "a", "de", "del", "es", "era", "ser", "con", "para", "por", "este", "esta", "él", "ella", "ellos", "nosotros", "vosotros", "yo", "que", "quien", "si", "como"}),
        past_indicators=frozenset({"ayer", "había", "era", "eran", "antes", "una", "vez", "pasado"}),
        future_indicators=frozenset({"mañana", "será", "serán", "pronto", "algún", "día", "próximo"}),
    ),
}

LANGUAGES = tuple(LANGUAGE_RULES)


def get_language_rules(language: str) -> LanguageRules:
    """Return rules for a supported ISO 639-1 language code."""
    try:
        return LANGUAGE_RULES[language]
    except KeyError as exc:
        supported = ", ".join(LANGUAGES)
        raise ValueError(f"Unsupported language '{language}'. Choose one of: {supported}.") from exc
