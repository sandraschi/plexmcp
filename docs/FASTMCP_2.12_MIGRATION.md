# FastMCP 2.12 Migration Guide

**Date:** 2025-10-21  
**Status:** Official Standard  
**Applies to:** All MCP projects using FastMCP

---

## 🎯 The Big Change

**FastMCP 2.12 changed how tool documentation works:**

### ❌ OLD Way (Pre-2.12)
```python
@mcp.tool(
    description="""This tool does something cool.
    
    It has many features and options.
    Use it when you need to do things."""
)
async def my_tool(param: str) -> str:
    """Just a basic docstring."""
    return "result"
```

### ✅ NEW Way (2.12+)
```python
@mcp.tool
async def my_tool(param: str) -> str:
    '''This tool does something cool with comprehensive documentation.
    
    FEATURES:
    - Feature 1 explained
    - Feature 2 explained
    - Feature 3 explained
    
    Args:
        param: Parameter description with type and purpose
        
    Returns:
        Result description with format details
        
    Examples:
        Basic usage: my_tool("value")
        Advanced: my_tool("complex-value")
        
    Notes:
        - Important note 1
        - Important note 2
    '''
    return "result"
```

---

## 🚨 Critical Rule

**NEVER use `description=` parameter in `@mcp.tool()`**

### Why?

**The description parameter OVERRIDES the docstring!**
- FastMCP reads docstring for tool info
- If description= exists, it uses THAT instead
- Your beautiful docstring gets ignored!
- Documentation becomes split between two places

### What Happens

```python
@mcp.tool(description="Short description")  # ❌ BAD!
async def my_tool() -> str:
    '''
    This amazing comprehensive docstring
    with all the details and examples...
    '''
    # FastMCP IGNORES the docstring!
    # Only sees "Short description"
```

**Result:** Terrible tool discovery, poor AI understanding!

---

## ✅ The Correct Pattern

### For Simple Tools

```python
@mcp.tool
async def simple_tool(name: str) -> str:
    '''Do a simple operation.
    
    Args:
        name: The name to process
        
    Returns:
        Processed result
        
    Example:
        simple_tool("test")
    '''
    return f"Processed: {name}"
```

### For Complex Tools (Portmanteau)

```python
from typing import Literal

@mcp.tool
async def portmanteau_tool(
    operation: Literal["create", "read", "update", "delete"],
    identifier: str | None = None,
    data: dict | None = None,
) -> str:
    '''Comprehensive tool that does multiple related operations.
    
    SUPPORTED OPERATIONS:
    - create: Create new resource
    - read: Retrieve resource
    - update: Modify resource
    - delete: Remove resource
    
    OPERATIONS DETAIL:
    
    create: Initialize new resource
    - Parameters: identifier (required), data (required)
    - Returns: Created resource confirmation
    - Example: portmanteau_tool("create", identifier="test", data={...})
    
    read: Retrieve resource
    - Parameters: identifier (required)
    - Returns: Full resource data
    - Example: portmanteau_tool("read", identifier="test")
    
    update: Modify existing resource
    - Parameters: identifier (required), data (required)
    - Returns: Update confirmation
    - Example: portmanteau_tool("update", identifier="test", data={...})
    
    delete: Remove resource
    - Parameters: identifier (required)
    - Returns: Deletion confirmation
    - Example: portmanteau_tool("delete", identifier="test")
    
    Args:
        operation: The operation to perform (create/read/update/delete)
        identifier: Resource identifier
        data: Resource data for create/update operations
        
    Returns:
        Operation-specific result with status and details
        
    Examples:
        # Create
        portmanteau_tool("create", identifier="new-resource", data={"key": "value"})
        
        # Read
        portmanteau_tool("read", identifier="existing-resource")
        
        # Update
        portmanteau_tool("update", identifier="resource", data={"updated": "value"})
        
        # Delete
        portmanteau_tool("delete", identifier="resource")
    '''
    # Implementation
```

---

## 🔧 Migration Steps

### Step 1: Identify Tools with description=

```bash
# Find all tools with description parameter
grep -r "@mcp.tool(" src/ -A 2 | grep "description="
```

### Step 2: Run Automated Fix

Copy `scripts/remove_description_params.py` from advanced-memory-mcp:

```bash
# From advanced-memory-mcp
cp scripts/remove_description_params.py ../your-repo/scripts/

# Run it
cd ../your-repo
python scripts/remove_description_params.py
```

**Script automatically:**
- Removes `description=` parameter
- Preserves tool name if using `@mcp.tool("custom-name")`
- Keeps docstrings intact
- Safe (regex-based, tested)

### Step 3: Enhance Docstrings

