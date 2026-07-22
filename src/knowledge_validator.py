from typing import Any


MINIMUM_COVERAGE = 0.60
MINIMUM_MATCHED_TERMS = 2


def validate_search_results(
    results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Return only search results that contain sufficient evidence
    to support the user's question.

    Coverage is stored as a decimal:
    0.60 means 60% coverage.
    """

    if not results:
        return []

    validated_results: list[dict[str, Any]] = []

    for result in results:
        coverage = float(result.get("coverage", 0.0))
        matched_terms = result.get("matched_terms", [])
        content = str(result.get("content", "")).strip()

        has_sufficient_coverage = (
            coverage >= MINIMUM_COVERAGE
        )

        has_sufficient_matches = (
            len(set(matched_terms))
            >= MINIMUM_MATCHED_TERMS
        )

        has_content = bool(content)

        if (
            has_sufficient_coverage
            and has_sufficient_matches
            and has_content
        ):
            validated_results.append(result)

    return validated_results