# PlexMCP Test Suite

## Quick Start

### Run All Tests (Unit Tests Only)
```bash
pytest
```

### Run Only Unit Tests
```bash
pytest -m unit
```

### Run Integration Tests (Requires Real Plex Server)
```bash
# Set environment variables
export PLEX_URL=http://localhost:32400
export PLEX_TOKEN=your_token_here

# Run integration tests
pytest -m integration
```

## Test Strategy

See [TEST_STRATEGY.md](./TEST_STRATEGY.md) for detailed information about the dual-mode testing approach.

## Test Structure

- **Unit Tests** (`test_portmanteau_*.py`): Mock-based, fast, no dependencies
- **Integration Tests** (`test_integration_*.py`): Real Plex server, optional

## Fixtures

### Unit Test Fixtures
- `mock_plex_service`: Mocked PlexService
- `mock_plex_server`: Mocked PlexServer
- `mock_library_data`, `mock_user_data`, etc.: Sample data

### Integration Test Fixtures
- `real_plex_service`: Real PlexService (requires Plex server)
- `plex_available`: Skips tests if server unavailable
- `test_library_id`: First available library ID

## Writing Tests

### Unit Test
```python
@pytest.mark.asyncio
async def test_something(mock_plex_service):
    with patch("...", return_value=mock_plex_service):
        result = await tool.fn(...)
        assert result["success"] is True
```

### Integration Test
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_something_real(real_plex_service, plex_available):
    with patch("...", return_value=real_plex_service):
        result = await tool.fn(...)
        assert result["success"] is True
```

## CI/CD

Unit tests run automatically. Integration tests require:
- `PLEX_URL` secret
- `PLEX_TOKEN` secret
- Accessible Plex server
