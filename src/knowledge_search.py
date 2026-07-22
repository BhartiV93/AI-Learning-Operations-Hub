"""Search the LearnFlow AI local knowledge base."""

import re
from typing import Any

from knowledge_loader import load_knowledge_sections


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "defined",
    "do",
    "does",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "me",
    "of",
    "on",
    "or",
    "should",
    "the",
    "their",
    "this",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
    "with",
    "after",
}


SYNONYMS = {
    "video": {"recording"},
    "recording": {"video"},

    "class": {"session", "training"},
    "lesson": {"session", "training"},
    "session": {"class", "training"},

    "receive": {"share", "send", "provide"},
    "share": {"receive", "send", "provide"},
    "send": {"share", "provide"},

    "participation": {"attendance"},
    "presence": {"attendance"},

    "test": {"assessment"},
    "quiz": {"assessment"},

    "project": {"capstone"},
    "capstone": {"project"},

    "criteria": {"requirements", "eligibility"},
    "requirement": {"criteria", "eligibility"},
    "requirements": {"criteria", "eligibility"},
    "eligible": {"eligibility", "criteria"},

    "student": {"learner"},
    "students": {"learners"},
    "learner": {"student"},
    "learners": {"students"},
}

MINIMUM_MATCHED_TERMS = 2
MINIMUM_TERM_COVERAGE = 0.60
MINIMUM_RELEVANCE_SCORE = 2.0


def normalize_word(word: str) -> str:
    """
    Apply small normalisation rules.

    This is intentionally simple and is not a complete linguistic stemmer.
    """

    word = word.lower().strip()

    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"

    if word.endswith("s") and len(word) > 4:
        return word[:-1]

    return word


def tokenize(text: str) -> set[str]:
    """
    Convert text into meaningful lowercase terms.
    """

    raw_words = re.findall(r"[a-zA-Z0-9]+", text.lower())

    terms = {
        normalize_word(word)
        for word in raw_words
        if word not in STOP_WORDS and len(word) > 2
    }

    return terms


def expand_query_terms(query_terms: set[str]) -> set[str]:
    """
    Add a limited set of synonyms without replacing the original terms.
    """

    expanded_terms = set(query_terms)

    for term in query_terms:
        synonym_values = SYNONYMS.get(term, set())

        expanded_terms.update(
            normalize_word(value)
            for value in synonym_values
        )

    return expanded_terms


def evaluate_section_match(
    query: str,
    section_title: str,
    section_content: str,
) -> dict[str, Any]:
    """
    Evaluate how well a knowledge section matches a query.

    Coverage is calculated by checking whether each original query concept,
    or one of its configured synonyms, appears in the section.
    """

    original_query_terms = tokenize(query)

    title_terms = tokenize(section_title)
    content_terms = tokenize(section_content)
    section_terms = title_terms | content_terms

    matched_query_concepts: set[str] = set()
    matched_section_terms: set[str] = set()

    for query_term in original_query_terms:
        related_terms = {
            query_term,
            *{
                normalize_word(value)
                for value in SYNONYMS.get(query_term, set())
            },
        }

        concept_matches = related_terms & section_terms

        if concept_matches:
            matched_query_concepts.add(query_term)
            matched_section_terms.update(concept_matches)

    if not original_query_terms:
        coverage = 0.0
    else:
        coverage = (
            len(matched_query_concepts)
            / len(original_query_terms)
        )

    title_matches = set()
    content_matches = set()

    for query_term in original_query_terms:
        related_terms = {
            query_term,
            *{
                normalize_word(value)
                for value in SYNONYMS.get(query_term, set())
            },
        }

        title_matches.update(related_terms & title_terms)
        content_matches.update(related_terms & content_terms)

    relevance_score = (
        len(title_matches) * 3.0
        + len(content_matches) * 1.0
    )

    return {
        "query_terms": sorted(original_query_terms),
        "matched_terms": sorted(matched_query_concepts),
        "matched_section_terms": sorted(matched_section_terms),
        "coverage": coverage,
        "score": relevance_score,
    }


def is_acceptable_match(match_details: dict[str, Any]) -> bool:
    """
    Apply conservative retrieval thresholds.
    """

    matched_term_count = len(match_details["matched_terms"])
    coverage = float(match_details["coverage"])
    score = float(match_details["score"])

    return (
        matched_term_count >= MINIMUM_MATCHED_TERMS
        and coverage >= MINIMUM_TERM_COVERAGE
        and score >= MINIMUM_RELEVANCE_SCORE
    )


def search_knowledge_base(
    query: str,
    max_results: int = 1,
) -> list[dict[str, Any]]:
    """
    Return sections that pass all relevance checks.
    """

    knowledge_sections = load_knowledge_sections()
    ranked_results: list[dict[str, Any]] = []

    for section in knowledge_sections:
        match_details = evaluate_section_match(
            query=query,
            section_title=section["section"],
            section_content=section["content"],
        )

        if not is_acceptable_match(match_details):
            continue

        ranked_results.append(
            {
                "document": section["document"],
                "section": section["section"],
                "content": section["content"],
                "score": match_details["score"],
                "coverage": match_details["coverage"],
                "matched_terms": match_details["matched_terms"],
                "matched_section_terms": match_details["matched_section_terms"],
            })
    

    ranked_results.sort(
        key=lambda result: (
            float(result["coverage"]),
            float(result["score"]),
        ),
        reverse=True,
    )

    return ranked_results[:max_results]


def build_context_from_results(results):
    """
    Build a context string and source labels from validated search results.
    """
    if not results:
        return "", []

    context_sections: list[str] = []
    source_labels: list[str] = []

    for result in results:
        source_label = (
            f"{result['document']} — {result['section']}"
        )

        source_labels.append(source_label)

        context_sections.append(
            f"""
SOURCE DOCUMENT: {result["document"]}
SOURCE SECTION: {result["section"]}

{result["content"]}
""".strip()
        )

    combined_context = "\n\n---\n\n".join(context_sections)

    return combined_context, source_labels


if __name__ == "__main__":
    test_query = input(
        "Enter a knowledge search question: "
    ).strip()

    results = search_knowledge_base(test_query)

    if not results:
        print("\nNo sufficiently relevant knowledge was found.")
    else:
        print(
            f"\nFound {len(results)} relevant section(s):\n"
        )

        for result in results:
            print(f"Document: {result['document']}")
            print(f"Section: {result['section']}")
            print(f"Score: {result['score']:.1f}")
            print(f"Coverage: {result['coverage']:.0%}")
            print(
                "Matched terms: "
                + ", ".join(result["matched_terms"])
            )
            print(
                "Matched source terms: "
                + ", ".join(result["matched_section_terms"])
            )
            print(
                f"Preview: {result['content'][:300]}..."
            )
            print("-" * 60)