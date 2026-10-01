"""Reproduce Exercise 3.5 on saved retrievals without gold leakage."""

from collections import Counter
import json
from pathlib import Path

from evaluate_answers import load_evaluation_inputs
from template import RAGASEvaluator, rerank_by_overlap


def main() -> None:
    pairs, _ = load_evaluation_inputs(
        "golden_dataset.json", "artifacts/actual_answers.json"
    )
    evaluator = RAGASEvaluator()
    rows = []
    for pair in pairs:
        before = pair.retrieved_contexts
        after = rerank_by_overlap(before, pair.question)
        assert Counter(before) == Counter(after), "Retrieved set changed"
        recall_before = evaluator.evaluate_context_recall(before, pair.expected_answer)
        recall_after = evaluator.evaluate_context_recall(after, pair.expected_answer)
        assert recall_before == recall_after, "Recall changed after permutation"
        rows.append({
            "id": pair.metadata["id"],
            "recall_before": recall_before,
            "recall_after": recall_after,
            "precision_before": evaluator.evaluate_context_precision(before, pair.expected_answer),
            "precision_after": evaluator.evaluate_context_precision(after, pair.expected_answer),
            "order_before": before,
            "order_after": after,
        })
    keys = ("recall_before", "recall_after", "precision_before", "precision_after")
    artifact = {
        "query_source": "question only; expected_answer used for scoring only",
        "generation_rerun": False,
        "results": rows,
        "averages": {key: sum(row[key] for row in rows) / len(rows) for key in keys},
    }
    Path("artifacts/reranking_results.json").write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(artifact["averages"], indent=2))


if __name__ == "__main__":
    main()
