#!/usr/bin/env python3
"""
Upload a prepared dataset JSON file to the API

Usage:
    python upload_dataset.py <filename>
    python upload_dataset.py borough_population_ranking.json

The script will look for the file in ./data/prepared_data/ directory
"""

import sys
from data.utils.utils import upload_dataset


def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("❌ Error: No filename provided")
        print("\nUsage:")
        print("  python upload_dataset.py <filename>")
        print("\nExample:")
        print("  python upload_dataset.py borough_population_ranking.json")
        sys.exit(1)

    filename = sys.argv[1]
    success = upload_dataset(filename)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
