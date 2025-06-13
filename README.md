# 🗄️ CSV Viewer (Python)

A lightweight and user-friendly **CSV viewer** built with Python, designed for quick inspection and basic manipulation of CSV, TSV, or other delimited text files.

---

## 📋 Table of Contents

1. [Overview](#overview)  
2. [Features](#features)  
3. [Requirements](#requirements)  
4. [Installation](#installation)  
5. [Usage](#usage)  
6. [Code Structure](#code-structure)  
7. [Enhancement Ideas](#enhancement-ideas)  
8. [Contributing](#contributing)  
9. [License](#license)

---

## 💡 Overview

This tool lets users easily view tabular data from CSV or delimited files via a CLI. It provides quick insights into large datasets without the need for spreadsheets or data-heavy tools by leveraging Python’s standard library :contentReference[oaicite:1]{index=1}.

---

## ✅ Features

- 📂 Read local delimited files (CSV, TSV, custom separators)  
- 🔢 Display row count, headers, and sample rows  
- 🔍 Sort data by column alphabetically or numerically  
- ✅ Clean handling of missing or malformed lines  
- 🛠️ Option to export a cleaned/filtered view to a new file

---

## 🧾 Requirements

- Python **3.7+**  
- Only uses the Python **standard library** (`csv`, `argparse`, `sys`, etc.)

---

## ⚙️ Installation

```bash
git clone https://github.com/MisaghMomeniB/CSV-Viewer-Python.git
cd CSV-Viewer-Python
python3 --version  # Confirm Python ≥3.7
````

---

## 🚀 Usage

### CLI Options

Basic usage:

```bash
python csv_viewer.py --path data.csv --delimiter comma --sample 20
```

Available flags:

* `--path <file>`: Path to your CSV/TSV file
* `--delimiter <char>`: `comma`, `semicolon`, `tab`, or custom
* `--sample <int>`: Number of rows to preview (default: 10)
* `--sort <column>`: Sort preview by this column
* `--export <file>`: Save cleaned/sample rows to a new file

---

## 📁 Code Structure

```
CSV-Viewer-Python/
├── csv_viewer.py   # Main CLI + core logic
├── README.md       # You're reading it!
└── LICENSE
```

Inside `csv_viewer.py`:

* Argparse handles CLI options
* Uses `csv.reader` / `csv.DictReader` for parsing
* Basic validation of headers, row counts, and empty fields
* Functions to preview and optionally export data

---

## 💡 Enhancement Ideas

* 📊 Add interactive filter options (e.g., show rows where column > value)
* 📦 Support export to formats like JSON or Markdown tables
* 📈 Integrate with Pandas for advanced previews or plotting
* 🧭 Build a GUI with libraries like Tkinter or PyQt
* 🔄 Add batch previewing for multi-file browsing

---

## 🤝 Contributing

Improvements welcome! Possible additions:

* Support large files via streaming
* Implement real-time file watching
* Add deduplication or column-based filters

**To contribute**:

1. Fork this repo
2. Create a branch (`feature/...`)
3. Write clear, well-commented code
4. Open a Pull Request with a description of changes

---

## 📄 License

Licensed under the **MIT License** — see `LICENSE` file for details.
