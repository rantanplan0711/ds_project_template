#!/usr/bin/env python
"""Post-generation hook für UV setup."""

import os
import subprocess
import sys
from pathlib import Path

# Cookiecutter variables
PROJECT_SLUG = "{{ cookiecutter.project_slug }}"
PYTHON_VERSION = "3.12"

PROJECT_DIR = Path.cwd()


def run_command(cmd: list[str], check: bool = True) -> bool:
    """Führt Befehl aus."""
    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=True,
            text=True
        )
        print(f"✓ {' '.join(cmd)}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Fehler bei: {' '.join(cmd)}")
        print(f"  {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"✗ Command nicht gefunden: {cmd[0]}")
        return False


def check_uv_installed() -> bool:
    """Prüft ob UV installiert ist."""
    try:
        subprocess.run(
            ["uv", "--version"],
            check=True,
            capture_output=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    """Haupt-Setup."""
    print("\n" + "="*50)
    print(f"🚀 Initialisiere Projekt: {PROJECT_SLUG}")
    print("="*50 + "\n")

    # 0. Add folder structure
    # Ordner erstellen
    directories = [
        "data/01_raw",
        "data/02_preprocess", 
        "data/03_final",
        "notebooks",
        "scripts",
        "models",
    ]

    for dir_path in directories:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        # .gitkeep für leere Ordner
        (path / ".gitkeep").touch()

    print("✓ Projektstruktur erstellt")
    # 1. UV Check
    if not check_uv_installed():
        print("⚠️  UV nicht gefunden!")
        print("   Installation: pip install uv")
        print("   Oder: curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)

    # 2. UV Sync (erstellt venv + installiert dependencies)
    print("\n📦 Installiere Dependencies...")
    if not run_command(["uv", "sync", "--all-extras"]):
        print("⚠️  UV sync fehlgeschlagen")
        sys.exit(1)

    # 3. Jupyter Kernel (falls gewünscht)
    print("\n🎯 Registriere Jupyter Kernel...")
    run_command([
        "uv", "run", "python", "-m", "ipykernel", "install",
        "--user", f"--name={PROJECT_SLUG}"
    ], check=False)

    # 4. Git initialisieren (optional)
    print("\n📝 Initialisiere Git...")
    run_command(["git", "init"], check=False)
    run_command(["git", "add", "."], check=False)
    # 5. Pre-commit hook installieren 
    if not run_command(["uv", "run", "pre-commit", "install"], check=False):
        print("⚠️  Pre-commit hooks Installation fehlgeschlagen")
        return False
    # 6. Initialer commit
    run_command([
        "git", "commit", "-m", "Initial commit from cookiecutter"
    ], check=False)

    # 5. Fertig!
    print("\n" + "="*50)
    print("✅ Projekt erfolgreich erstellt!")
    print("="*50)
    print(f"\n📂 Projekt-Verzeichnis: {PROJECT_DIR}")
    print("\n🎯 Nächste Schritte:")
    print(f"   cd {PROJECT_SLUG}")
    print("   uv run jupyter lab")
    print("\n💡 Weitere Commands:")
    print("   uv add <package>    - Package hinzufügen")
    print("   uv sync             - Dependencies aktualisieren")


if __name__ == "__main__":
    main()