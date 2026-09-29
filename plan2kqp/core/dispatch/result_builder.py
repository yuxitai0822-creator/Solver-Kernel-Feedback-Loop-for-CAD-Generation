"""result_builder.py — build the final KQPResult JSON.

Assembles per-query results into the structured output format.
"""
from __future__ import annotations


def build_kqp_result(
    sample_id: str,
    kqp_schema_version: str,
    step_file: str,
    query_results: list[dict],
) -> dict:
    """Build the full KQPResult JSON.

    query_results: list of dicts from query_dispatcher.dispatch_query,
    each augmented with query_id, intent, source_field.
    """
    total = len(query_results)
    passed = sum(1 for r in query_results if r["status"] == "pass")
    failed = sum(1 for r in query_results if r["status"] == "fail")
    errors = sum(1 for r in query_results if r["status"] == "error")
    overall = "pass" if (failed == 0 and errors == 0 and total > 0) else "fail"

    return {
        "sample_id": sample_id,
        "kqp_schema_version": kqp_schema_version,
        "step_file": step_file,
        "overall_status": overall,
        "summary": {
            "total_queries": total,
            "passed_queries": passed,
            "failed_queries": failed,
            "error_queries": errors,
        },
        "query_results": query_results,
    }
