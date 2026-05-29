# Step 6C: Remote MCP HTTP Client Placeholder

## Goal

Add a dedicated placeholder for the future remote MCP HTTP transport.

We do not make real network calls yet. The point is to create the correct replacement point without pretending remote execution works.

## What Changed

- Added `RemoteMcpHttpClient`.
- Updated `RemoteMcpExecutor` to build a remote envelope and call the HTTP client.
- The HTTP client raises a clear not-implemented exception until real transport is added.

## Why This Matters

Remote execution is a high-impact enterprise boundary. It should be introduced deliberately, with explicit configuration, tests, errors, and observability.

## Interview Talking Point

I added the transport boundary before implementing the transport. That keeps the architecture honest and gives the team a safe place to add authentication, retries, timeout handling, and payload logging later.
