# Agent2Agent (A2A) Protocol — Fleet briefing

**Audience:** Operators and implementers of our MCP server fleet (e.g. PlexMCP, shared FastMCP transport, HTTP/stdio modes).  
**Purpose:** Single “MCP central” reference for what A2A is, how it relates to MCP, maturity, backers, adoption signals, and when to adopt it.  
**Last reviewed:** 2026-04-22 (sources cited below; verify periodically).

**Fleet execution order (Plex → Calibre → Memory → supervisors):** [A2A_FLEET_ROLLOUT_PLAN.md](A2A_FLEET_ROLLOUT_PLAN.md).

---

## 1. Executive summary

**Agent2Agent (A2A)** is an open standard for **peer agents** to discover each other, exchange structured work as **tasks**, and coordinate over ordinary web infrastructure (HTTP, JSON-RPC 2.0, optional streaming). It is **orthogonal to MCP**: MCP standardizes **model ↔ tools/data/context**; A2A standardizes **agent ↔ agent** delegation and lifecycle.

For our fleet, the practical picture is:

- Keep **MCP** as the primary surface for IDE hosts (Cursor, Claude Desktop, Windsurf) and for tool execution.
- Add **A2A** only where we need **machine-to-machine agent delegation** across services (orchestrator calling a specialist agent over the network, long-running jobs with status, push callbacks).

Do **not** treat blog summaries or conference demos as normative; implement against the **official specification** and version headers your chosen stack expects.

---

## 2. What the standard specifies (conceptual)

Normative material lives in the open project repository (specification, protobuf, JSON bindings). At a high level, implementers care about:

| Area | Role |
|------|------|
| **Agent card** | JSON metadata describing the agent (capabilities, auth, endpoints). Commonly advertised at **`/.well-known/agent.json`** so clients can discover the agent without bespoke config. |
| **Task model** | Work is framed as tasks with a **lifecycle** (e.g. submitted → working → completed / failed / canceled — exact states and fields are defined in the spec). |
| **JSON-RPC binding** | JSON-RPC 2.0 over HTTP(S); methods for sending work, querying status, cancellation, and optional streaming / push-style notification flows (see spec for exact method names and parameters for your protocol version). |
| **Versioning** | Clients and servers negotiate supported **A2A protocol versions** (e.g. via headers such as `A2A-Version` in the JSON-RPC binding). Breaking evolution is expected to be managed like any young standard. |
| **Opacity** | Agents interact as **black boxes**: collaboration does not require exposing internal memory, prompts, or proprietary tool graphs. |

**Fleet note:** Internal method names you may see in informal writeups (e.g. `a2a.sendMessage`) may **not** match the public JSON-RPC method catalog. Always align with the **specification for the version you ship**.

---

## 3. A2A and MCP — complementary, not competing

Google’s launch messaging explicitly positions A2A as **complementing** Anthropic’s **Model Context Protocol (MCP)**:

- **MCP:** Universal connector for **tools, resources, prompts**, sampling, and host-managed sessions — ideal for assistant/IDE integration.
- **A2A:** **Inter-agent** interoperability — discovery, task delegation, status, streaming/push across independently deployed agents.

**Our default architecture:** MCP remains the “tool bridge.” A2A becomes an optional **HTTP façade** in front of the same business logic (adapter pattern: A2A message → MCP tool call → artifact mapping), not a rewrite of FastMCP internals.

---

## 4. Who is behind it (governance and sponsors)

### 4.1 Launch and intent

- **Announced April 9, 2025** on the Google Developers Blog: [Announcing the Agent2Agent Protocol (A2A)](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability).
- Described as **open source**, developed with a broad partner list, with a stated goal of a **production-hardened** specification in collaboration with partners (timeline language was forward-looking at launch — treat dates in old posts as historical context).

### 4.2 Linux Foundation and TSC

The project operates under **Linux Foundation** style open governance (meetings, antitrust, contribution licensing). The public **`GOVERNANCE.md`** in the main repository lists a **Technical Steering Committee (TSC)** with representatives from major vendors — as of the governance file in the repo, seats include **Google, Microsoft, Cisco, Amazon Web Services, Salesforce, SAP**, and related roles (verify the live file for the current roster):

