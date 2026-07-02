"""
ATS Scoring Workflow — LangGraph state machine.

Graph:
  keyword_match ──┐
  semantic_match ──┤
  technical_alignment ──┤─→ seniority_alignment → impact_score → ats_safety → critique → aggregate
"""
from langgraph.graph import END, StateGraph

from app.adapters.ai.workflows.ats_scoring.nodes import (
    aggregate_scores_node,
    ats_safety_node,
    critique_node,
    impact_score_node,
    keyword_match_node,
    semantic_match_node,
    seniority_alignment_node,
    technical_alignment_node,
)
from app.adapters.ai.workflows.ats_scoring.state import ATSScoringState


def build_ats_scoring_workflow() -> StateGraph:
    graph = StateGraph(ATSScoringState)

    # Register nodes
    graph.add_node("keyword_match", keyword_match_node)
    graph.add_node("semantic_match", semantic_match_node)
    graph.add_node("technical_alignment", technical_alignment_node)
    graph.add_node("seniority_alignment", seniority_alignment_node)
    graph.add_node("impact_score", impact_score_node)
    graph.add_node("ats_safety", ats_safety_node)
    graph.add_node("critique", critique_node)
    graph.add_node("aggregate_scores", aggregate_scores_node)

    # Entry point — first three nodes run sequentially
    graph.set_entry_point("keyword_match")
    graph.add_edge("keyword_match", "semantic_match")
    graph.add_edge("semantic_match", "technical_alignment")
    graph.add_edge("technical_alignment", "seniority_alignment")
    graph.add_edge("seniority_alignment", "impact_score")
    graph.add_edge("impact_score", "ats_safety")
    graph.add_edge("ats_safety", "critique")
    graph.add_edge("critique", "aggregate_scores")
    graph.add_edge("aggregate_scores", END)

    return graph


# Compiled graph — reused across requests
_compiled_workflow = None


def get_ats_scoring_workflow():
    global _compiled_workflow
    if _compiled_workflow is None:
        _compiled_workflow = build_ats_scoring_workflow().compile()
    return _compiled_workflow
