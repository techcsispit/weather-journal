# Source Start Weather Journal

Welcome to the **Source Start Weather Journal** repository! We're thrilled to have you as a contributor to our command-line weather logging, climate tracking, and statistics tool built in Python.

As part of **"Source Start"**, an open-source initiative organized by **CSI-SPIT**, this project gives beginners and intermediate developers a hands-on experience integrating with real-world REST APIs, managing embedded SQLite databases, designing CLI tools, and writing automated unit tests.

---

## Table of Contents

- [Introduction](#introduction)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [1. Fork the Repository](#1-fork-the-repository)
  - [2. Clone Your Fork](#2-clone-your-fork)
  - [3. Install Dependencies](#3-install-dependencies)
  - [4. Set up OpenWeatherMap API Key](#4-set-up-openweathermap-api-key)
  - [5. Running the CLI](#5-running-the-cli)
- [CLI Commands Reference](#cli-commands-reference)
- [Running Tests](#running-tests)
- [How to Contribute](#how-to-contribute)
  - [Contribution Workflow](#contribution-workflow)
  - [Issue Labels & Difficulty Tiers](#issue-labels--difficulty-tiers)
- [Code of Conduct](#code-of-conduct)
- [License](#license)

---

## Introduction

**Weather Journal** is a persistent terminal assistant for logging and analyzing meteorological observations across different cities. 

It queries the OpenWeatherMap REST API for real-time conditions, records temperatures, humidity levels, and descriptions in an embedded SQLite database (`weather_journal.db`), and computes insightful climate summaries including average temperatures, peak heatwaves, and rainy intervals.

---

## Key Features

- 🌤️ **Live Weather Fetching**: Integrates with OpenWeatherMap API to retrieve current conditions.
- 💾 **SQLite Storage**: Automatically manages historical observations in an embedded SQLite database.
- 📈 **Statistical Summaries**: Calculates averages, identifies record high temperatures, and counts rainy days.
- 💻 **Intuitive CLI Interface**: Subcommands for logging observations, browsing history, and generating stats.
- 🧪 **Automated Offline Unit Tests**: Tests statistics logic using mock datasets without making live API requests.

---

## Project Structure

```text
weather-journal/
├── README.md               # Project guide and contributor documentation
├── LICENSE                 # MIT License
├── requirements.txt        # Python dependencies (requests)
├── .gitignore              # Standard Python and database ignores
├── weather_journal/
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Allows running `python -m weather_journal`
│   ├── fetch.py            # API client for OpenWeatherMap
│   ├── store.py            # SQLite database schema and query helpers
│   ├── stats.py            # Average temperature and climate statistics
│   └── cli.py              # Command-line interface and subcommand parsers
└── tests/
    ├── __init__.py
    └── test_stats.py       # Offline unit tests for statistics logic
```

---

## Getting Started

### Prerequisites

- **Python 3.8+** installed on your system.
- A free OpenWeatherMap API Key (obtainable at [openweathermap.org](https://openweathermap.org/api)).

Verify your Python installation:
```bash
python3 --version
```

### 1. Fork the Repository

Click the **Fork** button in the top-right corner of this repository page on GitHub to create your own copy.

### 2. Clone Your Fork

Clone your newly created fork locally:

```bash
git clone https://github.com/techcsispit/weather-journal.git
cd weather-journal
```

### 3. Install Dependencies

Install the required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Set up OpenWeatherMap API Key

Export your API key as an environment variable in your shell:

```bash
# macOS / Linux
export OWM_API_KEY="your_api_key_here"

# Windows (Command Prompt)
set OWM_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:OWM_API_KEY="your_api_key_here"
```

Alternatively, you can supply `--key <your-key>` directly in CLI commands.

### 5. Running the CLI

Run the tool as a Python module:

```bash
# Log current weather for a city
python3 -m weather_journal log "Mumbai"

# View observation history
python3 -m weather_journal history "Mumbai"

# Calculate climate stats
python3 -m weather_journal stats "Mumbai"
```

---

## CLI Commands Reference

| Command | Arguments | Description |
|---|---|---|
| `log` | `<city> [--key <key>]` | Queries current weather for a city and appends it to the database. |
| `history` | `[city]` | Displays previous weather observations. |
| `stats` | `<city>` | Computes summary metrics (average temp, hottest day, rainy counts). |

---

## Running Tests

Unit tests run completely offline without making live API calls, using sample fixtures:

```bash
python3 -m unittest discover tests
```

To run a specific test file:
```bash
python3 -m unittest tests/test_stats.py
```

> 💡 **Tip for Contributors:** Always run unit tests before opening a pull request to ensure your changes don't break existing stats logic.

---

## How to Contribute

We welcome and appreciate contributions from everyone participating in **Source Start**!

### Contribution Workflow

1. **Pick an Issue:** Go to the **Issues** tab to find an open task. Leave a comment expressing your interest to be assigned.
2. **Create a Feature Branch:** Keep your `main` branch clean by creating a dedicated topic branch:
   ```bash
   git checkout -b fix/issue-description
   ```
3. **Make Your Changes:** Edit code cleanly, preserving existing conventions and docstrings.
4. **Test Your Changes:**
   - Run automated tests: `python3 -m unittest discover tests`
   - Test manually in your terminal with sample CLI calls.
5. **Commit Your Work:** Write clear, descriptive commit messages:
   ```bash
   git commit -m "fix: resolve issue description"
   ```
6. **Push to Your Fork:**
   ```bash
   git push origin fix/issue-description
   ```
7. **Open a Pull Request:** Navigate to your fork on GitHub and submit a Pull Request describing your changes.

### Issue Labels & Difficulty Tiers

- 🔁 `good first issue`: Ideal for beginners and first-time contributors.
- 🐛 `bug`: Fixing API parsing discrepancies, error crashes, or query boundaries.
- ✨ `enhancement`: Introducing new metric calculations, command options, or export formats.

> 📌 **Note:** All active tasks and bug reports will be announced in the **[Issues](../../issues)** tab. Check the tab to pick your first issue!

---

## Code of Conduct

This project adheres to a community code of conduct fostering a respectful, inclusive, and welcoming learning environment. Please be supportive in all discussions and pull request reviews.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Organized with ❤️ by <b>CSI-SPIT</b> for <b>Source Start</b>.<br>
  Happy Coding! ☀️🌧️
</p>
