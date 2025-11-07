#!/usr/bin/env python3
"""
Creates SQLite database from adblock lists.
"""

import os
import sqlite3
import sys
from pathlib import Path

# Database configuration
PAGE_SIZE = 32768  # SQLite page size
FTS_PAGE_SIZE = 32000  # FTS page size (pgsz)


def main():
    # Allow specifying lists directory and database filename via command line arguments
    lists_dir = sys.argv[1] if len(sys.argv) > 1 else "lists"
    db_file = sys.argv[2] if len(sys.argv) > 2 else "rules.db"

    print(f"Creating database '{db_file}' from files in '{lists_dir}'...")

    # Clean up old DB
    if os.path.exists(db_file):
        os.unlink(db_file)
        print(f"Removed existing '{db_file}'.")

    # Setup new DB
    db = sqlite3.connect(db_file, isolation_level="IMMEDIATE", autocommit=True)
    db.execute("PRAGMA foreign_keys = ON")

    # Create tables
    print("Creating tables...")

    # Create a table for source files (normalized)
    db.execute("""
        CREATE TABLE source_files (
            id INTEGER PRIMARY KEY,
            filename TEXT UNIQUE NOT NULL
        )
    """)

    # Create a table for the rule content with foreign key to source_files
    db.execute("""
        CREATE TABLE rules_content (
            id INTEGER PRIMARY KEY,
            rule TEXT NOT NULL,
            source_file_id INTEGER NOT NULL,
            line_number INTEGER NOT NULL,
            FOREIGN KEY (source_file_id) REFERENCES source_files(id)
        )
    """)

    # Prepare for import
    lists_path = Path(lists_dir)
    if not lists_path.exists():
        print(f"Error: Directory '{lists_dir}' does not exist.")
        sys.exit(1)

    list_files = [f.name for f in lists_path.iterdir() if f.suffix == ".txt"]

    # Bulk insert source files
    print(f"Inserting {len(list_files)} source files...")
    db.executemany(
        "INSERT INTO source_files (filename) VALUES (?)",
        [(file,) for file in list_files],
    )

    # Read back the source file IDs
    source_file_map = {}
    cursor = db.execute("SELECT id, filename FROM source_files")
    for row in cursor:
        source_file_map[row[1]] = row[0]

    total_rules = 0

    # Read lists and import
    print(f"Found {len(list_files)} .txt files to import.")

    # Start explicit transaction for rule insertions (for better performance)
    db.execute("BEGIN IMMEDIATE TRANSACTION")

    for file in list_files:
        file_path = lists_path / file
        print(f"- Importing '{file_path}'...")

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            with open(file_path, encoding="latin-1") as f:
                content = f.read()

        lines = content.split("\n")
        rules_to_insert = []

        for i, line in enumerate(lines):
            rule_text = line.strip()
            # Skip comments and empty lines
            if (
                rule_text.startswith("!")
                or rule_text.startswith("data:")
                or rule_text == ""
            ):
                continue

            normalized_text = rule_text.lower()
            rules_to_insert.append((normalized_text, source_file_map[file], i + 1))

        # Bulk insert rules for this file
        db.executemany(
            "INSERT INTO rules_content (rule, source_file_id, line_number) VALUES (?, ?, ?)",
            rules_to_insert,
        )

        print(f"  Imported {len(rules_to_insert)} rules.")
        total_rules += len(rules_to_insert)

    # Single commit for ALL rule insertions
    db.execute("COMMIT")

    print(f"\nImported a total of {total_rules} rules.\n")

    # 6. Create and populate FTS index
    print("Creating and populating FTS index...")
    db.execute("""
        CREATE VIRTUAL TABLE rules USING fts5(
            rule,
            content='rules_content',
            content_rowid=rowid,
            tokenize="unicode61 separators '-._#$,'"
        )
    """)

    db.execute(f"INSERT INTO rules(rule) VALUES('pgsz={FTS_PAGE_SIZE}')")

    db.execute("""
        INSERT INTO rules(rowid, rule)
        SELECT id, rule FROM rules_content
    """)
    print("FTS index created.")

    # Optimize DB
    print("Optimizing database...")
    db.execute("PRAGMA journal_mode = DELETE")
    db.execute(f"PRAGMA page_size = {PAGE_SIZE}")
    print(" - Running FTS optimize...")
    db.execute("INSERT INTO rules(rules) VALUES ('optimize')")

    print(" - Vacuuming database...")
    db.execute("VACUUM")
    print("Database optimized.")

    # 8. Close DB
    db.close()

    print(f"\nSQLite database '{db_file}' created successfully.")


if __name__ == "__main__":
    main()
