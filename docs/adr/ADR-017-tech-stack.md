# ADR-017: Python 3.13 with uv, numpy, DuckDB, and a single command-line entry point

**Status:** Accepted (design); solver choice in ADR-006. **Date:** 2026-10-13.

**Changelog:** 2026-10-14 (ADJUDICATION entry 3): DuckDB is not an MVP dependency; MVP storage is JSON and Parquet; DuckDB arrives with the learning chunk. The solver choice (ADR-006) is unchanged.

## Context

The engine runs on a Windows 11 laptop (Intel Core Ultra 7 258V, 8 cores, 32 GB RAM with about 6 GB free, Python 3.13 and uv installed, VERIFIED). Claude Code builds and operates it. Your prior engines grew large and slow to test (NHL: 18 to 35 minute test suite; MLB: about 100,000 lines) (RR1, RR3).

## Decision

- **Language and packaging:** Python 3.13 managed by uv (`uv run dfs ...`), one package `nbadfs`, one CLI entry point (Typer).
- **Numerics:** numpy (counter-based random generators for determinism), scipy for distributions.
- **Tables and storage:** pandas for file I/O, DuckDB for the engine database, Parquet for arrays.
- **Schemas:** pydantic models for every file format, LLM record, and configuration.
- **Solver:** see ADR-006.
- **PDF parsing:** pdfplumber for the injury report.
- **HTTP:** httpx with a per-host rate limiter and the snapshot store.
- **Tests:** pytest plus property tests; smoke under 60 seconds, full suite under 5 minutes.
- **No services:** no database server, no web app, no cloud (nba-betting-system stopped on a database password, RR4).

## Consequences

- **Results:** none directly.
- **Cost:** all free and open source.
- **Workload:** one-time `uv sync`; nothing to keep running between nights except the optional news watcher.
