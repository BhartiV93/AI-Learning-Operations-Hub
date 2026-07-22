from foundry_client import FoundryClient
from knowledge_search import (
    search_knowledge_base,
    build_context_from_results,
)
from prompt_builder import build_grounded_prompt
from knowledge_validator import validate_search_results
class LearningAssistantOrchestrator:
    """Coordinate retrieval, prompt creation, and model invocation."""

    def __init__(self):
        self.foundry = FoundryClient()

    def process_question(
        self,
        question: str,
        assistant_instructions: str,
        previous_response_id: str | None = None,
    ):
        """
        Process one user question.

        Returns:
            stream:
                Streaming response returned by Azure AI Foundry.
            knowledge_sources:
                Source labels for validated knowledge.
        """
         
        search_results = search_knowledge_base(
            query=question
            )
        
        validated_results = validate_search_results(
            search_results
        )

        knowledge_context, knowledge_sources = (
            build_context_from_results(
                validated_results
            )
        )

        grounded_prompt = build_grounded_prompt(
            user_question=question,
            knowledge_context=knowledge_context,
        )

        stream = self.foundry.stream_response(
            instructions=assistant_instructions,
            user_input=grounded_prompt,
            previous_response_id=previous_response_id,
        )

        return stream, knowledge_sources