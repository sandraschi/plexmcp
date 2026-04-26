from plex_mcp.services.rag_ingestor import PlexIngestor


def test_srt_parsing_unit():
    """Verify that the SRT parser correctly extracts text and timestamps."""
    ingestor = PlexIngestor(None, None)
    sample_srt = """1
00:00:01,000 --> 00:00:04,000
Hello, world!
This is a test.

2
00:00:05,000 --> 00:00:08,000
<i>Italicized text</i> and <b>bold text</b>.
"""
    items = ingestor._parse_srt(sample_srt)

    assert len(items) == 2
    assert items[0]["text"] == "Hello, world! This is a test."
    assert items[0]["start_ms"] == 1000
    assert items[0]["end_ms"] == 4000

    # Verify HTML stripping
    assert items[1]["text"] == "Italicized text and bold text."
    assert items[1]["start_ms"] == 5000
    assert items[1]["end_ms"] == 8000


def test_vtt_parsing_unit():
    """Verify that the VTT parser correctly extracts text and timestamps."""
    ingestor = PlexIngestor(None, None)
    sample_vtt = """WEBVTT

1
00:00:01.000 --> 00:00:04.000
Hello from VTT!

00:00:05.500 --> 00:00:08.500
Timestamp only header.
"""
    items = ingestor._parse_vtt(sample_vtt)

    assert len(items) == 2
    assert items[0]["text"] == "Hello from VTT!"
    assert items[0]["start_ms"] == 1000

    assert items[1]["text"] == "Timestamp only header."
    assert items[1]["start_ms"] == 5500


def test_dialogue_chunking():
    """Verify that dialogue is grouped into overlapping chunks."""
    ingestor = PlexIngestor(None, None)
    # Create 15 items
    items = [{"start_ms": i * 1000, "end_ms": (i + 1) * 1000, "text": f"Line {i}"} for i in range(15)]

    chunks = ingestor._chunk_dialogue(items)

    # chunk_size=8, overlap=2. Steps = 8-2 = 6.
    # Chunk 0: 0-7
    # Chunk 1: 6-13
    # Chunk 2: 12-14
    assert len(chunks) == 3
    assert "Line 0" in chunks[0]["text"]
    assert "Line 7" in chunks[0]["text"]
    assert "Line 8" not in chunks[0]["text"]

    assert "Line 6" in chunks[1]["text"]  # Overlap
    assert "Line 7" in chunks[1]["text"]  # Overlap
    assert "Line 13" in chunks[1]["text"]

    # Verify metadata
    assert chunks[0]["start_ms"] == 0
    assert chunks[0]["end_ms"] == 8000
