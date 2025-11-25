# Documentation Standards for MCP Projects

**Version:** 1.0  
**Date:** 2025-10-21  
**Status:** Living Document

---

## Purpose

This document defines the documentation standards for all MCP projects in the repository collection. Following these standards ensures:
- Consistent quality across all projects
- Easy discoverability and learning
- Professional presentation
- Community-ready documentation
- FastMCP 2.12+ compliance
- Modern MCPB packaging standards

---

## Core Principles

### 1. Complete
- Document all features, not just the "main" ones
- No "TODO: document this" placeholders in public docs
- Cover basic to advanced usage

### 2. Clear
- Write for your target audience (users, developers, contributors)
- Use concrete examples, not abstract descriptions
- Progressive disclosure (simple first, advanced later)

### 3. Correct
- Keep docs synchronized with code
- Test all examples before committing
- Update docs when features change
- Specify version compatibility

### 4. Consistent
- Use standard structure across all repos
- Use same terminology throughout
- Apply same quality standards everywhere

### 5. Discoverable
- Good navigation and linking
- Clear table of contents for long docs
- Searchable content
- Proper headings hierarchy

### 6. Professional
- No rough drafts in public docs (use docs-private/)
- Proper grammar and spelling
- Good markdown formatting
- Appropriate tone

---

## Integration Definition

### What is an "Integration"?

**An "Integration" is an application or service that we control via MCP servers.**

This includes:
- **Media Applications**: Plex, Calibre, Immich
- **Creative Software**: Blender, GIMP, Unity 3D, VRChat, Reaper
- **Development Tools**: Notepad++, Typora
- **System Tools**: HandBrake, Virtual DJ, rTorrent
- **Infrastructure**: Tailscale, virtualization platforms
- **Any application** that can be automated and controlled programmatically

### What is NOT an Integration?

- **Development Tools**: Ruff, Semgrep, Mypy (these are development tools, not integrations)
- **Build Tools**: UV, pip, npm (these are build/packaging tools)
- **Testing Tools**: pytest, coverage (these are testing tools)
- **CI/CD Tools**: GitHub Actions, Docker (these are deployment tools)

### Integration Documentation Standards

All integration MCP servers must document:
- **Application Overview**: What the application does
- **MCP Server Purpose**: How the MCP server controls the application
- **Installation Requirements**: Prerequisites and setup
- **Configuration**: Environment variables and settings
- **Tool Documentation**: Complete API reference for all tools
- **Usage Examples**: Practical examples of common tasks
- **Troubleshooting**: Common issues and solutions

---

## FastMCP 2.12+ Compliance Standards

### Tool Documentation Requirements

**All MCP servers MUST use FastMCP 2.12+ tool documentation standards:**

#### ✅ Correct Tool Documentation Format
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

#### ❌ Prohibited Patterns
- **NO** `@mcp.tool(description="...")` decorators
- **NO** basic docstrings without comprehensive documentation
- **NO** incomplete parameter documentation
- **NO** missing return value documentation

### MCPB Packaging Standards

**All MCP servers MUST use MCPB packaging:**

#### Required Files
- `manifest.json` - MCPB manifest configuration
- `assets/` directory - Icons, screenshots, prompts
- `pyproject.toml` - Python project configuration
- `requirements.txt` - Runtime dependencies

#### Manifest Requirements
```json
{
  "manifest_version": "0.2",
  "server": {
    "type": "python",
    "entry_point": "src/package_name/mcp_server.py",
    "mcp_config": {
      "command": "python",
      "args": ["-m", "package_name.mcp_server"]
    }
  }
}
```

### Portmanteau Pattern Standards

**For feature-rich MCP servers, use the Portmanteau Pattern:**

#### Benefits
- Prevents tool explosion (60+ tools → 10 portmanteau tools)
- Improves discoverability
- Better user experience
- Easier maintenance

#### Implementation
- Group related operations into single tools
- Use operation parameter to specify actions
- Provide comprehensive documentation for each operation
- Include usage examples for all operations

---

## Required Documentation Files

### Every MCP Repository MUST Have:

