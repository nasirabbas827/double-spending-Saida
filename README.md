# Double Spending Saida

double-spending-Saida is a local blockchain simulation for exploring double-spending scenarios.

![Flask](https://img.shields.io/badge/Flask-2563EB?style=flat-square)

## Overview

The Flask implementation is organized around the entry points and modules below.

## Implemented workflows

The source defines these handlers:

- **Index** — `index`
- **Transactions** — `transactions`
- **Mining** — `mining`
- **Attacks** — `attacks`
- **Chain Explorer** — `chain_explorer`
- **Get Chain** — `get_chain`
- **Get Nodes** — `get_nodes`
- **Get Balances** — `get_balances`
- **New Transaction** — `new_transaction`
- **Mine** — `mine`
- **Perform Attack** — `perform_attack`
- **Get Stats** — `get_stats`

## Getting started

### 1. Get the project

```bash
git clone https://github.com/nasirabbas827/double-spending-Saida.git
cd double-spending-Saida
```

### 2. Prepare Python

Create an isolated environment:

```bash
python -m venv .venv
```

Activate it with `.venv\Scripts\activate` on Windows Command Prompt, or `source .venv/bin/activate` on macOS/Linux.

No requirements file is included. The inspected Python imports indicate these dependencies as a starting point:

```bash
python -m pip install Flask simpy
```

Dependency versions are not pinned in this repository.

### 3. Configure and run

Run from the repository root so relative file paths resolve correctly:

```bash
python app.py
```

Open http://127.0.0.1:5000/, or use the address printed by the application.

## Repository guide

| Path | Purpose |
| --- | --- |
| [`app.py`](app.py) | Application entry point |
| [`templates`](templates) | HTML page templates |

## Development notes

These setup instructions are based on the repository source. The application has not been executed as part of this documentation update; verify dependencies and configuration in your local environment.
