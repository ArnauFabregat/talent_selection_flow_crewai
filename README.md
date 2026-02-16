# OS Multiagent System

An open-source multiagent system for talent selection using advanced AI techniques. This system leverages multiple specialized agents to analyze candidate profiles and job requirements, providing intelligent matching and insights.

Tech Stack:
- [**CrewAI**](https://docs.crewai.com/en/quickstart) - Multi-agent orchestration framework
- [**ChromaDB**](https://docs.trychroma.com/docs/overview/getting-started) - Vector database for semantic search and embeddings
- [**OpenRouter**](https://openrouter.ai/) - LLM provider using `arcee-ai/trinity-large-preview:free` (free tier)
- [**Jina**](https://jina.ai/) - Embedding model `jina-embeddings-v2-base-en` for semantic embeddings (free tier)
- [**Chainlit**](https://docs.chainlit.io/get-started/overview) - LLM application UI framework

## Table of Contents

1. [Data Sources](#data-sources)
2. [Agents Workflow](#agents-workflow)
3. [How to Run](#how-to-run)
4. [Virtual Environment](#virtual-environment)
    - [Create a new virtualenv with the project's dependencies](#create-a-new-virtualenv-with-the-projects-dependencies)
    - [Checking if the project's virtual environment is active](#checking-if-the-projects-virtual-environment-is-active)
    - [Updating the project's dependencies](#updating-the-projects-dependencies)
5. [Code Quality & Documentation](#code-quality--documentation)
    - [Pre-commit Hooks](#pre-commit-hooks)
    - [Unit Testing](#unit-testing)
    - [Peer Review](#peer-review)
6. [TODO](#todo)

## Data Sources
The system uses two primary datasets sourced from Kaggle to train and evaluate the CV-to-job matching algorithms:
- CV data: https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset
- Job posts data: https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction

## Agents Workflow

Full Architecture Diagram (TBD)

The system will do three main workflows:
- Metadata extraction from raw cv or job
- CV → Related Jobs → Gaps → Interview Questions → Final Report
- Job → Related CVs → Gaps → Interview Questions → Final Report

Agents description:
0) Metadata extractor Agents: cvs and jobs.
1) Orchestrator Agent.
    - **Role**: Entry point. Detects whether the user uploaded a CV or a job description and selects the correct workflow.
    - **Tools**: None or simple classification LLM.
    - **Goal**: Pick the correct pipeline (CV→JD or JD→CV).
2) CV → Job Retrieval Agent.
    - **Role**: Given a CV (plain text), embed & query ChromaDB to retrieve top X job descriptions.
    - **Knowledge**: ChromaDB job embeddings.
    - **Goal**: Return a ranked list of job postings related to the CV.
3) Job → CV Retrieval Agent. This is symmetric to agent #2.
    - **Role**: Given a job description, embed & query ChromaDB to retrieve top X candidate CVs.
    - **Knowledge**: ChromaDB CV embeddings.
    - **Goal**: Return a ranked list of candidates.
4) Gap Identifier Agent.
    - **Role**:
        - Compare candidate skills vs job requirements.
        - Identify missing skills (skill gaps).
        - Provide severity levels (must‑have / nice‑to‑have).
    - **Goal**: Output a structured JSON of gaps.
5) Interview Question Generator Agent.
    - **Role**: Generate HR-friendly interview questions based on:
        - Skills matched
        - Skills missing
        - Ambiguities in experience
        - Seniority expectations
    - **Goal**: Provide 5–10 tailored questions per match.
6) Report Writer Agent
    - **Role**: Combine outputs into a clean, final PDF/text report:
        - Top matches
        - Score explanations
        - Skill gaps
        - Interview questions
        - Overall recommendation
    - **Goal**: Produce a polished summary for HR.

## How to Run
TBD

## Virtual Environment
### Create a new virtualenv with the project's dependencies
---
Install the project's virtual environment and set it as your project's Python interpreter.
This will also install the project's current dependencies.

Open a terminal in VSCode, then execute the following commands:

1. Install [UV: Python package and project manager](https://docs.astral.sh/uv/getting-started/installation/):
    * On Mac OSX / Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
    * On Windows [In Powershell]: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

2. [optional] To create virtual environment from scratch with `uv`: [Working on projects](https://docs.astral.sh/uv/guides/projects/)

3. If the environment already exists, install the virtual environment. It will be installed in the project's root, under a new directory named `.venv`:
    * `uv sync`
    * `uv sync --group dev --group dashboard --group test` to install all the dependency groups

4. Activate the new virtual environment:
    * On Mac OSX / Linux: `source .venv/bin/activate`
    * On Windows [In Powershell]: `.venv\Scripts\activate`

5. Configure / install pre-commit hooks:
    * [Pre-commit](https://pre-commit.com/) is a tool that helps us keep the repository complying with certain formatting and style standards, using the `hooks` configured in the `.pre-commit-config.yaml` file.
    * Previously installed with `uv sync`.

### Checking if the project's virtual environment is active
---
All commands listed here assume the project's virtual env is active.

To ensure so, execute the following command, and ensure it points to: `{project_root}/.venv/bin/python`:
* On Mac OSX / Linux: `which python`
* On Windows / Mac OSX / Linux: `python -c "import sys; import os; print(os.path.abspath(sys.executable))"`

If not active, execute the following to activate:
* On Mac OSX / Linux: `source .venv/bin/activate`
* On Windows [In Powershell]: `.venv\Scripts\activate`

Alternatively, you can also run any command using the prefix `uv run` and `uv` will make sure that it uses the virtual env's Python executable.

### Updating the project's dependencies
---
#### Adding new dependencies
---
In order to avoid potential version conflicts, we should use uv's dependency manager to add new libraries additional to the project's current dependenies.
Open a terminal in VSCode and execute the following commands:

* `uv add {dependency}` e.g. `uv add pandas`

This command will update the project's files `pyproject.toml` and `uv.lock` automatically, which are the ones ensuring all developers and environments have the exact same dependencies.

#### Updating your virtual env with dependencies recently added or removed from the project
---
Open a terminal in VSCode and execute the following command:
* `uv sync`

## Code Quality & Documentation
### Pre-commit Hooks
---
This project uses [pre-commit](https://pre-commit.com/) hooks to enforce code quality standards automatically before each commit. The following hooks are configured:

- **Formatting & File Integrity**: `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-toml`
- **Code Linting & Formatting**: `ruff-check`, `ruff-format`
- **Type Checking**: `mypy`

Pre-commit hooks are automatically installed during virtual environment setup (`uv sync`). To run them manually:
```bash
.venv\Scripts\activate
pre-commit run
```

### Unit Testing
---
Unit tests ensure code reliability and prevent regressions. Tests are written using pytest and should cover critical functionality.

To run all tests:
```bash
uv run pytest
```

To run tests with coverage:
```bash
uv run pytest --cov
```

### Peer Review
---
All code contributions are subject to peer review. Detailed review guidelines and standards are documented in the project's peer review guidelines document.

TBD

## TODO
- Add top_k from input optional
- Add documentation in README
- Add docstrings
- Add unit tests
- Add max_iter and max_rpm to control rate limits in agents
- Add chainlit and save logs in file
- Add pdf mapper if pdf input
- Add agent that gets profiles from linkedin in JobToCVCrew
    - https://github.com/crewAIInc/crewAI-examples/blob/main/crews/recruitment/src/recruitment/tools/linkedin.py
    - add reasoning True with max_reasoning_attempts
- Tools:
    - crewai: https://docs.crewai.com/en/concepts/tools
    - langchain: https://docs.langchain.com/oss/python/integrations/tools
- Crewai examples: https://docs.crewai.com/en/examples/example