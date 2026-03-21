""" Validator for Machine-Readable FITS HISTORY Cards. """

from .schemas import get_schema
from .parser import parse_history



class ValidationResult:
    """ Result of validating a single HistoryEntry. """

    def __init__(self, entry):
        self.entry = entry
        self.errors = []
        self.warnings = []

    @property
    def is_valid(self):
        """ An entry is valid if it has no errors. Warnings are acceptable. """
        return len(self.errors) == 0

    def add_error(self, message):
        self.errors.append(message)

    def add_warning(self, message):
        self.warnings.append(message)

    def __repr__(self):
        status = "VALID" if self.is_valid else "INVALID"
        return f"ValidationResult(#{self.entry.entry_type}, {status}, errors={len(self.errors)}, warnings={len(self.warnings)})"

    def report(self):
        """ Return a human-readable report string. """
        lines = []
        status = "VALID" if self.is_valid else "INVALID"
        lines.append(f"#{self.entry.entry_type}: {status}")

        for err in self.errors:
            lines.append(f"  ERROR:   {err}")
        for warn in self.warnings:
            lines.append(f"  WARNING: {warn}")

        if self.is_valid and not self.warnings:
            lines.append(f"  All checks passed.")

        return '\n'.join(lines)



def validate_entry(entry):
    """
    Validate a single HistoryEntry against its schema.

    Checks:
        1. Entry type is recognized in the registry
        2. All required fields are present
        3. Field values match their expected types
        4. No unrecognized fields

    """
    result = ValidationResult(entry)
    schema = get_schema(entry.entry_type)

    # Check if the entry type is recognized
    if schema is None:
        result.add_warning(
            f"Unknown entry type '{entry.entry_type}'. "
            f"Not in the standard registry."
        )
        # Can't check fields without a schema
        return result

    # Check of all required fields are present
    for field_name in schema.required_fields:
        if field_name not in entry.fields:
            result.add_error(
                f"Missing required field '{field_name}'."
            )

    # Check if field values match expected types
    for field_name, value in entry.fields.items():
        if field_name in schema.fields:
            field_def = schema.fields[field_name]
            type_error = _check_type(value, field_def.dtype)
            if type_error:
                result.add_error(
                    f"Field '{field_name}' {type_error}"
                )
        else:
            # An Unrecognized field
            result.add_warning(
                f"Unrecognized field '{field_name}' for type '{entry.entry_type}'."
            )

    return result


def validate_history(history_cards):
    """
    Validate all entries in a list of HISTORY cards.
    """
    entries = parse_history(history_cards)
    results = []
    for entry in entries:
        results.append(validate_entry(entry))
    return results


def validate_header(header):
    """
    Validate all HISTORY entries in an astropy FITS header.
    """
    history_cards = header.get('HISTORY', [])
    # astropy returns history values without the 'HISTORY ' prefix
    # so we add it back for the parser
    full_cards = [f"HISTORY {card}" for card in history_cards]
    return validate_history(full_cards)


def print_report(results):
    """ Print a formatted validation report. """
    total = len(results)
    valid = 0
    for r in results:
        if r.is_valid:
            valid += 1
    invalid = total - valid

    print(f"Validation Report")
    print(f"Entries checked: {total}")
    print(f"Valid: {valid}  |  Invalid: {invalid}")
    print()

    for r in results:
        print(r.report())
        print()



def _check_type(value, expected_dtype):
    """
    Check if a value matches the expected type. Returns None if valid, or an error message string if not.
    """
    if expected_dtype == 'int':
        if not isinstance(value, int):
            return f"expected int, got '{value}' ({type(value).__name__})."
    elif expected_dtype == 'float':
        # Accept both float and int for float fields
        if not isinstance(value, (float, int)):
            return f"expected float, got '{value}' ({type(value).__name__})."
    elif expected_dtype == 'str':
        if not isinstance(value, str):
            return f"expected str, got '{value}' ({type(value).__name__})."
    return None