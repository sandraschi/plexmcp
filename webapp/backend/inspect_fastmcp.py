import inspect

import fastmcp.tools


def inspect_tool_result():
    try:
        print(f"ToolResult inspect: {inspect.signature(fastmcp.tools.ToolResult.__init__)}")
    except Exception as e:
        print(f"Error inspecting ToolResult: {e}")


if __name__ == "__main__":
    inspect_tool_result()
