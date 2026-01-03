#!/usr/bin/env python3
"""
GitHub Issues Manager - Main CLI Entry Point
"""

import sys


def main():
    """Main CLI entry point"""
    try:
        from sage_github.cli import app
        
        # Run the Typer app
        app()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
