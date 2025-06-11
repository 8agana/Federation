#!/usr/bin/env python3
"""
Content hashing utilities for CC-DT Memory Federation.

Provides consistent SHA256 hashing for memory content to:
- Enable content-based addressing
- Prevent duplicate storage
- Allow verification of content integrity
"""

import hashlib
import json
from typing import Dict, Any, Optional, Union

def generate_content_hash(content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate a SHA256 hash of content with optional metadata inclusion.
    
    Args:
        content: The main content to hash
        metadata: Optional metadata to include in hash calculation
        
    Returns:
        Hex string of SHA256 hash (64 characters)
    """
    # Normalize content (strip whitespace, consistent line endings)
    normalized_content = content.strip().replace('\r\n', '\n').replace('\r', '\n')
    
    # Create hash object
    hasher = hashlib.sha256()
    
    # Hash the content
    hasher.update(normalized_content.encode('utf-8'))
    
    # Optionally include certain metadata fields in hash
    if metadata:
        # Only include stable metadata fields (not timestamps)
        stable_fields = ['title', 'tags', 'domain', 'category']
        stable_metadata = {k: v for k, v in metadata.items() if k in stable_fields}
        
        if stable_metadata:
            # Sort keys for consistent ordering
            metadata_str = json.dumps(stable_metadata, sort_keys=True)
            hasher.update(metadata_str.encode('utf-8'))
    
    return hasher.hexdigest()

def generate_short_hash(content: str, length: int = 8) -> str:
    """
    Generate a shortened hash for display purposes.
    
    Args:
        content: The content to hash
        length: Number of characters to return (default 8)
        
    Returns:
        First N characters of the hash
    """
    full_hash = generate_content_hash(content)
    return full_hash[:length]

def verify_content_hash(content: str, expected_hash: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """
    Verify that content matches an expected hash.
    
    Args:
        content: The content to verify
        expected_hash: The hash to check against
        metadata: Optional metadata that was included in original hash
        
    Returns:
        True if content matches hash, False otherwise
    """
    actual_hash = generate_content_hash(content, metadata)
    return actual_hash == expected_hash

def check_duplicate_content(new_content: str, existing_hashes: list[str], metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Check if content already exists based on hash.
    
    Args:
        new_content: The new content to check
        existing_hashes: List of existing content hashes
        metadata: Optional metadata for hash calculation
        
    Returns:
        The matching hash if duplicate found, None otherwise
    """
    new_hash = generate_content_hash(new_content, metadata)
    
    if new_hash in existing_hashes:
        return new_hash
    
    return None

def hash_memory_id(content_hash: str, timestamp: str) -> str:
    """
    Generate a composite memory ID from content hash and timestamp.
    
    This allows for both content-based and time-based addressing.
    
    Args:
        content_hash: The content's SHA256 hash
        timestamp: ISO format timestamp
        
    Returns:
        Composite ID like "cc_20250607_210900_a1b2c3d4"
    """
    # Take first 8 chars of content hash
    short_hash = content_hash[:8]
    
    # Extract date/time from timestamp
    if 'T' in timestamp:
        date_part = timestamp.split('T')[0].replace('-', '')
        time_part = timestamp.split('T')[1].split('.')[0].replace(':', '')
    else:
        # Fallback for non-ISO timestamps
        date_part = timestamp[:10].replace('-', '')
        time_part = timestamp[11:19].replace(':', '')
    
    return f"cc_{date_part}_{time_part}_{short_hash}"

def extract_hash_from_id(memory_id: str) -> Optional[str]:
    """
    Extract the content hash portion from a composite memory ID.
    
    Args:
        memory_id: Memory ID like "cc_20250607_210900_a1b2c3d4"
        
    Returns:
        The hash portion or None if not found
    """
    parts = memory_id.split('_')
    if len(parts) >= 4:
        return parts[-1]
    return None

if __name__ == "__main__":
    # Test the hasher
    test_content = "This is a test memory about implementing hash-based IDs."
    test_metadata = {"title": "Test Memory", "tags": ["test", "hash"]}
    
    # Generate hash
    content_hash = generate_content_hash(test_content, test_metadata)
    print(f"Content hash: {content_hash}")
    print(f"Short hash: {generate_short_hash(test_content)}")
    
    # Test verification
    is_valid = verify_content_hash(test_content, content_hash, test_metadata)
    print(f"Verification: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Test composite ID
    from datetime import datetime
    timestamp = datetime.now().isoformat()
    composite_id = hash_memory_id(content_hash, timestamp)
    print(f"Composite ID: {composite_id}")
    
    # Extract hash back
    extracted = extract_hash_from_id(composite_id)
    print(f"Extracted hash: {extracted}")