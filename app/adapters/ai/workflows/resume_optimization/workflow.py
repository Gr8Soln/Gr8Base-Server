"""
Resume Optimization Workflow — LangGraph state machine.

Graph:
  strategy_planning
    → bullet_optimization
    → keyword_injection
    → assemble_resume
    → ats_evaluation ──(pass)──→ critic → END
                     ──(fail, retry < max)──→ bullet_optimization (loop)
"""
from langgraph.graph import END, StateGraph

from app.adapters.ai.workflows.resume_optimization.nodes import (
    assemble_resume_node,
    ats_evaluation_node,
    bullet_optimization_node,
    critic_node,
    keyword_injection_node,
    strategy_planning_node,
)
from app.adapters.ai.workflows.resume_optimization.state import ResumeOptimizationState


def _should_retry(state: ResumeOptimizationState) -> str:
    """Conditional edge: retry bullet optimization if score too low and under max iterations."""
    passed = state.get("evaluation_passed", True)
    iteration = state.get("iteration", 0)
    max_iter = state.get("max_iterations", 2)

    if not passed and iteration < max_iter:
        return "retry"
    return "proceed"


async def _increment_iteration(state: ResumeOptimizationState) -> dict:
    return {"iteration": state.get("iteration", 0) + 1}


def build_resume_optimization_workflow() -> StateGraph:
    graph = StateGraph(ResumeOptimizationState)

    graph.add_node("strategy_planning", strategy_planning_node)
    graph.add_node("bullet_optimization", bullet_optimization_node)
    graph.add_node("keyword_injection", keyword_injection_node)
    graph.add_node("assemble_resume", assemble_resume_node)
    graph.add_node("ats_evaluation", ats_evaluation_node)
    graph.add_node("increment_iteration", _increment_iteration)
    graph.add_node("critic", critic_node)

    graph.set_entry_point("strategy_planning")
    graph.add_edge("strategy_planning", "bullet_optimization")
    graph.add_edge("bullet_optimization", "keyword_injection")
    graph.add_edge("keyword_injection", "assemble_resume")
    graph.add_edge("assemble_resume", "ats_evaluation")

    # Conditional: retry loop or proceed to critic
    graph.add_conditional_edges(
        "ats_evaluation",
        _should_retry,
        {
            "retry": "increment_iteration",
            "proceed": "critic",
        },
    )
    graph.add_edge("increment_iteration", "bullet_optimization")
    graph.add_edge("critic", END)

    return graph


_compiled_workflow = None


def get_resume_optimization_workflow():
    global _compiled_workflow
    if _compiled_workflow is None:
        _compiled_workflow = build_resume_optimization_workflow().compile()
    return _compiled_workflow
