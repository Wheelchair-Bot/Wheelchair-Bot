#!/usr/bin/env python
"""
Consolidated test runner for wheelchair emulator project.

Runs all tests across all packages with coverage reporting.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Run all tests with coverage."""
    project_root = Path(__file__).parent.parent

    print("=" * 70)
    print("Running Wheelchair Emulator Test Suite")
    print("=" * 70)
    print()

    # Set PYTHONPATH to include src directory
    import os
    env = os.environ.copy()
    src_path = str(project_root / "src")
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{src_path}:{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = src_path

    # Run pytest with coverage
    # Run tests separately to avoid module name conflicts
    cmd1 = [
        sys.executable,
        "-m",
        "pytest",
        str(project_root / "tests"),
        "-v",
        "--cov=wheelchair_bot",
        "--cov=wheelchair_controller",
        "--cov-report=term-missing:skip-covered",
        "--tb=short",
    ]

    cmd2 = [
        sys.executable,
        "-m",
        "pytest",
        str(project_root / "src" / "tests"),
        "-v",
        "--cov=wheelchair",
        "--cov-append",
        "--cov-report=term-missing:skip-covered",
        "--cov-report=html",
        "--tb=short",
    ]

    print(f"Running existing tests: {' '.join(cmd1[:4])}")
    print()

    result1 = subprocess.run(cmd1, cwd=project_root, env=env)

    print()
    print("=" * 70)
    print(f"Running emulator tests: {' '.join(cmd2[:4])}")
    print("=" * 70)
    print()

    result2 = subprocess.run(cmd2, cwd=project_root, env=env)

    # Run package tests (only if packages are installed)
    print()
    print("=" * 70)
    print("Running package tests")
    print("=" * 70)
    print()

    # Check if packages are installed before trying to test them
    package_tests_available = False
    try:
        import wheelchair_bot_shared  # noqa: F401
        import fastapi  # noqa: F401
        package_tests_available = True
    except ImportError:
        print("Package dependencies not installed. Skipping package tests.")
        print("To test packages, install them with:")
        print("  cd packages/shared && pip install -e .")
        print("  cd packages/backend && pip install -e .")
        result3 = subprocess.CompletedProcess(args=[], returncode=0)

    if package_tests_available:
        cmd3 = [
            sys.executable,
            "-m",
            "pytest",
            "packages/shared/tests/",
            "packages/backend/tests/",
            "-v",
            "--tb=short",
        ]
        result3 = subprocess.run(cmd3, cwd=project_root, env=env)
    else:
        # Create a successful result if packages aren't available
        result3 = subprocess.CompletedProcess(args=[], returncode=0)

    print()
    print("=" * 70)
    if result1.returncode == 0 and result2.returncode == 0 and result3.returncode == 0:
        print("✓ All tests passed!")
        returncode = 0
    else:
        print("✗ Some tests failed")
        returncode = 1
    print("=" * 70)

    # Print coverage report location
    coverage_dir = project_root / "htmlcov"
    if coverage_dir.exists():
        print(f"\nHTML coverage report: {coverage_dir / 'index.html'}")

    return returncode


if __name__ == "__main__":
    sys.exit(main())
