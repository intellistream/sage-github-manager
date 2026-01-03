"""
Basic usage example for GitHub Issues Manager
"""

from sage_github import IssuesConfig, IssuesManager


def main():
    """Main example function"""
    print("🐙 GitHub Issues Manager - Basic Example")
    print("=" * 50)

    # Create configuration
    # Note: Set GITHUB_TOKEN environment variable or create ~/.github_token file
    config = IssuesConfig(
        github_owner="intellistream",  # Change to your organization
        github_repo="SAGE",  # Change to your repository
    )

    print("\n📋 Configuration:")
    print(f"  Repository: {config.GITHUB_OWNER}/{config.GITHUB_REPO}")
    print(f"  Project Root: {config.project_root}")
    print(f"  Workspace: {config.workspace_path}")

    # Test GitHub connection
    print("\n🔍 Testing GitHub connection...")
    if config.test_github_connection():
        print("  ✅ Connected successfully!")

        # Get repository info
        repo_info = config.get_repo_info()
        print("\n📊 Repository Info:")
        print(f"  Full Name: {repo_info['full_name']}")
        print(f"  Description: {repo_info.get('description', 'N/A')}")
        print(f"  Stars: {repo_info['stargazers_count']}")
        print(f"  Forks: {repo_info['forks_count']}")
        print(f"  Open Issues: {repo_info['open_issues_count']}")
    else:
        print("  ❌ Connection failed!")
        print("  💡 Make sure to set GITHUB_TOKEN environment variable")
        return

    # Create manager
    print("\n🔨 Creating Issues Manager...")
    manager = IssuesManager()

    # Load issues (if already downloaded)
    print("\n📥 Loading issues...")
    issues = manager.load_issues()

    if issues:
        print(f"  ✅ Loaded {len(issues)} issues")

        # Show statistics
        print("\n📊 Generating statistics...")
        manager.show_statistics()
    else:
        print("  ℹ️ No issues found locally")
        print("  💡 Run 'github-manager download' to download issues first")


if __name__ == "__main__":
    main()
