
from fastmcp.tools import ToolResult
import json

def test_result():
    # Test common pattern
    try:
        res = ToolResult(content={"test": 1}, meta={"prefabs": ["test_prefab"]})
        print(f"SUCCESS with content/meta: {res}")
        print(f"Content: {res.content}")
        # Some versions of FastMCP use 'content' for the body
    except Exception as e:
        print(f"Error with content/meta: {e}")

if __name__ == "__main__":
    test_result()