- [A2A `GOVERNANCE.md` (TSC composition)](https://github.com/a2aproject/A2A/blob/main/GOVERNANCE.md)

### 4.3 Partner ecosystem

Google maintains a public **partners** page (technology vendors, consultancies, and platform companies). It is useful for **adoption signaling**, not for technical guarantees:

- [A2A partners (official listing)](https://google.github.io/A2A/partners/)

Examples frequently cited alongside the launch include enterprise software and cloud names (e.g. Atlassian, Salesforce, SAP, ServiceNow, MongoDB, LangChain, and many systems integrators). The list changes; link beats a static copy here.

---

## 5. Maturity: “fully baked” or still moving?

**Verdict for fleet planning:** **Maturing standard, not a frozen POSIX.** Use it with **pinned protocol versions**, contract tests, and an adapter layer.

Evidence:

- The **official roadmap** (last updated **2026-03-10** at time of writing) describes a **1.0** release as representing **maturation**, clearer specification, and structural improvements — i.e. the project itself frames pre-1.0 evolution as normal:
  - [A2A protocol roadmap](https://a2a-protocol.org/dev/roadmap)
- Launch blog described an initial **specification draft** and path toward **production-ready** iterations — appropriate for **pilot** and **controlled production**, not for “set and forget for 10 years” without upgrade discipline.
- **SDKs** are officially multi-language (Python, Go, JavaScript/TypeScript, Java, .NET per project communications and roadmap pages).

**Operational implication:** Treat A2A like **HTTP APIs in 2010** — real deployments exist, but **version negotiation**, **deprecation windows**, and **compatibility tests** are mandatory for a serious fleet.

---

## 6. Uptake among Anthropic and other large players

### 6.1 Anthropic

- **MCP** remains Anthropic’s flagship open standard for **context and tools** (originated by Anthropic; broad IDE and host adoption).
- Anthropic has publicly **co-presented** with Google Cloud on **deploying multi-agent systems using MCP and A2A** (recorded partner webinar, **August 27, 2025**), which is a strong signal that Anthropic sees **A2A as complementary infrastructure** in cloud multi-agent topologies — not as an MCP replacement:
  - [Deploying multi-agent systems using MCP and A2A with Claude on Vertex AI (Anthropic webinars)](https://www.anthropic.com/webinars/deploying-multi-agent-systems-using-mcp-and-a2a-with-claude-on-vertex-ai)

**Do not infer** from marketing pages alone that every Anthropic product surface (e.g. Claude Desktop) will natively speak A2A tomorrow; treat **MCP as the near-universal host integration** and A2A as **optional cross-service** glue.

### 6.2 Microsoft, AWS, Google

TSC membership and cloud documentation indicate **serious vendor investment** in A2A as a **coordination layer** for agents on their platforms. For fleet design, that matters for **longevity** and **SDK maintenance**, not for assuming identical semantics across clouds without testing.

### 6.3 OpenAI and others

The landscape is **fragmented by framework** (OpenAI Agents SDK, Google ADK, LangGraph, CrewAI, etc.). Third-party surveys in **2026** still often note **narrow native A2A coverage** outside Google-centric stacks, with **MCP support wider** among agent frameworks. Treat such surveys as **directional** unless backed by release notes you verify.

---

## 7. Official information sites and repositories

| Resource | URL | Notes |
|----------|-----|--------|
| **Project docs site** | https://a2a-protocol.org/ | Official documentation hub (topics, roadmap, governance links). |
| **GitHub organization / spec** | https://github.com/a2aproject/A2A | Specification, samples, governance, issue tracker. |
| **Google-hosted A2A site** | https://google.github.io/A2A/ | Partners, introductory material. |
| **Launch narrative** | https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability | Historical context and partner quotes. |

### 7.1 Samples and learning paths

Start from the **`a2aproject/A2A`** repository: sample agents, demo hosts, and specification artifacts are maintained there. Prefer **first-party samples** over random tutorials when validating wire formats.

### 7.2 Third-party documentation (use with care)

Sites such as **a2a.plus**, **a2aprotocol.ai**, and generic “Python A2A” packages may be **helpful for learning** but can **lag or diverge** from the normative spec. For fleet implementations:

- **Trust order:** `a2aproject/A2A` spec → official SDKs → vendor integration guides → community blogs.

---

## 8. Pros and cons (honest fleet view)

### Pros

- **Standardized discovery** via agent cards reduces bespoke integration between teams.
- **Task lifecycle** fits **long-running** automation (indexing, transcoding orchestration, batch enrichment) better than cramming everything into a single MCP request-response.
- **Streaming / push patterns** (per spec) reduce naive polling for slow jobs.
- **Vendor-neutral ambition** backed by **LF governance** and a **multi-vendor TSC** — better than each internal service inventing its own “agent HTTP API.”
- **Complements MCP** instead of forcing a rewrite of existing MCP servers.

### Cons and risks

- **Young standard:** Versioning and method names evolve; **upgrade tax** is real.
- **Two surfaces to secure:** MCP (often local or trusted network) + A2A (HTTP, broader attack surface) requires **authn/z**, rate limits, and audit logging.
- **Not observability:** A2A standardizes **interaction**, not traces/metrics. Production fleets still need **OpenTelemetry** (or equivalent), structured logs, and cost controls — community commentary correctly stresses “A2A is not enough” for serious operations (e.g. discussion of OTel + protocols in industry posts).
- **Framework gaps:** Outside Google-aligned stacks, **end-to-end A2A** may require **custom adapters** (exactly what we’d build around FastMCP).
- **Spec vs hype:** Conference demos and social posts may show **flags or shorthand** that are not the canonical wire protocol — implementors must ignore that noise.

---

## 9. Usage patterns for **our** MCP fleet members

These patterns assume servers already expose **MCP** (stdio or HTTP via FastMCP).

| Pattern | When to use A2A | MCP alone |
|---------|-----------------|-----------|
| **IDE / assistant driven** | Usually **no** | Yes — host speaks MCP. |
| **Service-to-service delegation** | **Yes** — publish agent card + JSON-RPC endpoint behind auth | Possible but ad hoc unless you standardize. |
| **Long-running jobs with status** | **Yes** — task store + `tasks/get` (names per version) + optional push | MCP can stream in some hosts; cross-network status is still custom without A2A. |
| **Public “agent marketplace”** | **Maybe later** — needs registry, trust, SLAs | MCP catalogs (e.g. Glama) solve **distribution**, not agent negotiation. |

**Recommended rollout for fleet:**

1. **Design** agent card **skills** to map 1:1 to stable, documented MCP tool operations (thin adapter).
2. **Pin** `A2A-Version` / protocol version per deployment; record in runbooks.
3. **Pilot** one HTTP-enabled fleet member (same host/port or reverse proxy path) with **composite ASGI**: MCP app + `/.well-known/agent.json` + A2A RPC route.
4. **Add** integration tests that **golden-file** JSON-RPC request/response shapes against the pinned spec version.
5. **Layer** observability (trace IDs on tasks, log correlation with MCP `call_tool`).

---

## 10. Community and industry reactions (balanced)

**Positive themes**

- Relief at a **credible attempt** to standardize **agent-to-agent** traffic instead of N custom REST dialects.
- Appreciation that A2A **explicitly complements MCP** rather than declaring MCP obsolete.
- Enterprise-friendly framing (auth, multi-tenant concerns in later spec work).

**Skeptical / constructive themes**

- “**Another protocol**” fatigue — teams demand clarity on **when A2A pays for its complexity** vs internal gRPC/REST.
- Reminders that **interoperability ≠ reliability**: without **observability**, policy, and evaluation harnesses, A2A alone does not make multi-agent systems production-safe (see e.g. developer-community essays on observable multi-agent systems in 2026).
- **Tutorial ecosystem quality** varies; some articles use **incorrect method names** — always diff against the spec.

---

## 11. FAQ

**Is A2A a replacement for MCP?**  
No. Different layer: MCP for **tools/context**; A2A for **agent collaboration**.

**Should every MCP server in the fleet expose A2A?**  
No. Add A2A only to servers that are **peers** on the network or need **standard cross-team delegation**.

**Is the Google blog’s partner list normative?**  
It’s **marketing and ecosystem signaling**, not a technical conformance list.

**Where do we file bugs or spec questions?**  
The **`a2aproject/A2A`** GitHub issues and TSC processes per `GOVERNANCE.md`.

---

## 12. References (bookmark list)

1. Google Developers Blog — *Announcing the Agent2Agent Protocol (A2A)* (2025-04-09): https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability  
2. A2A official documentation: https://a2a-protocol.org/  
3. A2A roadmap: https://a2a-protocol.org/dev/roadmap  
4. A2A governance / TSC: https://github.com/a2aproject/A2A/blob/main/GOVERNANCE.md  
5. A2A GitHub organization: https://github.com/a2aproject/A2A  
6. Google A2A documentation (partners, intro): https://google.github.io/A2A/  
7. Anthropic webinar — *MCP and A2A with Claude on Vertex AI* (2025-08-27): https://www.anthropic.com/webinars/deploying-multi-agent-systems-using-mcp-and-a2a-with-claude-on-vertex-ai  
8. Anthropic — *Introducing the Model Context Protocol* (MCP origin, 2024-11-25): https://www.anthropic.com/news/model-context-protocol  

---

*This document is fleet guidance for the plex-mcp repository. It is not legal advice and not an official statement of the A2A project.*
