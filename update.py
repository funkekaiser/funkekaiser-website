#!/usr/bin/env python3
"""Update website fonts and CSP security hashes.

Handles:
1. Font management (restore from git or download from CDN)
2. CSP hash regeneration for inline scripts
"""

import re
import sys
import json
import hashlib
import base64
import subprocess
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError


# Font definitions with SHA256 checksums for integrity
FONTS = {
    "geist-latin.woff2": "19f9c92546aa300c312235e3125af1b81394d8db9a4bc4a425cd5b641d2d54e1",
    "geist-latin-ext.woff2": "824f485b5d26e2f2da3c2b236132ece1bc8e4e43373452950bb8e40548b4313f",
    "geist-mono-latin.woff2": "af61b969e7f999969f6af576e584ee85dca301a008a76be1251d172d56b9904c",
    "geist-mono-latin-ext.woff2": "63e27dba1a5baa700f1e279593c25ea6cfe24d2dff5badd2ecba178a35a49bb9",
}

# CDN source for font files
CDN_BASE = "https://unpkg.com/geist@1.7.2/fonts"

# HTML files containing inline scripts
SCRIPT_FILES = ["index.html", "impressum.html", "404.html"]


def run_command(cmd, quiet=False):
    """Run a shell command and return (success, output)."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=False
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def restore_fonts_from_git():
    """Try to restore fonts from git history."""
    print("📦 Attempting to restore fonts from git...")
    success, output = run_command("git checkout HEAD -- fonts/ 2>/dev/null")
    if success:
        fonts_dir = Path("fonts")
        if fonts_dir.exists():
            font_files = list(fonts_dir.glob("*.woff2"))
            if font_files:
                print(f"✓ Restored {len(font_files)} fonts from git")
                return True
    return False


def verify_font_integrity(filepath, expected_hash):
    """Verify font file integrity using SHA256."""
    if not filepath.exists():
        return False
    
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    
    actual_hash = sha256_hash.hexdigest()
    if actual_hash != expected_hash:
        print(f"⚠️  Hash mismatch for {filepath.name}")
        print(f"   Expected: {expected_hash}")
        print(f"   Actual:   {actual_hash}")
        return False
    return True


def download_font(filename, expected_hash):
    """Download a single font file from CDN with integrity check."""
    filepath = Path("fonts") / filename
    url = f"{CDN_BASE}/{filename}"
    
    print(f"⬇️  Downloading {filename}...")
    try:
        with urlopen(url, timeout=10) as response:
            data = response.read()
        
        filepath.write_bytes(data)
        
        if verify_font_integrity(filepath, expected_hash):
            size_kb = filepath.stat().st_size / 1024
            print(f"   ✓ {filename} ({size_kb:.1f} KB)")
            return True
        else:
            filepath.unlink(missing_ok=True)
            return False
    
    except URLError as e:
        print(f"   ✗ Failed to download: {e}")
        return False


def update_fonts():
    """Update fonts: restore from git first, fallback to CDN."""
    fonts_dir = Path("fonts")
    fonts_dir.mkdir(exist_ok=True)
    
    print("\n" + "=" * 60)
    print("🔄 Updating fonts...")
    print("=" * 60)
    
    # Try git first
    if restore_fonts_from_git():
        print("=" * 60)
        return True
    
    # Fallback to CDN
    print("⚠️  Fonts not in git, downloading from CDN...")
    failed = []
    
    for filename, expected_hash in FONTS.items():
        if not download_font(filename, expected_hash):
            failed.append(filename)
    
    if failed:
        print(f"\n✗ Failed to download: {', '.join(failed)}")
        print("=" * 60)
        return False
    
    print("\n⚠️  Downloaded fonts from CDN. Consider committing to git:")
    print("   git add fonts/")
    print('   git commit -m "Update Geist fonts"')
    print("=" * 60)
    return True


def compute_script_hashes():
    """Extract and hash inline scripts from HTML files."""
    hashes_by_file = {}
    all_hashes = []
    
    for filename in SCRIPT_FILES:
        try:
            with open(filename, encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"✗ Error: {filename} not found")
            return None, None
        
        hashes_by_file[filename] = []
        
        # Find all inline <script> blocks (skip external scripts and JSON-LD)
        for match in re.finditer(
            r"<script([^>]*)>(.*?)</script>", content, re.DOTALL
        ):
            attrs = match.group(1)
            script_content = match.group(2)
            
            # Skip external scripts and JSON-LD
            if "src=" in attrs or "ld+json" in attrs:
                continue
            
            # Compute SHA-256 hash
            hash_obj = hashlib.sha256(script_content.encode())
            hash_b64 = base64.b64encode(hash_obj.digest()).decode()
            hash_csp = f"'sha256-{hash_b64}'"
            
            print(f"  {filename:20} {hash_csp}")
            hashes_by_file[filename].append(hash_csp)
            all_hashes.append(hash_csp)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_hashes = []
    for h in all_hashes:
        if h not in seen:
            seen.add(h)
            unique_hashes.append(h)
    
    return hashes_by_file, unique_hashes


def update_headers_file(all_hashes):
    """Update _headers file with new hashes."""
    headers_file = Path("_headers")
    
    try:
        headers_content = headers_file.read_text(encoding="utf-8")
    except FileNotFoundError:
        print("✗ Error: _headers file not found")
        return False
    
    # Find existing script-src line
    csp_match = re.search(r"script-src '[^']+' ([^;]+);", headers_content)
    if not csp_match:
        print("✗ Error: Could not find script-src in _headers")
        return False
    
    # Build new script-src directive
    new_script_src = (
        "script-src 'self' " +
        " ".join(all_hashes) +
        " https://static.cloudflareinsights.com"
    )
    
    # Update the _headers file
    updated_headers = re.sub(
        r"script-src '[^']+' [^;]+;", new_script_src + ";", headers_content
    )
    
    # Write updated _headers
    try:
        headers_file.write_text(updated_headers, encoding="utf-8")
        return True
    except IOError as e:
        print(f"✗ Error writing _headers: {e}")
        return False


def extract_hashes_from_headers():
    """Extract hashes from current _headers file."""
    headers_file = Path("_headers")
    try:
        headers_content = headers_file.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    
    # Extract hashes from script-src line
    match = re.search(r"script-src '[^']+' ([^;]+);", headers_content)
    if not match:
        return None
    
    hashes_str = match.group(1)
    # Extract all 'sha256-...' hashes
    hashes = re.findall(r"'sha256-[^']*'", hashes_str)
    return set(hashes)


def validate_hashes():
    """Validate that _headers hashes match current inline scripts (no update)."""
    print("\n" + "=" * 60)
    print("🔍 Validating CSP hashes...")
    print("=" * 60)
    
    hashes_by_file, all_hashes = compute_script_hashes()
    
    if hashes_by_file is None or not all_hashes:
        print("✗ Error: No inline scripts found")
        print("=" * 60)
        return False
    
    # Get unique hashes from scripts
    unique_script_hashes = set(all_hashes)
    
    # Get hashes currently in _headers
    headers_hashes = extract_hashes_from_headers()
    if headers_hashes is None:
        print("✗ Error: Could not read hashes from _headers")
        print("=" * 60)
        return False
    
    # Compare
    if unique_script_hashes == headers_hashes:
        print("=" * 60)
        print("✓ CSP hashes are valid (match current inline scripts)")
        print("=" * 60)
        return True
    else:
        print("\n✗ CSP hashes are OUT OF DATE!")
        print("\nExpected hashes from scripts:")
        for h in sorted(unique_script_hashes):
            print(f"  {h}")
        print("\nCurrent hashes in _headers:")
        for h in sorted(headers_hashes):
            print(f"  {h}")
        print("\nMissing from _headers:", unique_script_hashes - headers_hashes)
        print("Extra in _headers:", headers_hashes - unique_script_hashes)
        print("\n💡 Fix this by running: python3 update.py hashes")
        print("=" * 60)
        return False


def update_hashes():
    """Update CSP hashes in _headers."""
    print("\n" + "=" * 60)
    print("🔐 Regenerating CSP hashes...")
    print("=" * 60)
    
    hashes_by_file, all_hashes = compute_script_hashes()
    
    if hashes_by_file is None or not all_hashes:
        print("✗ Error: No inline scripts found")
        print("=" * 60)
        return False
    
    if not update_headers_file(all_hashes):
        print("=" * 60)
        return False
    
    print("=" * 60)
    print("✓ _headers updated successfully")
    print("=" * 60)
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update website fonts and CSP security hashes"
    )
    parser.add_argument(
        "action",
        nargs="?",
        default="all",
        choices=["all", "fonts", "hashes", "validate"],
        help="Action to perform (default: all)",
    )
    
    args = parser.parse_args()
    
    success = True
    
    if args.action == "validate":
        success = validate_hashes()
    else:
        if args.action in ("all", "fonts"):
            if not update_fonts():
                success = False
        
        if args.action in ("all", "hashes"):
            if not update_hashes():
                success = False
        
        if args.action == "all":
            print("\n✓ All updates complete" if success else "\n✗ Some updates failed")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