**1. README.md** (Root)
```markdown
# Project Name

Brief 1-2 sentence description.

## Features
- Key feature 1
- Key feature 2
- Key feature 3

## Installation
[Step-by-step instructions]

## Quick Start
[Copy-paste example]

## Documentation
- [Integration Guide](docs/integration-guide.md)
- [Architecture](docs/architecture.md)
- [API Reference](docs/tools-reference.md)

## License
[License info]
```

**2. CHANGELOG.md** (Root)
```markdown
# Changelog

## [Version] - YYYY-MM-DD
### Added
### Changed
### Fixed
### Removed
```

**3. LICENSE** (Root)
- Choose appropriate license (MIT, Apache, etc.)

**4. docs/** (Directory)
- Organized documentation
- Clear structure by topic

---

## MCP Server Documentation Structure

### For FastMCP 2.12+ Servers:

```
repo-name/
├── README.md (overview, quick start)
├── CHANGELOG.md (version history)
├── LICENSE
├── docs/
│   ├── integration-guide.md (Claude Desktop setup)
│   ├── architecture.md (system design)
│   ├── tools-reference.md (complete tool list)
│   ├── configuration.md (settings, env vars)
│   ├── troubleshooting.md (common issues)
│   └── examples/ (working examples)
└── docs-private/ (internal dev notes - git-ignored)
```

### Additional for Portmanteau Servers:

```
docs/
├── portmanteau-pattern/ (if using pattern)
│   ├── CONCEPT.md (what it is)
│   ├── TOOL_MODE_CONFIGURATION.md (switching modes)
│   └── WHAT_CLAUDE_SEES.md (discoverability)
```

---

## Documentation Templates

### README.md Template

```markdown
# {Project Name}

{1-2 sentence description of what it does}

## ✨ Features

- {Key feature 1}
- {Key feature 2}
- {Key feature 3}

## 📦 Installation

### Prerequisites
- {Requirement 1}
- {Requirement 2}

### Install via {package manager}
\`\`\`bash
{installation commands}
\`\`\`

## 🚀 Quick Start

\`\`\`json
{
  "mcpServers": {
    "{server-name}": {
      "command": "{command}",
      "args": ["{args}"]
    }
  }
}
\`\`\`

## 📚 Documentation

- [Integration Guide](docs/integration-guide.md) - Setup with Claude Desktop
- [Architecture](docs/architecture.md) - How it works
- [Tool Reference](docs/tools-reference.md) - Complete API
- [Examples](docs/examples/) - Working examples

## 🔧 Configuration

{Brief config info, link to docs/configuration.md}

## 🤝 Contributing

{Link to CONTRIBUTING.md or brief guidelines}

## 📄 License

{License info}

---

**Status:** {Production/Beta/Alpha}  
**MCP Version:** FastMCP {version}  
**Maintained by:** {Name}
```

---

## FastMCP 2.12 Specific Standards

### For Portmanteau Tools:

**REQUIRED:**
1. ✅ Use `Literal` types for action parameters
2. ✅ Use `@mcp.tool()` WITHOUT description parameter
3. ✅ Write comprehensive docstrings (200+ lines for complex tools)
4. ✅ Document ALL sub-operations in docstring
5. ✅ Provide examples for each operation
6. ✅ Check imports (no circular dependencies)
7. ✅ Run ruff before committing

**Example:**
```python
from typing import Literal
from fastmcp import FastMCP

@mcp.tool()  # No description parameter!
async def category_management(
    action: Literal["op1", "op2", "op3"],  # Required!
    param: str | None = None
) -> dict:
    '''
    Complete description of tool purpose.
    
    Args:
        action: Available operations:
            - op1: Full description with requirements
            - op2: Full description with requirements  
            - op3: Full description with requirements
        param: Parameter description
        
    Returns:
        Dictionary with success, result, error
        
    Examples:
        # Example for op1
        result = await category_management(action="op1")
        
        # Example for op2
        result = await category_management(action="op2", param="value")
    '''
    # Implementation
```

---

## Integration Guide Template

**docs/integration-guide.md:**

```markdown
# Integration Guide - {Project Name}

## Claude Desktop Setup

### 1. Installation

{Installation steps}

### 2. Configuration

Edit your Claude Desktop config:

\`\`\`json
{
  "mcpServers": {
    "{server-name}": {
      "command": "{command}",
      "args": ["{args}"],
      "env": {
        "{ENV_VAR}": "{value}"
      }
    }
  }
}
\`\`\`

### 3. Verification

Restart Claude Desktop and ask:
"{test query}"

Expected response: {what to expect}

## First Steps

### Basic Operations

{3-5 common operations with examples}

### Common Use Cases

{3-5 use case scenarios}

## Troubleshooting

{Common issues and solutions}
```

---

## Architecture Documentation Template

**docs/architecture.md:**

```markdown
# Architecture - {Project Name}

## Overview

{System overview diagram or description}

## Components

### {Component 1}
- **Purpose:** {what it does}
- **Dependencies:** {what it needs}
- **Key Files:** {relevant files}

### {Component 2}
...

## Tool Organization

{How tools are organized, if portmanteau explain that}

## Data Flow

{How data flows through the system}

## Extension Points

{How to extend or customize}

## Dependencies

{Key dependencies and why}
```

---

## Tool Reference Template

**docs/tools-reference.md:**

```markdown
# Tool Reference - {Project Name}

## Tool List

### {tool_name}

**Description:** {what it does}

**Parameters:**
- `param1` (type, required/optional): {description}
- `param2` (type, required/optional): {description}

**Returns:**
\`\`\`json
{
  "success": true,
  "result": {example}
}
\`\`\`

**Example:**
\`\`\`python
result = await tool_name(param1="value")
\`\`\`

**Notes:**
- {Important note 1}
- {Important note 2}

---

{Repeat for each tool}
```

---

## Quality Checklist

### Before Marking Docs as "Complete":

**README.md:**
- [ ] Clear 1-2 sentence description
- [ ] Features list
- [ ] Installation instructions work (tested!)
- [ ] Quick start example works (tested!)
- [ ] Links to detailed docs
- [ ] License info

**CHANGELOG.md:**
- [ ] Exists
- [ ] Last 3+ versions documented
- [ ] Follows semantic versioning

**docs/integration-guide.md:**
- [ ] Claude Desktop config shown
- [ ] First steps clear
- [ ] Common operations documented
- [ ] Troubleshooting section

**docs/architecture.md:**
- [ ] Components explained
- [ ] Data flow clear
- [ ] Dependencies listed

**docs/tools-reference.md:**
- [ ] All tools documented
- [ ] Parameters explained
- [ ] Return values shown
- [ ] Examples provided

**General:**
- [ ] No TODOs in public docs
- [ ] All examples tested
- [ ] Links work
- [ ] Grammar/spelling checked
- [ ] Formatted properly
- [ ] Up-to-date with code

---

## Public vs Private Documentation

### docs/ (Public - on GitHub)
**Include:**
- User-facing documentation
- Architecture and design
- Integration guides
- API reference
- Polished, professional content

### docs-private/ (Private - git-ignored)
**Include:**
- Progress reports
- Debug notes
- Bloopers and mistakes
- Scratch work
- Internal planning
- WIP documentation

**Rule:** If it's rough or just for you → docs-private/  
If it helps others → polish and put in docs/

---

## Maintenance

### Documentation is NOT "done once"

**When adding features:**
- [ ] Update relevant docs
- [ ] Add examples
- [ ] Update CHANGELOG

**When fixing bugs:**
- [ ] Update docs if behavior changed
- [ ] Add to troubleshooting if common issue

**Regular reviews (monthly):**
- [ ] Check all examples still work
- [ ] Update for version changes
- [ ] Fix broken links
- [ ] Improve clarity based on questions

---

## Success Criteria

**Good Documentation (7-8/10):**
- All required files present
- Installation and quick start work
- Main features documented
- Examples provided

**Excellent Documentation (9-10/10):**
- Comprehensive coverage
- Multiple examples per feature
- Architecture explained
- Troubleshooting guide
- Contributes to community
- Used as reference by others

---

**Version History:**
- 1.0 (2025-10-21): Initial standards based on virtualization-mcp

**Review Schedule:** Quarterly

**Owner:** Sandra Schi

