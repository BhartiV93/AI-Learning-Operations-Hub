"""Load and split Markdown knowledge documents into searchable sections."""

from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_PATH = PROJECT_ROOT / "data" / "knowledge_base"

EXCLUDED_FILES = {
    "README.md",
    "knowledge_catalog.md",
}


def split_markdown_into_sections(
    document_name: str,
    content: str,
) -> list[dict[str, str]]:
    """
    Split a Markdown document using level-two headings.

    Example:
        ## Attendance Management
        Content...

    Each section becomes an independently searchable knowledge chunk.
    """

    sections: list[dict[str, str]] = []

    heading_pattern = re.compile(
    r"^(##|###)\s+(.+?)\s*$",
    flags=re.MULTILINE,
    )

    matches = list(heading_pattern.finditer(content))

    if not matches:
        return [
            {
                "document": document_name,
                "section": "Full Document",
                "content": content.strip(),
            }
        ]

    # Text before the first heading, often the title or introduction.
    introductory_text = content[: matches[0].start()].strip()

    if introductory_text:
        sections.append(
            {
                "document": document_name,
                "section": "Introduction",
                "content": introductory_text,
            }
        )

    for index, match in enumerate(matches):
        section_title = match.group(2).strip()
        section_start = match.end()

        if index + 1 < len(matches):
            section_end = matches[index + 1].start()
        else:
            section_end = len(content)

        section_content = content[section_start:section_end].strip()

        if not section_content:
            continue

        sections.append(
            {
                "document": document_name,
                "section": section_title,
                "content": section_content,
            }
        )

    return sections


def load_knowledge_sections() -> list[dict[str, str]]:
    """
    Load all Markdown files and return independently searchable sections.
    """

    if not KNOWLEDGE_BASE_PATH.exists():
        raise FileNotFoundError(
            f"Knowledge base folder not found: {KNOWLEDGE_BASE_PATH}"
        )

    knowledge_sections: list[dict[str, str]] = []

    for file_path in KNOWLEDGE_BASE_PATH.glob("*.md"):
        if file_path.name in EXCLUDED_FILES:
            continue

        content = file_path.read_text(encoding="utf-8").strip()

        if not content:
            continue

        sections = split_markdown_into_sections(
            document_name=file_path.stem,
            content=content,
        )

        knowledge_sections.extend(sections)

    return knowledge_sections


if __name__ == "__main__":
    loaded_sections = load_knowledge_sections()

    print(f"Loaded {len(loaded_sections)} knowledge section(s).\n")

    for section in loaded_sections:
        print(f"Document: {section['document']}")
        print(f"Section: {section['section']}")
        print(f"Characters: {len(section['content'])}")
        print("-" * 60)