**For each tool, ensure docstring has:**
- [ ] Purpose statement
- [ ] Args section with types
- [ ] Returns section with format
- [ ] Examples section (at least 2)
- [ ] Notes/warnings if applicable

**For portmanteau tools, also include:**
- [ ] SUPPORTED OPERATIONS section
- [ ] OPERATIONS DETAIL section (each operation documented)
- [ ] Examples for EACH operation

### Step 4: Use Single Quotes

```python
# ❌ BAD (can cause nesting issues)
@mcp.tool
async def my_tool() -> str:
    """Docstring with potential "nested" 'quote' issues"""
    
# ✅ GOOD (no nesting issues)
@mcp.tool
async def my_tool() -> str:
    '''Docstring with safe "nested" 'quote' handling'''
```

### Step 5: Verify

```bash
# Check no description= remains
grep -r "description=" src/ | grep "@mcp.tool"

# Should return NOTHING!

# Lint
ruff check src/

# Test imports
python -c "from your_package.mcp.tools import tool_name; print('✅')"
```

---

## 📋 Checklist for Each Tool

### Minimum (All Tools)

- [ ] No `description=` parameter in `@mcp.tool()`
- [ ] Docstring exists (not just pass)
- [ ] Purpose clearly stated
- [ ] Args documented with types
- [ ] Returns documented
- [ ] At least 1 example

### Recommended (Quality)

- [ ] Single quote docstrings `'''`
- [ ] Multiple examples
- [ ] Edge cases noted
- [ ] Error conditions documented
- [ ] Related tools mentioned

### Excellent (Portmanteau)

- [ ] SUPPORTED OPERATIONS section
- [ ] Each operation detailed (200+ lines total)
- [ ] Parameters for EACH operation
- [ ] Returns for EACH operation
- [ ] Examples for EACH operation
- [ ] Usage patterns explained

---

## 🎯 Quality Targets

### Tool Docstring Length Guidelines

**Simple tool (single operation):**
- Minimum: 50 lines
- Recommended: 80-100 lines
- Excellent: 120+ lines

**Complex tool (portmanteau):**
- Minimum: 150 lines
- Recommended: 200-300 lines
- Excellent: 400+ lines (like adn_content, adn_skills)

### What to Include

**Always:**
1. Purpose statement (1-2 paragraphs)
2. Args section (every parameter)
3. Returns section (format + examples)
4. Examples section (2-3 examples)

**For Portmanteau:**
5. SUPPORTED OPERATIONS list
6. OPERATIONS DETAIL (each operation)
7. Operation-specific examples
8. Usage patterns and workflows

---

## 🔍 Verification Commands

### Check Compliance

```bash
# 1. No description parameters
grep -r "@mcp.tool(" src/ -A 1 | grep "description=" | wc -l
# Should output: 0

# 2. All tools import
python -c "import your_package.mcp.tools; print('✅')"

# 3. Lint clean
ruff check src/

# 4. Tests pass
pytest tests/
```

---

## 📊 Migration Status Tracking

### Repos Migrated to FastMCP 2.12

✅ **advanced-memory-mcp**
- Status: FULLY COMPLIANT
- Tools: 51 total (13 portmanteau + 38 individual)
- description= removed from ALL tools
- Comprehensive docstrings on all tools
- Date: 2025-10-21

**Others:** TBD (use scan script)

### Repos Needing Migration

Run scan script to identify:
```bash
python scripts/scan_repos_for_description.py
```

---

## 💾 Templates & Scripts

### Available in advanced-memory-mcp

**scripts/remove_description_params.py**
- Automated description= removal
- Safe regex-based replacement
- Copy to any repo and run

**FASTMCP_2.12_COMPLIANCE_REPORT.md**
- Verification report template
- Shows what was checked
- Documents compliance status

---

## 🚀 Benefits of Migration

**Better Tool Discovery:**
- FastMCP reads rich docstrings
- AI gets full context
- Better parameter understanding

**Single Source of Truth:**
- Documentation in ONE place (docstring)
- No parameter/docstring conflicts
- Easier to maintain

**Cleaner Code:**
- No multi-line decorator parameters
- Readable tool definitions
- Consistent pattern

**Future-Proof:**
- FastMCP 2.12+ standard
- Matches MCP ecosystem best practices
- Won't need another migration

---

## 📚 Resources

**FastMCP Documentation:**
- https://fastmcp.wiki/
- Tool documentation patterns
- Best practices

**Reference Implementation:**
- advanced-memory-mcp (all tools compliant)
- Check `src/advanced_memory/mcp/tools/` for examples

**Migration Scripts:**
- `scripts/remove_description_params.py`
- `scripts/scan_repos_for_description.py`

---

**Last Updated:** 2025-10-21  
**Review:** When FastMCP updates (check changelog)  
**Owner:** Sandra Schi
