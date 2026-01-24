#!/usr/bin/env python3
import re
from pathlib import Path

INPUT = Path("README.md")
OUTPUT = Path("README_CV.generated.md")


def remove_specific_center_banner(text: str) -> str:
    # Supprime uniquement le bandeau image centré (<p align="center">...</p>)
    return re.sub(
        r'<p\s+align\s*=\s*"(?:center|centre)"\s*>.*?</p>\s*',
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

# def remove_left_badges_block(text: str) -> str:
#     # Supprime le bloc <p align="left">...</p> utilisé pour badges / shields
#     return re.sub(
#         r'<p\s+align\s*=\s*"left"\s*>.*?</p>\s*',
#         "",
#         text,
#         flags=re.IGNORECASE | re.DOTALL,
#     )
def extract_skills_from_badges(text: str) -> str:
    """
    Remplace le bloc <p align="left">...</p> contenant des badges
    par une liste texte des compétences (labels des ![]()).
    """
    def replace_block(match: re.Match) -> str:
        block = match.group(0)
        # Récupère tous les labels ![LABEL](...)
        skills = re.findall(r"!\[([^\]]+)\]\([^)]+\)", block)
        if not skills:
            return ""
        # Nettoyage + déduplication en conservant l’ordre
        seen = set()
        cleaned = []
        for skill in skills:
            s = skill.strip()
            if s and s not in seen:
                seen.add(s)
                cleaned.append(s)
        return "\n\n**Technologies maîtrisées :** " + ", ".join(cleaned) + "\n\n"
    return re.sub(
        r'<p\s+align\s*=\s*"left"\s*>.*?</p>',
        replace_block,
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )


def unwrap_table_keep_text(text: str) -> str:
    # Le <table> contient du texte utile → on enlève seulement la structure
    return re.sub(
        r"</?\s*(table|tr|td)\b[^>]*>",
        "\n",
        text,
        flags=re.IGNORECASE,
    )


def remove_html_images(text: str) -> str:
    # Supprime toutes les balises <img ...> sans toucher au texte
    return re.sub(r"<img\b[^>]*>", "", text, flags=re.IGNORECASE)


def convert_basic_html_to_md(text: str) -> str:
    # Gras
    text = re.sub(r"</?\s*b\s*>", "**", text, flags=re.IGNORECASE)

    # Titres HTML → Markdown
    text = re.sub(
        r"<h1[^>]*>\s*(.*?)\s*</h1>",
        r"# \1\n",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    text = re.sub(
        r"<h2[^>]*>\s*(.*?)\s*</h2>",
        r"## \1\n",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    text = re.sub(
        r"<h3[^>]*>\s*(.*?)\s*</h3>",
        r"### \1\n",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Paragraphes → texte brut
    text = re.sub(
        r"<p\b[^>]*>\s*(.*?)\s*</p>",
        r"\1\n",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # <br> → newline
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)

    return text


def remove_markdown_images(text: str) -> str:
    # Supprime uniquement les images Markdown ![](), conserve les liens
    return re.sub(r"!\[[^\]]*]\([^)]+\)", "", text)


def remove_github_stats_section(text: str) -> str:
    """
    Supprime UNIQUEMENT la section 'Statistiques GitHub'
    (regex ancrée pour éviter toute suppression excessive)
    """
    pattern = re.compile(
        r"(?ms)^[ \t]*##[^\n]*Statistiques GitHub[^\n]*\n.*?(?=^[ \t]*##\s|\Z)"
    )
    return pattern.sub("", text)


def normalize_headers_with_icons(text: str) -> str:
    # ## <img ...> Profil → ## Profil
    text = re.sub(
        r"(?m)^(#+)\s*<[^>]+>\s*",
        r"\1 ",
        text,
    )
    # Nettoyage espaces multiples
    return re.sub(r"[ \t]{2,}", " ", text)


def cleanup(text: str) -> str:
    # Normalise les fins de ligne
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Supprime les lignes ne contenant que des espaces
    text = re.sub(r"(?m)^[ \t]+$", "", text)
    # Réduit TOUTES les séquences de lignes vides à UNE seule
    text = re.sub(r"(?:\n[ \t]*){2,}", "\n\n", text)
    return text.strip() + "\n"


def main() -> None:
    raw = INPUT.read_text(encoding="utf-8")

    text = raw
    text = remove_specific_center_banner(text)
    text = unwrap_table_keep_text(text)
    # text = remove_left_badges_block(text)
    text = extract_skills_from_badges(text)
    text = remove_github_stats_section(text)
    text = remove_html_images(text)
    text = convert_basic_html_to_md(text)
    text = normalize_headers_with_icons(text)
    text = remove_markdown_images(text)
    text = cleanup(text)

    # Écrasement explicite pour comportement déterministe
    # if OUTPUT.exists():
    #     OUTPUT.unlink()

    OUTPUT.write_text(text, encoding="utf-8")
    print("✔ README_CV.generated.md overwritten successfully")


if __name__ == "__main__":
    main()
