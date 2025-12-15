"""
Checksum utility functions for data integrity verification
"""

import hashlib
from typing import Union


def calculate_checksum(data: Union[bytes, str], algorithm: str = "sha256") -> str:
    """
    Calculate checksum for data

    Args:
        data: Data to calculate checksum for (bytes or string)
        algorithm: Hash algorithm ('md5' or 'sha256')

    Returns:
        Checksum hex string

    Raises:
        ValueError: If unsupported algorithm is specified

    Example:
        >>> calculate_checksum(b"Hello World", "sha256")
        'a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e'
    """
    # Convert string to bytes if needed
    if isinstance(data, str):
        data = data.encode("utf-8")

    if algorithm.lower() == "md5":
        return hashlib.md5(data).hexdigest()
    elif algorithm.lower() == "sha256":
        return hashlib.sha256(data).hexdigest()
    else:
        raise ValueError(f"Unsupported checksum algorithm: {algorithm}")


def verify_checksum(
    data: Union[bytes, str], expected_checksum: str, algorithm: str = "sha256"
) -> bool:
    """
    Verify data against an expected checksum

    Args:
        data: Data to verify
        expected_checksum: Expected checksum hex string
        algorithm: Hash algorithm used

    Returns:
        True if checksums match, False otherwise

    Example:
        >>> data = b"Hello World"
        >>> checksum = calculate_checksum(data, "sha256")
        >>> verify_checksum(data, checksum, "sha256")
        True
    """
    calculated = calculate_checksum(data, algorithm)
    return calculated.lower() == expected_checksum.lower()


def calculate_file_checksum(file_path: str, algorithm: str = "sha256") -> str:
    """
    Calculate checksum for a file

    Args:
        file_path: Path to the file
        algorithm: Hash algorithm ('md5' or 'sha256')

    Returns:
        Checksum hex string

    Raises:
        ValueError: If unsupported algorithm is specified
        FileNotFoundError: If file doesn't exist

    Example:
        >>> calculate_file_checksum("document.pdf", "sha256")
        'abc123...'
    """
    if algorithm.lower() == "md5":
        hasher = hashlib.md5()
    elif algorithm.lower() == "sha256":
        hasher = hashlib.sha256()
    else:
        raise ValueError(f"Unsupported checksum algorithm: {algorithm}")

    # Read file in chunks to handle large files
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def verify_file_checksum(
    file_path: str, expected_checksum: str, algorithm: str = "sha256"
) -> bool:
    """
    Verify file against an expected checksum

    Args:
        file_path: Path to the file
        expected_checksum: Expected checksum hex string
        algorithm: Hash algorithm used

    Returns:
        True if checksums match, False otherwise

    Example:
        >>> verify_file_checksum("document.pdf", "abc123...", "sha256")
        True
    """
    calculated = calculate_file_checksum(file_path, algorithm)
    return calculated.lower() == expected_checksum.lower()
