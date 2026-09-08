from aimemory import Evidence, JsonlMemoryStore, MemoryRecord, VerificationStatus


def test_jsonl_round_trip(tmp_path):
    store = JsonlMemoryStore(tmp_path / "memory.jsonl")
    original = MemoryRecord(
        content="Structured evidence survives the hand-off.",
        tags=["research", "handoff"],
        evidence=[
            Evidence(
                claim="The hand-off is structured.",
                source="test://local",
                confidence=0.9,
                status=VerificationStatus.SUPPORTED,
            )
        ],
    )

    store.append(original)
    restored = list(store.all())

    assert len(restored) == 1
    assert restored[0].id == original.id
    assert restored[0].content == original.content
    assert restored[0].evidence[0].status is VerificationStatus.SUPPORTED
