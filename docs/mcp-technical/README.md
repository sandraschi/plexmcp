# 🔧 MCP Technical Documentation

**Technical guides for MCP server development, deployment, and troubleshooting**

---

## 📚 **Documentation Index**

### **1. Claude Desktop Debugging**
📄 [CLAUDE_DESKTOP_DEBUGGING.md](CLAUDE_DESKTOP_DEBUGGING.md)

**Debug MCP servers in Claude Desktop**
- Log file locations
- Common errors
- Debugging techniques
- Connection issues
- stdio protocol troubleshooting

---

### **2. MCP Production Checklist**
📄 [MCP_PRODUCTION_CHECKLIST.md](MCP_PRODUCTION_CHECKLIST.md)

**Comprehensive production readiness checklist**
- Code quality requirements
- Testing standards
- Documentation requirements
- Security considerations
- Performance benchmarks
- Deployment checklist

---

### **3. FastMCP 2.12 Troubleshooting**
📄 [TROUBLESHOOTING_FASTMCP_2.12.md](TROUBLESHOOTING_FASTMCP_2.12.md)

**FastMCP-specific issues and solutions**
- Version compatibility
- Common errors
- Configuration issues
- Tool registration problems
- stdio protocol issues

---

### **4. Containerization Guidelines**
📄 [CONTAINERIZATION_GUIDELINES.md](CONTAINERIZATION_GUIDELINES.md)

**Docker and containerization for MCP servers**
- Docker best practices
- Container configuration
- Deployment strategies
- Security considerations
- Performance optimization

---

### **5. Monitoring Stack Deployment**
📄 [MONITORING_STACK_DEPLOYMENT.md](MONITORING_STACK_DEPLOYMENT.md)

**Production monitoring and observability**
- Logging infrastructure
- Metrics collection
- Error tracking
- Performance monitoring
- Alert configuration

---

### **6. A2A Protocol (Agent2Agent) — Fleet briefing**
📄 [A2A_PROTOCOL_FLEET_BRIEFING.md](A2A_PROTOCOL_FLEET_BRIEFING.md)

**Google / Linux Foundation Agent2Agent standard next to MCP**
- What A2A specifies (agent cards, tasks, JSON-RPC) vs MCP
- Governance, partners, maturity and versioning
- Anthropic and ecosystem uptake (with citations)
- Pros, cons, fleet rollout patterns, official links and samples

---

### **7. A2A fleet rollout plan (Plex → Calibre → Memory → supervisors)**
📄 [A2A_FLEET_ROLLOUT_PLAN.md](A2A_FLEET_ROLLOUT_PLAN.md)

**Phased adoption across fleet repos + mcp-central-docs alignment**
- Phase 1 **plex-mcp** (reference A2A server)
- Phase 2 **calibre-mcp** (HTTP readiness checklist, then A2A)
- Phase 3 **advanced-memory-mcp** (horizontal A2A agent)
- Phase 4 **meta-mcp** / **universal-actuator-mcp** (supervisor as A2A client; optional inbound A2A)

---

## 🎯 **Purpose**

This directory contains **MCP server technical documentation** including:

✅ **MCP Protocol** - Implementation details  
✅ **FastMCP Framework** - Version 2.12+ specifics  
✅ **Claude Desktop** - Integration and debugging  
✅ **Production Deployment** - Checklists and guidelines  
✅ **Troubleshooting** - Common issues and fixes  
✅ **Monitoring** - Observability and logging  
✅ **A2A (Agent2Agent)** - Complementary agent-to-agent standard (fleet briefing)  
✅ **A2A rollout** - Plex → Calibre → Memory → supervisor MCPs ([plan](A2A_FLEET_ROLLOUT_PLAN.md))

---

## 👥 **Target Audience**

- **MCP Server Developers** - Building MCP servers
- **DevOps Engineers** - Deploying MCP servers
- **System Administrators** - Managing MCP infrastructure
- **Technical Support** - Troubleshooting MCP issues
- **Contributors** - Understanding the stack

---

## 🔧 **Key Topics Covered**

### **MCP Protocol**
- stdio transport
- Tool registration
- Resource handling
- Prompt templates
- Error responses

### **FastMCP Framework**
- Version 2.12+ requirements
- Tool decorators
- Async/await patterns
- Error handling
- Logging integration

### **Claude Desktop Integration**
- Configuration (`claude_desktop_config.json`)
- Log file analysis
- Connection troubleshooting
- stdio communication
- Path resolution

### **Production Deployment**
- Quality checklist
- Security hardening
- Performance optimization
- Monitoring setup
- Container deployment

