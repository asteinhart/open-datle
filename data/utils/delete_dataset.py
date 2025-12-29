#!/usr/bin/env python3
"""
Delete a dataset from the API

Usage:
    python delete_dataset.py <dataset_id>
    python delete_dataset.py 3
"""

import sys
from data.utils.utils import delete_dataset


def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: python delete_dataset.py <dataset_id>")
        print("Example: python delete_dataset.py 3")
        sys.exit(1)

    dataset_id = sys.argv[1]

    try:
        dataset_id = int(dataset_id)
    except ValueError:
        print("Error: Dataset ID must be a number")
        sys.exit(1)

    # Execute deletion
    success = delete_dataset(dataset_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
