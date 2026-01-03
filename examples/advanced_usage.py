"""
Advanced usage example with custom configuration
"""

from pathlib import Path

from sage_github import IssuesConfig, IssuesManager


def main():
    """Advanced example with custom configuration"""
    print("🚀 GitHub Issues Manager - Advanced Example")
    print("=" * 50)

    # Custom project root
    custom_root = Path.home() / "my-projects" / "example-repo"
    custom_root.mkdir(parents=True, exist_ok=True)

    # Create configuration with custom settings
    config = IssuesConfig(
        project_root=custom_root, github_owner="your-org", github_repo="your-repo"
    )

    print(f"\n⚙️ Custom Configuration:")
    print(f"  Project Root: {config.project_root}")
    print(f"  Base Directory: {config.base_dir}")
    print(f"  Workspace: {config.workspace_path}")
    print(f"  Output: {config.output_path}")
    print(f"  Metadata: {config.metadata_path}")

    # Test connection
    print("\n🔍 Testing connection...")
    if not config.test_github_connection():
        print("  ❌ Failed to connect to GitHub")
        print("  💡 Please check:")
        print("     1. GITHUB_TOKEN environment variable is set")
        print("     2. Repository owner/name are correct")
        print("     3. Token has 'repo' scope permission")
        return

    print("  ✅ Connected!")

    # Create manager with custom config
    manager = IssuesManager(project_root=custom_root)

    print("\n📋 Manager initialized:")
    print(f"  Workspace: {manager.workspace_dir}")
    print(f"  Output: {manager.output_dir}")
    print(f"  Metadata: {manager.metadata_dir}")

    # Example: Load and analyze issues
    issues = manager.load_issues()

    if issues:
        print(f"\n📊 Found {len(issues)} issues")

        # Generate detailed statistics
        stats = manager._generate_statistics(issues)

        print("\n📈 Detailed Statistics:")
        print(f"  Total: {stats['total']}")
        print(f"  Open: {stats['open']}")
        print(f"  Closed: {stats['closed']}")

        # Show top labels
        if stats["labels"]:
            print("\n🏷️ Top 5 Labels:")
            for label, count in sorted(stats["labels"].items(), key=lambda x: x[1], reverse=True)[
                :5
            ]:
                print(f"    {label}: {count}")

        # Show top assignees
        if stats["assignees"]:
            print("\n👤 Top 5 Assignees:")
            for assignee, count in sorted(
                stats["assignees"].items(), key=lambda x: x[1], reverse=True
            )[:5]:
                print(f"    {assignee}: {count}")
    else:
        print("\n📥 No issues found. Download them first:")
        print("   github-manager download")


def example_with_environment_variables():
    """Example using environment variables for configuration"""
    import os

    # Set environment variables (in practice, do this in shell or .env file)
    os.environ["GITHUB_OWNER"] = "your-org"
    os.environ["GITHUB_REPO"] = "your-repo"
    # os.environ["GITHUB_TOKEN"] = "your_token_here"  # Set this securely

    # Configuration will automatically use environment variables
    config = IssuesConfig()

    print(f"Using repository: {config.GITHUB_OWNER}/{config.GITHUB_REPO}")

    # Rest of your code...


if __name__ == "__main__":
    print("Running advanced example...\n")
    main()

    print("\n" + "=" * 50)
    print("\nTo see environment variable example, uncomment the function call below")
    # example_with_environment_variables()
