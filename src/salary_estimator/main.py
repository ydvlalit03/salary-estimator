"""CLI entry point for salary estimation."""

import argparse
import json
import sys
from pathlib import Path

from .graph import estimate_salary
from .nodes.knowledge_base import init_knowledge_base


EXAMPLE_PROFILE = """
John Smith
Senior Software Engineer at Google

San Francisco Bay Area

About:
Experienced software engineer with 7 years of experience building scalable distributed systems.
Currently working on Google Cloud Platform infrastructure.

Experience:
- Senior Software Engineer at Google (2021 - Present, 3 years)
  Working on GCP Compute Engine, Kubernetes integration, and cloud infrastructure.

- Software Engineer at Stripe (2019 - 2021, 2 years)
  Built payment processing systems and fraud detection pipelines.

- Software Engineer at Airbnb (2017 - 2019, 2 years)
  Developed search ranking algorithms and backend services.

Education:
- M.S. Computer Science, Stanford University
- B.S. Computer Science, UC Berkeley

Skills:
Python, Go, Java, Kubernetes, Distributed Systems, Machine Learning, AWS, GCP, System Design
"""


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Estimate market salary from LinkedIn profile",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Estimate salary from a file
  salary-estimator --file profile.txt

  # Estimate salary from stdin
  cat profile.txt | salary-estimator

  # Use the built-in example profile
  salary-estimator --example

  # Initialize the knowledge base
  salary-estimator --init-kb
        """,
    )

    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Path to a file containing the LinkedIn profile text",
    )
    parser.add_argument(
        "--example",
        action="store_true",
        help="Run with an example profile to test the system",
    )
    parser.add_argument(
        "--init-kb",
        action="store_true",
        help="Initialize the knowledge base with seed data",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Pretty-print the JSON output (default: True)",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Output compact JSON (no pretty-printing)",
    )

    args = parser.parse_args()

    # Initialize knowledge base
    if args.init_kb:
        count = init_knowledge_base()
        print(f"Knowledge base initialized with {count} records.")
        return 0

    # Get profile text
    profile_text = None

    if args.example:
        profile_text = EXAMPLE_PROFILE
        print("Using example profile...\n", file=sys.stderr)
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            return 1
        profile_text = file_path.read_text()
    elif not sys.stdin.isatty():
        profile_text = sys.stdin.read()
    else:
        parser.print_help()
        print("\nError: No profile provided. Use --file, --example, or pipe input.", file=sys.stderr)
        return 1

    if not profile_text or not profile_text.strip():
        print("Error: Empty profile provided.", file=sys.stderr)
        return 1

    # Initialize KB before running
    init_knowledge_base()

    # Run estimation
    try:
        print("Analyzing profile...", file=sys.stderr)
        result = estimate_salary(profile_text)

        # Output result
        if args.compact:
            print(json.dumps(result))
        else:
            print(json.dumps(result, indent=2))

        return 0

    except Exception as e:
        print(f"Error during estimation: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
