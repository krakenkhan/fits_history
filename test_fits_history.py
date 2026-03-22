import sys
sys.path.append('/content/drive/MyDrive/astro')

"""
Unit Tests for fits_history
"""

from fits_history.schemas import get_schema, list_entry_types, register_entry_type, unregister_entry_type, Field, EntryType
from fits_history.parser import parse_history, parse_card
from fits_history.writer import format_entry, format_value
from fits_history.validator import validate_entry, validate_history, print_report


passed = 0
failed = 0

def test(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS: {name}")
    else:
        failed += 1
        print(f"  FAIL: {name}")


PRE_BUILT_TYPES = 4

print("\n TESTING SCHEMAS")

print(f"{'--' * 25}")

test("All 13 types registered",
     len(list_entry_types()) == PRE_BUILT_TYPES)

test("PARENT has FILE as required",
     'FILE' in get_schema('PARENT').required_fields)

test("PARENT hdu is optional",
     'HDU' in get_schema('PARENT').optional_fields)
test("FILTER has 2 required fields",
     len(get_schema('FILTER').required_fields) == 2)

test("Unknown type returns None",
     get_schema('MOGUL') is None)

test("Case insensitive lookup",
     get_schema('origin') is not None)

# Testing Custom Entry TYPE addition and removal
custom = EntryType('RESAMP', 'Resampling', [
    Field('method', 'str', True, 'Method'),
    Field('pixscale', 'float', False, 'Pixel scale'),
])

register_entry_type(custom)
test("Custom type registered",
     get_schema('RESAMP') is not None)


# Duplicate registration should fail
try:
    register_entry_type(custom)
    test("Duplicate registration raises error", False)
except ValueError:
    test("Duplicate registration raises error", True)

unregister_entry_type(custom.name)

test("Custom type de-registered",
     get_schema('RESAMP') is None)



print(f"{'--' * 25}")

print("\nTESTING PARSER")

print(f"{'--' * 25}")

# Simple entry
entries = parse_history(['HISTORY #PARENT FILE=dark.fits hdu=1']) 
test("Parse simple entry",
     len(entries) == 1 and entries[0].entry_type == 'PARENT')

test("Parse field values",
     entries[0]['FILE'] == 'dark.fits' and entries[0]['HDU'] == 1)

# Continuation cards
entries = parse_history([
    'HISTORY #ORIGIN TEL=VLT INST=HAWK-I',
    "HISTORY ## OBS='J. Smith' DATE=2024-01-15",
])
test("Continuation merges fields",
     len(entries) == 1 and 'OBS' in entries[0] and 'TEL' in entries[0])

test("Quoted value with spaces",
     entries[0]['OBS'] == 'J. Smith')


# Multiple entries
entries = parse_history([
    'HISTORY #PARENT FILE=dark.fits',
    'HISTORY #FLATSUB FILE=flat.fits',
    'HISTORY #BIAS FILE=bias.fits',
])
test("Parse multiple entries",
     len(entries) == 3)


# Old free-form cards skipped
entries = parse_history([
    'HISTORY Old style text here',
    'HISTORY #DARKSUB FILE=dark.fits',
    'HISTORY More old text',
])


test("Skips free-form cards",
     len(entries) == 1 and entries[0].entry_type == 'DARKSUB')

# Type casting
entries = parse_history(['HISTORY #PARENT FILE=dark.fits hdu=1'])
test("Int casting",
     isinstance(entries[0]['hdu'], int) and entries[0]['hdu'] == 1)

entries = parse_history(['HISTORY #FILTER TYPE=gaussian SIZE=1080.67'])
test("Float casting",
     isinstance(entries[0]['SIZE'], float) and entries[0]['SIZE'] == 1080.67)

test("String stays string",
     isinstance(entries[0]['TYPE'], str))



# Testin get() with default
entries = parse_history(['HISTORY #DARKSUB FILE=dark.fits'])
test("get() returns value when present",
     entries[0].get('FILE') == 'dark.fits')

test("get() returns default if missing",
     entries[0].get('METHOD', 'none') == 'none')

# 'in' operator
test("'in' operator works",
     'FILE' in entries[0] and 'MOGUL' not in entries[0])

# Empty / malformed
test("Empty list returns empty",
     len(parse_history([])) == 0)

test("Only free-form returns empty",
     len(parse_history(['HISTORY just some text'])) == 0)

# Lonely continuation is ignored
entries = parse_history(['HISTORY ## KEY=value'])
test("Orphan continuation ignored",
     len(entries) == 0)


print(f"{'--' * 25}")

print("\n WRITER TESTS ")

print(f"{'--' * 25}")

# All cards are exactly 80 chars
cards = format_entry('DARKSUB', {'FILE': 'dark.fits', 'METHOD': 'median'})
test("Cards are 80 chars",
     all(len(c) == 80 for c in cards))

# Starts with HISTORY #TYPE
test("Card starts with HISTORY #TYPE",
     cards[0].startswith('HISTORY #DARKSUB'))

# Auto continuation
cards = format_entry('ORIGIN', {
    'TEL': 'VLT', 'INST': 'HAWK-I', 'SITE': 'Paranal',
    'OBS': 'J. Smith', 'DATE': '2024-01-15T14:30:00', 'PROG': '098.A-0123',
})
test("Long entry produces continuation",
     len(cards) > 1 and 'HISTORY ## ' in cards[1])

test("Continuation cards are 80 chars",
     all(len(c) == 80 for c in cards))

# Quoted values
cards = format_entry('ORIGIN', {'TEL': 'VLT UT1'})
test("Spaces in value get quoted",
     "'VLT UT1'" in cards[0])

# Numeric values
cards = format_entry('STACK', {'METHOD': 'median', 'NFRAMES': 20, 'LSIGMA': 3.0})
test("Numeric values written correctly",
     'NFRAMES=20' in cards[0] and 'LSIGMA=3.0' in cards[0])

# Fragment too long raises error
try:
    format_entry('SOFTWARE', {'REF': 'x' * 100})
    test("Oversized fragment raises error", False)
except ValueError:
    test("Oversized fragment raises error", True)



print(f"{'--' * 25}")
print("\nTESTING VALIDATOR")
print(f"{'--' * 25}")

# Valid entry
results = validate_history(['HISTORY #PARENT FILE=dark.fits HDU=1'])
test("Valid entry passes",
     results[0].is_valid)

test("Valid entry has no errors",
     len(results[0].errors) == 0)

# Missing required field
results = validate_history(['HISTORY #PARENT  HDU=1'])
test("Missing required field is invalid",
     not results[0].is_valid)

test("Error mentions missing field",
     'FILE' in results[0].errors[0])

# Multiple missing fields
results = validate_history(['HISTORY #FILTER KERNEL=linux'])
test("Multiple missing fields caught",
     len(results[0].errors) == 2)

# Unrecognized field is warning not error
results = validate_history(['HISTORY #PARENT FILE=dark.fits MOGUL=123'])
test("Unrecognized field is warning",
     results[0].is_valid and len(results[0].warnings) == 1)

# Unknown entry type is warning
results = validate_history(['HISTORY #FOOBAR KEY=value'])
test("Unknown type is warning",
     results[0].is_valid and len(results[0].warnings) == 1)


print(f"\n{'='*50}")
print(f"RESULTS: {passed} passed, {failed} failed out of {passed + failed}")
print(f"{'='*50}")