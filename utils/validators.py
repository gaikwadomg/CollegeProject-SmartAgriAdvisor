"""
AgriSense AI - Input Validators
=================================

Provides reusable validation functions for form inputs across the
application. Used by UI forms and service layer to ensure data integrity.

Usage:
    from utils.validators import validate_numeric_range, validate_required
    
    errors = []
    errors += validate_required("Username", username_value)
    errors += validate_numeric_range("Nitrogen", n_value, 0, 140)

Author: AgriSense AI Team
"""

import re
from typing import Any, List, Optional, Tuple

from utils.constants import INPUT_RANGES


def validate_required(field_name: str, value: Any) -> List[str]:
    """
    Validate that a field is not empty or None.

    Args:
        field_name: Human-readable field name for error messages
        value: The value to check

    Returns:
        List of error messages (empty if valid)
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return [f"{field_name} is required."]
    return []


def validate_numeric(field_name: str, value: Any) -> Tuple[List[str], Optional[float]]:
    """
    Validate that a value is numeric and convert it.

    Args:
        field_name: Human-readable field name
        value: The value to validate

    Returns:
        Tuple of (error_list, converted_float_or_None)
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return [f"{field_name} is required."], None
    try:
        return [], float(value)
    except (ValueError, TypeError):
        return [f"{field_name} must be a valid number."], None


def validate_numeric_range(
    field_name: str,
    value: Any,
    min_val: float,
    max_val: float
) -> Tuple[List[str], Optional[float]]:
    """
    Validate that a value is numeric and within a specified range.

    Args:
        field_name: Human-readable field name
        value: The value to validate
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)

    Returns:
        Tuple of (error_list, converted_float_or_None)
    """
    errors, num_value = validate_numeric(field_name, value)
    if errors:
        return errors, None
    if num_value < min_val or num_value > max_val:
        return [f"{field_name} must be between {min_val} and {max_val}."], None
    return [], num_value


def validate_input_field(field_key: str, value: Any) -> Tuple[List[str], Optional[float]]:
    """
    Validate an input field using predefined ranges from constants.

    Args:
        field_key: Key matching INPUT_RANGES dict (e.g., 'nitrogen', 'temperature')
        value: The value to validate

    Returns:
        Tuple of (error_list, converted_float_or_None)
    """
    if field_key not in INPUT_RANGES:
        return [f"Unknown field: {field_key}"], None

    ranges = INPUT_RANGES[field_key]
    display_name = field_key.replace("_", " ").title()
    return validate_numeric_range(
        f"{display_name} ({ranges['unit']})",
        value,
        ranges["min"],
        ranges["max"]
    )


def validate_selection(field_name: str, value: Any, options: List[str]) -> List[str]:
    """
    Validate that a value is one of the allowed options.

    Args:
        field_name: Human-readable field name
        value: The selected value
        options: List of allowed options

    Returns:
        List of error messages
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return [f"{field_name} is required."]
    if value not in options:
        return [f"{field_name} must be one of: {', '.join(options[:5])}..."]
    return []


def validate_email(email: str) -> List[str]:
    """
    Validate email format using a simple regex pattern.

    Args:
        email: Email address to validate

    Returns:
        List of error messages
    """
    if not email or not email.strip():
        return ["Email is required."]
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return ["Please enter a valid email address."]
    return []


def validate_password(password: str, min_length: int = 6) -> List[str]:
    """
    Validate password strength.

    Args:
        password: Password to validate
        min_length: Minimum required length

    Returns:
        List of error messages
    """
    errors = []
    if not password:
        return ["Password is required."]
    if len(password) < min_length:
        errors.append(f"Password must be at least {min_length} characters.")
    return errors


def validate_username(username: str) -> List[str]:
    """
    Validate username format.

    Args:
        username: Username to validate

    Returns:
        List of error messages
    """
    if not username or not username.strip():
        return ["Username is required."]
    if len(username) < 3:
        return ["Username must be at least 3 characters."]
    if len(username) > 50:
        return ["Username must be 50 characters or less."]
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return ["Username can only contain letters, numbers, and underscores."]
    return []


def validate_crop_inputs(
    n: Any, p: Any, k: Any,
    temperature: Any, humidity: Any,
    ph: Any, rainfall: Any
) -> Tuple[List[str], Optional[dict]]:
    """
    Validate all inputs for crop recommendation in one call.

    Args:
        n, p, k: Soil nutrient values
        temperature: Temperature in °C
        humidity: Relative humidity in %
        ph: Soil pH value
        rainfall: Rainfall in mm

    Returns:
        Tuple of (error_list, validated_values_dict_or_None)
    """
    all_errors = []
    values = {}

    fields = [
        ("nitrogen", n), ("phosphorus", p), ("potassium", k),
        ("temperature", temperature), ("humidity", humidity),
        ("ph", ph), ("rainfall", rainfall)
    ]

    for field_key, value in fields:
        errors, validated = validate_input_field(field_key, value)
        all_errors.extend(errors)
        if validated is not None:
            values[field_key] = validated

    if all_errors:
        return all_errors, None
    return [], values


def validate_positive_number(field_name: str, value: Any) -> Tuple[List[str], Optional[float]]:
    """
    Validate that a value is a positive number (> 0).

    Args:
        field_name: Human-readable field name
        value: The value to validate

    Returns:
        Tuple of (error_list, converted_float_or_None)
    """
    errors, num_value = validate_numeric(field_name, value)
    if errors:
        return errors, None
    if num_value <= 0:
        return [f"{field_name} must be a positive number."], None
    return [], num_value
