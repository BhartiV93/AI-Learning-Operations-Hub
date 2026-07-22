def build_grounded_prompt(
    user_question: str,
    knowledge_context: str,
) -> str:
    """Build a prompt grounded in organisational knowledge."""

    if knowledge_context:
        return f"""
Answer the user's question using only the organisational knowledge below.

Rules:
- Use only explicit evidence from the supplied knowledge.
- Do not invent policies, deadlines, eligibility criteria, numbers, or responsibilities.
- Do not use general knowledge to fill missing organisational information.
- If the supplied knowledge does not explicitly answer the question, respond:
  "The available organisational knowledge does not specify this information."
- Mention the source document and section used.

ORGANISATIONAL KNOWLEDGE:
{knowledge_context}

USER QUESTION:
{user_question}
""".strip()

    return f"""
No relevant organisational knowledge was retrieved.

USER QUESTION:
{user_question}

Respond exactly with:
"The available organisational knowledge does not specify this information."
""".strip()