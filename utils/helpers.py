"""
AgriSense AI - Helper Utilities
=================================

General-purpose utility functions used throughout the application.
Includes date formatting, file operations, image processing helpers,
and data conversion utilities.

Author: AgriSense AI Team
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from utils.logger import get_logger

logger = get_logger(__name__)


# ══════════════════════════════════════════════════════════════════════
# DATE & TIME UTILITIES
# ══════════════════════════════════════════════════════════════════════

def format_datetime(dt: Optional[datetime] = None, fmt: str = "%d %b %Y, %I:%M %p") -> str:
    """
    Format a datetime object to a human-readable string.

    Args:
        dt: Datetime to format. Uses current time if None.
        fmt: Format string.

    Returns:
        Formatted date string (e.g., '21 Jul 2026, 09:30 PM')
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)


def format_date(dt: Optional[datetime] = None, fmt: str = "%d %b %Y") -> str:
    """
    Format a datetime to a date-only string.

    Args:
        dt: Datetime to format.
        fmt: Format string.

    Returns:
        Formatted date (e.g., '21 Jul 2026')
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)


def get_greeting() -> str:
    """
    Return a time-appropriate greeting.

    Returns:
        'Good Morning', 'Good Afternoon', or 'Good Evening'
    """
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"


# ══════════════════════════════════════════════════════════════════════
# FILE UTILITIES
# ══════════════════════════════════════════════════════════════════════

def safe_load_json(file_path: str) -> Optional[Dict]:
    """
    Safely load a JSON file, returning None on any error.

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed dict or None on error
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
        logger.warning(f"Failed to load JSON from {file_path}: {e}")
        return None


def safe_save_json(data: Any, file_path: str) -> bool:
    """
    Safely save data to a JSON file.

    Args:
        data: Data to serialize
        file_path: Output file path

    Returns:
        True if saved successfully
    """
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except (OSError, TypeError) as e:
        logger.error(f"Failed to save JSON to {file_path}: {e}")
        return False


def get_file_size_display(file_path: str) -> str:
    """
    Get a human-readable file size string.

    Args:
        file_path: Path to the file

    Returns:
        Size string like '2.5 MB' or 'N/A' if not found
    """
    try:
        size = os.path.getsize(file_path)
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except OSError:
        return "N/A"


def copy_file_safe(src: str, dst: str) -> bool:
    """
    Safely copy a file, creating destination directory if needed.

    Args:
        src: Source file path
        dst: Destination file path

    Returns:
        True if copied successfully
    """
    try:
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    except (OSError, shutil.Error) as e:
        logger.error(f"Failed to copy {src} to {dst}: {e}")
        return False


# ══════════════════════════════════════════════════════════════════════
# DATA CONVERSION UTILITIES
# ══════════════════════════════════════════════════════════════════════

def round_to(value: float, decimals: int = 2) -> float:
    """Round a float to specified decimal places."""
    return round(value, decimals)


def percentage_str(value: float, decimals: int = 1) -> str:
    """Format a float as a percentage string."""
    return f"{round(value * 100, decimals)}%"


def confidence_to_label(confidence: float) -> Tuple[str, str]:
    """
    Convert a confidence score (0-1) to a human-readable label and color.

    Args:
        confidence: Float between 0 and 1

    Returns:
        Tuple of (label, color_hex) e.g., ('High', '#66BB6A')
    """
    if confidence >= 0.8:
        return "High", "#66BB6A"
    elif confidence >= 0.5:
        return "Medium", "#FFA726"
    else:
        return "Low", "#EF5350"


def format_currency(amount: float, symbol: str = "₹") -> str:
    """
    Format a number as currency with Indian style.

    Args:
        amount: Amount to format
        symbol: Currency symbol

    Returns:
        Formatted string like '₹1,25,000.00'
    """
    if amount < 0:
        return f"-{symbol}{abs(amount):,.2f}"
    return f"{symbol}{amount:,.2f}"


def format_yield(value: float, unit: str = "kg/hectare") -> str:
    """Format a yield value with unit."""
    return f"{value:,.1f} {unit}"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


# ══════════════════════════════════════════════════════════════════════
# IMAGE UTILITIES
# ══════════════════════════════════════════════════════════════════════

def resize_image_maintain_aspect(
    image_size: Tuple[int, int],
    max_size: Tuple[int, int]
) -> Tuple[int, int]:
    """
    Calculate new dimensions maintaining aspect ratio within max bounds.

    Args:
        image_size: Original (width, height)
        max_size: Maximum (width, height)

    Returns:
        New (width, height) maintaining aspect ratio
    """
    orig_w, orig_h = image_size
    max_w, max_h = max_size

    ratio = min(max_w / orig_w, max_h / orig_h)
    new_w = int(orig_w * ratio)
    new_h = int(orig_h * ratio)

    return new_w, new_h


# ══════════════════════════════════════════════════════════════════════
# DATABASE / BACKUP UTILITIES
# ══════════════════════════════════════════════════════════════════════

def create_backup(source_path: str, backup_dir: str) -> Optional[str]:
    """
    Create a timestamped backup of a file.

    Args:
        source_path: File to backup
        backup_dir: Directory to store backups

    Returns:
        Backup file path on success, None on failure
    """
    try:
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(source_path).stem
        ext = Path(source_path).suffix
        backup_path = os.path.join(backup_dir, f"{filename}_backup_{timestamp}{ext}")
        shutil.copy2(source_path, backup_path)
        logger.info(f"Backup created: {backup_path}")
        return backup_path
    except (OSError, shutil.Error) as e:
        logger.error(f"Backup failed for {source_path}: {e}")
        return None


def restore_backup(backup_path: str, target_path: str) -> bool:
    """
    Restore a backup file to the target path.

    Args:
        backup_path: Path to the backup file
        target_path: Where to restore it

    Returns:
        True if restored successfully
    """
    try:
        shutil.copy2(backup_path, target_path)
        logger.info(f"Restored backup from {backup_path} to {target_path}")
        return True
    except (OSError, shutil.Error) as e:
        logger.error(f"Restore failed: {e}")
        return False
