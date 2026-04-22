from __future__ import annotations

import play_book_studio.retrieval.retriever_search as retriever_search


class _BoomVectorRetriever:
    def search_with_trace(self, query: str, top_k: int):  # noqa: ANN202
        raise ValueError('Not found: Collection `openshift_docs` doesn\'t exist!')


class _DummyRetriever:
    def __init__(self, vector_retriever) -> None:
        self.settings = object()
        self.vector_retriever = vector_retriever


def test_search_vector_candidates_degrades_when_collection_is_missing(monkeypatch) -> None:
    monkeypatch.setattr(
        retriever_search,
        "search_selected_customer_pack_private_vectors",
        lambda settings, context, query, top_k: ([], {"status": "not_ready", "hit_count": 0}),
    )
    trace_events: list[dict[str, object]] = []

    result = retriever_search.search_vector_candidates(
        _DummyRetriever(_BoomVectorRetriever()),
        context=None,
        rewritten_queries=["오픈시프트가 뭐야?"],
        effective_candidate_k=8,
        trace_callback=trace_events.append,
        timings_ms={},
    )

    assert result["hits"] == []
    runtime = result["runtime"]
    assert runtime["status"] == "degraded"
    assert "openshift_docs" in str(runtime["error"])
    assert runtime["subquery_count"] == 1
    assert trace_events[-1]["status"] == "error"


def test_search_vector_candidates_degrades_when_vector_retriever_is_not_configured(monkeypatch) -> None:
    monkeypatch.setattr(
        retriever_search,
        "search_selected_customer_pack_private_vectors",
        lambda settings, context, query, top_k: ([], {"status": "not_ready", "hit_count": 0}),
    )
    trace_events: list[dict[str, object]] = []

    result = retriever_search.search_vector_candidates(
        _DummyRetriever(None),
        context=None,
        rewritten_queries=["클러스터 업그레이드"],
        effective_candidate_k=8,
        trace_callback=trace_events.append,
        timings_ms={},
    )

    assert result["hits"] == []
    runtime = result["runtime"]
    assert runtime["status"] == "degraded"
    assert runtime["error"] == "vector retriever is not configured"
    assert trace_events[-1]["detail"] == "vector retriever is not configured"
