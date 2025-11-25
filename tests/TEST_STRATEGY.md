# PlexMCP Test Strategy

## Overview

PlexMCP uses a **dual-mode testing strategy** that supports both mock-based unit tests and real integration tests against an actual Plex Media Server.

## Test Modes

### 1. Unit Tests (Mock-Based) - Default Mode

**When:** Always runs, in CI/CD and local development  
**How:** Uses mocked PlexService and PlexAPI objects  
**Purpose:** Fast, reliable, no external dependencies

- All tests in `test_portmanteau_*.py` use mocks by default
- Tests verify tool logic, error handling, and response structure
- No Plex server required
- Fast execution (< 30 seconds for full suite)
- Suitable for CI/CD pipelines

**Running:**
```bash
pytest tests/                    # Run all tests (unit tests only)
pytest -m unit                   # Explicitly run unit tests
```

### 2. Fixture Database Tests - Middle Ground

**When:** For testing database queries and data structures without full server  
**How:** Uses minimal SQLite database in Plex format + small test video  
**Purpose:** Test database operations, data parsing, and file handling

- Tests marked with `@pytest.mark.fixture_db`
- Uses `tests/fixtures/plex_test.db` (minimal Plex SQLite database)
- Includes small test video file (~20KB, 5 seconds)
- Tests direct database queries and data structures
- No Plex server required, but limited to database operations

**Fixtures:**
- `plex_fixture_db`: Path to test SQLite database
- `plex_fixture_video`: Path to test video file
- `plex_fixture_service`: Service configured for fixture database (future)

**Running:**
```bash
# Create fixtures first (one-time setup)
python tests/fixtures/create_fixtures.py

# Run fixture database tests
pytest -m fixture_db
```

**Limitations:**
- PlexAPI doesn't directly support SQLite database access
- Requires custom database access layer or test Plex server
- Best for testing data parsing and structure validation

### 3. Integration Tests (Real Plex Server) - Optional Mode

**When:** Only when Plex server is available and accessible  
**How:** Connects to real Plex server using environment variables  
**Purpose:** Verify actual API interactions, end-to-end workflows

- Tests marked with `@pytest.mark.integration`
- Requires `PLEX_URL` and `PLEX_TOKEN` environment variables
- Automatically skipped if server is unavailable
- Tests real API calls, data transformations, and error scenarios
- Slower execution (depends on server response time)

**Running:**
```bash
# Set environment variables
export PLEX_URL=http://localhost:32400
export PLEX_TOKEN=your_token_here

# Run integration tests
pytest -m integration            # Only integration tests
pytest -m "not integration"      # Only unit tests
pytest                           # Both (integration skipped if server unavailable)
```

## Test Detection Logic

The test suite automatically detects if a real Plex server is available:

1. **Check Environment Variables:**
   - `PLEX_URL` or `PLEX_SERVER_URL` must be set
   - `PLEX_TOKEN` must be set

2. **Health Check:**
   - Attempts to connect to Plex server
   - Verifies authentication token is valid
   - Checks server responds to basic API calls

3. **Test Execution:**
   - If server is available: Integration tests run against real server
   - If server is unavailable: Integration tests are skipped with reason

## Test Structure

```
tests/
├── conftest.py                  # Shared fixtures and test configuration
├── test_portmanteau_*.py        # Unit tests (mock-based)
├── test_integration_*.py        # Integration tests (real server)
├── fixtures/                    # Test fixtures
│   ├── plex_test.db            # Minimal Plex SQLite database
│   ├── media/                  # Test media files
│   │   └── test_video.mp4     # Small test video (5 sec, ~20KB)
│   ├── library/                # Test library structure
│   └── create_fixtures.py     # Script to generate fixtures
└── TEST_STRATEGY.md            # This file
```

### Fixtures

**Unit Test Fixtures:**
- `mock_plex_service`: Mocked PlexService with all methods stubbed
- `mock_plex_server`: Mocked PlexServer object
- `mock_library_data`, `mock_user_data`, etc.: Sample data structures

**Fixture Database Fixtures:**
- `plex_fixture_db`: Path to minimal Plex SQLite database
- `plex_fixture_video`: Path to test video file
- `plex_fixture_service`: Service configured for fixture database (future)

**Integration Test Fixtures:**
- `real_plex_service`: Real PlexService connected to actual server
- `plex_available`: Pytest fixture that skips tests if server unavailable
- `test_library_id`: ID of a test library (if available)

## Writing Tests

### Unit Test Example

```python
@pytest.mark.asyncio
async def test_list_libraries(mock_plex_service):
    """Unit test using mocks."""
    with patch("plex_mcp.tools.portmanteau.library._get_plex_service", return_value=mock_plex_service):
        result = await plex_library.fn(operation="list")
        assert result["success"] is True
        assert "data" in result
```

### Integration Test Example

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_libraries_real(real_plex_service, plex_available):
    """Integration test against real Plex server."""
    result = await plex_library.fn(operation="list")
    assert result["success"] is True
    assert len(result["data"]) > 0  # Real server should have libraries
```

## CI/CD Configuration

### GitHub Actions

```yaml
# Unit tests always run
- name: Run unit tests
  run: pytest -m "not integration"

# Integration tests only if Plex server available
- name: Run integration tests
  if: env.PLEX_TOKEN != ''
  env:
    PLEX_URL: ${{ secrets.PLEX_URL }}
    PLEX_TOKEN: ${{ secrets.PLEX_TOKEN }}
  run: pytest -m integration
```

### Local Development

**Without Plex Server:**
```bash
pytest  # Runs unit tests only, integration tests skipped
```

**With Plex Server:**
```bash
export PLEX_URL=http://localhost:32400
export PLEX_TOKEN=your_token
pytest  # Runs both unit and integration tests
```

## Test Coverage

- **Unit Tests:** ~80% of test suite
  - Tool logic and error handling
  - Response structure validation
  - Parameter validation
  - Mock-based edge cases

- **Integration Tests:** ~20% of test suite
  - Real API interactions
  - End-to-end workflows
  - Data transformation accuracy
  - Real-world error scenarios

## Best Practices

1. **Always write unit tests first** - Fast feedback, no dependencies
2. **Add integration tests for critical paths** - Verify real behavior
3. **Use descriptive test names** - Indicate if test uses mocks or real server
4. **Keep integration tests isolated** - Don't modify server state permanently
5. **Use test markers** - `@pytest.mark.unit` or `@pytest.mark.integration`
6. **Skip destructive operations** - Integration tests should be read-only when possible

## Troubleshooting

**Integration tests always skipped:**
- Check `PLEX_URL` and `PLEX_TOKEN` are set
- Verify Plex server is running and accessible
- Check network connectivity to server
- Verify token has appropriate permissions

**Integration tests fail:**
- Check server logs for errors
- Verify token hasn't expired
- Ensure server version is compatible
- Check for rate limiting or connection issues

