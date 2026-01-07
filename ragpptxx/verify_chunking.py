from pipeline import process_document

chunks = process_document("sample.pdf", "test_team", 1)

assert len(chunks) == 5, "Chunk count must be 5"

sections = set()
for c in chunks:
    assert "section" in c
    assert "text" in c
    assert "ppt_id" in c
    assert "team_name" in c
    sections.add(c["section"])

assert len(sections) == 5, "All sections must exist"

print("✅ CHUNKING TEST PASSED")
