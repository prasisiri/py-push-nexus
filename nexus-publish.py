#!/usr/bin/env python3
"""
Script to build and publish the package to Nexus repository.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, check=True):
    """Run a command and handle errors."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        sys.exit(f"Command failed with return code {result.returncode}")
    
    return result


def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning previous build artifacts...")
    
    directories_to_clean = ['build', 'dist', 'src/*.egg-info']
    for directory in directories_to_clean:
        run_command(f"rm -rf {directory}", check=False)


def build_package():
    """Build the package."""
    print("Building package...")
    run_command("python -m build")


def publish_to_nexus(nexus_url, username=None, password=None):
    """Publish package to Nexus repository."""
    print(f"Publishing to Nexus: {nexus_url}")
    
    # Build twine upload command
    cmd = f"twine upload --repository-url {nexus_url}/repository/pypi-hosted/ dist/*"
    
    if username:
        cmd += f" --username {username}"
    
    if password:
        cmd += f" --password {password}"
    
    run_command(cmd)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Build and publish package to Nexus")
    parser.add_argument("--nexus-url", required=True, 
                       help="Nexus repository URL (e.g., https://nexus.example.com)")
    parser.add_argument("--username", 
                       help="Nexus username (can also use NEXUS_USERNAME env var)")
    parser.add_argument("--password", 
                       help="Nexus password (can also use NEXUS_PASSWORD env var)")
    parser.add_argument("--skip-build", action="store_true",
                       help="Skip building and just publish existing artifacts")
    parser.add_argument("--dry-run", action="store_true",
                       help="Build package but don't publish")
    
    args = parser.parse_args()
    
    # Get credentials from environment if not provided
    username = args.username or os.getenv('NEXUS_USERNAME')
    password = args.password or os.getenv('NEXUS_PASSWORD')
    
    if not args.dry_run and not username:
        print("Error: Nexus username required (use --username or NEXUS_USERNAME env var)")
        sys.exit(1)
    
    if not args.dry_run and not password:
        print("Error: Nexus password required (use --password or NEXUS_PASSWORD env var)")
        sys.exit(1)
    
    try:
        # Check if required tools are installed
        run_command("python -m build --version")
        run_command("twine --version")
        
        if not args.skip_build:
            clean_build()
            build_package()
        
        if not args.dry_run:
            publish_to_nexus(args.nexus_url, username, password)
            print("\n✅ Package successfully published to Nexus!")
            print(f"Install with: pip install connect-postgres-utility --extra-index-url {args.nexus_url}/repository/pypi-hosted/simple/")
        else:
            print("\n✅ Package built successfully (dry run - not published)")
            print("Artifacts available in dist/ directory")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 