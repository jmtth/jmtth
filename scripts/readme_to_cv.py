#!/usr/bin/env python3

import re
from pathlib import Path

INPUT = Path("README.md")
OUTPUT = Path("README_CV.generated.md")


def remove_html_blocks(text: str, tag: str) -> str:
    """
    Remove full HTML blocks like <tag> ... </tag>
    """
    pattern = re.compile(
        rf"<{tag}[^>]*>.*?</{tag}>",
        flags=re.DOTALL | re.IGNORECASE,
    )
    return pattern.sub("", text)


def remove_markdown_images(text: str) -> str:
    """
    Remove Markdown images ![alt](path)
    """
    return re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)


def remove_html_images(text: str) -> str:
    """
    Remove <img ...> tags
    """
    return re.sub(r"<img[^>]*>", "", text, flags=re.IGNORECASE)


def remove_github_stats_section(text: str) -> str:
    """
    Remove the GitHub statistics section entirely
    """
    pattern = re.compile(
        r"##.*Statistiques GitHub.*?(?=\n## |\Z)",
        flags=re.DOTALL | re.IGNORECASE,
    )
    return pattern.sub("", text)


def normalize_titles(text: str) -> str:
    """
    Clean titles polluted by inline HTML/icons
    """
    # Remove residual inline HTML inside headers
    text = re.sub(r"(#+)\s*<[^>]+>\s*", r"\1 ", text)
    return text


def cleanup_spacing(text: str) -> str:
    """
    Normalize excessive blank lines
    """
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def main():
    raw = INPUT.read_text(encoding="utf-8")

    text = raw
    text = remove_html_blocks(text, "table")
    text = remove_html_blocks(text, "p")
    text = remove_github_stats_section(text)
    text = remove_html_images(text)
    text = remove_markdown_images(text)
    text = normalize_titles(text)
    text = cleanup_spacing(text)

    OUTPUT.write_text(text, encoding="utf-8")

    print("✔ README_CV.generated.md generated successfully")


if __name__ == "__main__":
    main()