---

## 📋 **Quick Reference**

| Need | Document | Time |
|------|----------|------|
| **Debug Claude** | [Claude Desktop Debugging](CLAUDE_DESKTOP_DEBUGGING.md) | 15 min |
| **Go to production** | [Production Checklist](MCP_PRODUCTION_CHECKLIST.md) | 20 min |
| **FastMCP issues** | [FastMCP Troubleshooting](TROUBLESHOOTING_FASTMCP_2.12.md) | 10 min |
| **Containerize** | [Containerization](CONTAINERIZATION_GUIDELINES.md) | 20 min |
| **Monitor** | [Monitoring Stack](MONITORING_STACK_DEPLOYMENT.md) | 15 min |
| **A2A + MCP** | [A2A fleet briefing](A2A_PROTOCOL_FLEET_BRIEFING.md) | 25 min |
| **A2A rollout** | [Fleet rollout plan](A2A_FLEET_ROLLOUT_PLAN.md) | 15 min |

---

## 🏆 **Production Readiness**

**Our MCP server achieves**:
- ✅ FastMCP 2.12+ compliance
- ✅ Zero print statements (stdio safe)
- ✅ Structured logging
- ✅ Comprehensive error handling
- ✅ All tests passing
- ✅ Production checklist complete
- ✅ Gold Status (90/100)

**Reference**: These docs guided us to Gold++ status!

---

## 🚨 **Common Issues**

### **MCP Server Won't Start**

**Check**:
1. Log files in `%APPDATA%\Claude\logs\`
2. Python path configuration
3. FastMCP version (must be >=2.12.0)
4. stdio protocol compliance

**Document**: [Claude Desktop Debugging](CLAUDE_DESKTOP_DEBUGGING.md)

---

### **Tools Not Appearing**

**Check**:
1. Tool registration (FastMCP decorators)
2. Server connection
3. Configuration file syntax
4. Tool function signatures

**Document**: [FastMCP Troubleshooting](TROUBLESHOOTING_FASTMCP_2.12.md)

---

### **Performance Issues**

**Check**:
1. Async/await implementation
2. Blocking operations
3. Memory leaks
4. Log file growth

**Document**: [Production Checklist](MCP_PRODUCTION_CHECKLIST.md)

---

## 📊 **Technical Stack**

### **Core Technologies**

- **MCP Protocol** - Model Context Protocol
- **FastMCP** - Python MCP framework (v2.12+)
- **Python** - 3.10+ with async/await
- **stdio** - Standard input/output transport
- **JSON-RPC** - Message format

### **Platform Integration**

- **Claude Desktop** - Primary client
- **Windows API** - Native integration (pywin32)
- **Notepad++** - Target application
- **GitHub Actions** - CI/CD
- **Docker** - Optional containerization

---

## 🔗 **Related Documentation**

### **In This Repository**

- [Development Docs](../development/README.md) - Development practices
- [MCPB Packaging](../mcpb-packaging/README.md) - Distribution
- [Repository Protection](../repository-protection/README.md) - Safety
- [Documentation Index](../DOCUMENTATION_INDEX.md) - All docs

### **External Resources**

- [MCP Specification](https://modelcontextprotocol.io)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Claude Desktop Docs](https://claude.ai/docs)
- [Python async/await](https://docs.python.org/3/library/asyncio.html)
- [A2A Protocol docs](https://a2a-protocol.org/) · [A2A spec repo](https://github.com/a2aproject/A2A)

---

## 🎯 **For New MCP Developers**

**Start Here**:

1. Read: [MCP Production Checklist](MCP_PRODUCTION_CHECKLIST.md)
2. Setup: Claude Desktop debugging
3. Build: Follow production checklist
4. Test: Use troubleshooting guides
5. Deploy: Containerization or direct

**Expected Time**: 4-8 hours to production-ready MCP server

---

## 🏅 **Quality Standards**

**Our Gold Status checklist enforces**:

- ✅ Zero print() statements
- ✅ Structured logging (stderr)
- ✅ FastMCP 2.12+
- ✅ Comprehensive tests
- ✅ Error handling
- ✅ Type hints
- ✅ Documentation
- ✅ CI/CD pipeline

**See**: [Production Checklist](MCP_PRODUCTION_CHECKLIST.md)

---

*MCP Technical Documentation*  
*Location: `docs/mcp-technical/`*  
*Files: 7*  
*Focus: MCP server development & deployment*  
*Target: Technical developers & DevOps*

**Master MCP server development!** 🔧✨

