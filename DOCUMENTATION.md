# fits_history — Machine-Readable FITS HISTORY Standard

**Version:** 0.1.0

A Python library that defines and implements a standard for writing structured, machine-readable HISTORY keyword entries in FITS files. Fully backward-compatible with all existing FITS readers — old parsers see normal HISTORY comment text and ignore it.

---

## The Problem

FITS HISTORY cards are free-form text:

```
HISTORY bias subtracted using bias frame bias_20240115.fits
HISTORY flat fielded using flat_K_20240115.fits
```

Humans can read this. Machines cannot. There is no way to programmatically answer "which dark frame was used?" or "was sky subtraction performed?" without writing fragile text-parsing hacks that break across different observatories.

## The Solution

This library defines a standard syntax for HISTORY cards that is both human-readable and machine-parseable:

```
HISTORY #DARKSUB FILE=dark_60s.fits METHOD=median SCALE=1.02
HISTORY #FLATSUB FILE=flat_K.fits FILTER=K METHOD=divide
HISTORY #SOFTWARE NAME=DRAGONS VER=3.1.0 LANG=Python
```

Old FITS readers see `HISTORY` followed by text — they skip it as always. This library's parser sees the `#` prefix and extracts structured key-value data.

---

## Installation

Copy the `fits_history/` package folder into your project or add it to your Python path. Requires Python 3.7+. The writer and validator integration methods require `astropy`.

```
your_project/
├── fits_history/
│   ├── __init__.py
│   ├── schemas.py
│   ├── parser.py
│   ├── writer.py
│   └── validator.py
└── your_script.py
```

---

## Syntax Rules

```
HISTORY #TYPE KEY=value KEY=value
HISTORY ## KEY=value KEY=value        (continuation)
```

- `#` at column 9 signals a machine-readable entry
- `##` signals a continuation of the previous entry
- The word after `#` is the entry type (uppercase, max 8 characters)
- Keys are uppercase, alphanumeric plus underscore
- Values with spaces are wrapped in single quotes: `KEY='some value'`
- Values without spaces are unquoted: `KEY=3.14`
- Every card is exactly 80 characters (standard FITS)
- Usable space per card is 72 characters (`HISTORY ` takes 8)

---

## Supported Entry Types

The standard defines 13 entry types. Each has required fields (must be present) and optional fields (recognized but not mandatory).

### #ORIGIN — Where the raw data came from

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| TEL | yes | str | Telescope name |
| INST | yes | str | Instrument name |
| SITE | no | str | Observatory site |
| OBS | no | str | Observer name |
| DATE | no | str | Observation date (ISO 8601) |
| PROG | no | str | Program/proposal ID |

```
HISTORY #ORIGIN TEL=VLT INST=HAWK-I SITE=Paranal
HISTORY ## OBS='J. Smith' DATE=2024-01-15T14:30:00
```

### #DARKSUB — Dark frame subtraction

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| FILE | yes | str | Dark frame filename |
| METHOD | no | str | median / mean / scaled |
| SCALE | no | float | Scale factor applied |
| EXPTIME | no | float | Dark frame exposure time (seconds) |

```
HISTORY #DARKSUB FILE=dark_60s_K.fits METHOD=median SCALE=1.02
```

### #FLATSUB — Flat field correction

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| FILE | yes | str | Flat field filename |
| FILTER | no | str | Filter band used |
| METHOD | no | str | divide / multiply |
| NORM | no | float | Normalization value |

```
HISTORY #FLATSUB FILE=flat_K_norm.fits FILTER=K METHOD=divide
```

### #BIAS — Bias subtraction

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| FILE | yes | str | Bias frame filename |
| METHOD | no | str | median / mean |
| NFRAMES | no | int | Number of frames in master bias |

```
HISTORY #BIAS FILE=bias_master.fits METHOD=median NFRAMES=50
```

### #SKYSUB — Sky subtraction

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| METHOD | yes | str | median / model / offset / polynomial |
| LEVEL | no | float | Sky level subtracted (ADU) |
| NFRAMES | no | int | Number of sky frames used |
| FILE | no | str | Sky model filename if applicable |

```
HISTORY #SKYSUB METHOD=median NFRAMES=5 LEVEL=245.3
```

### #STACK — Image combination / stacking

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| METHOD | yes | str | median / mean / sigclip / minmax |
| NFRAMES | yes | int | Number of input frames |
| REJECT | no | str | Rejection algorithm |
| LSIGMA | no | float | Lower sigma clipping threshold |
| HSIGMA | no | float | Upper sigma clipping threshold |
| OUTPUT | no | str | Output filename |

```
HISTORY #STACK METHOD=sigclip NFRAMES=20 REJECT=sigclip
HISTORY ## LSIGMA=3.0 HSIGMA=3.0 OUTPUT=mosaic_K.fits
```

### #WCSCAL — World Coordinate System calibration

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| CATALOG | yes | str | Reference catalog used |
| NSTARS | no | int | Number of matched stars |
| RMS | no | float | RMS of fit (arcseconds) |
| METHOD | no | str | Fitting method |

```
HISTORY #WCSCAL CATALOG=GAIA-DR3 NSTARS=142 RMS=0.12
```

### #PHOTCAL — Photometric calibration

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| ZP | yes | float | Zero point magnitude |
| FILTER | yes | str | Filter band |
| CATALOG | no | str | Reference catalog |
| NSTARS | no | int | Number of standard stars used |
| EXTINCT | no | float | Extinction coefficient |

```
HISTORY #PHOTCAL ZP=25.32 FILTER=K CATALOG=2MASS NSTARS=15
```

### #SOFTWARE — Processing software used

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| NAME | yes | str | Software name |
| VER | yes | str | Version string |
| LANG | no | str | Language / platform |
| REF | no | str | URL or citation |

```
HISTORY #SOFTWARE NAME=DRAGONS VER=3.1.0 LANG=Python
```

### #FILTER — Filtering / smoothing applied

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| TYPE | yes | str | gaussian / median / boxcar / butterworth |
| SIZE | yes | float | Kernel size (pixels) |
| KERNEL | no | str | Custom kernel name or shape |
| AXIS | no | str | Axis filtered: x / y / both |

```
HISTORY #FILTER TYPE=gaussian SIZE=3.5 AXIS=both
```

### #COSMIC — Cosmic ray rejection

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| METHOD | yes | str | lacosmic / dcr / crmedian / manual |
| NREJ | no | int | Number of pixels rejected |
| THRESH | no | float | Detection threshold (sigma) |
| ITER | no | int | Number of iterations |

```
HISTORY #COSMIC METHOD=lacosmic THRESH=5.0 NREJ=1523 ITER=3
```

### #TRIM — Image trimming / cropping

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| X1 | yes | int | Start pixel X |
| X2 | yes | int | End pixel X |
| Y1 | yes | int | Start pixel Y |
| Y2 | yes | int | End pixel Y |
| REASON | no | str | Reason for trimming |

```
HISTORY #TRIM X1=50 X2=2000 Y1=50 Y2=2000 REASON=overscan
```

### #PARENT — Links to source files

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| FILE | yes | str | Source filename |
| HDU | no | int | HDU index in source file |
| ROLE | no | str | science / calibration / reference |
| CHECKSUM | no | str | File checksum for verification |

```
HISTORY #PARENT FILE=raw_001.fits ROLE=science
HISTORY #PARENT FILE=std_star.fits ROLE=calibration
```

---

## API Reference

### schemas.py

The schema registry. Defines all 13 entry types and their fields. This is the single source of truth that the parser, writer, and validator all reference.

#### Field(name, dtype, required, description)

Defines a single field within an entry type.

```python
from fits_history.schemas import Field

f = Field('file', 'str', True, 'Dark frame filename')

f.name          # 'FILE' (auto-uppercased)
f.dtype         # 'str'
f.required      # True
f.description   # 'Dark frame filename'
```

**Parameters:**

- `name` (str) — Field name. Automatically converted to uppercase.
- `dtype` (str) — Expected type: `'str'`, `'int'`, or `'float'`.
- `required` (bool) — Whether this field must be present for a valid entry.
- `description` (str) — Human-readable description.

---

#### EntryType(name, description, fields)

Defines an entry type schema with its collection of fields.

```python
from fits_history.schemas import EntryType, Field

my_type = EntryType(
    name='RESAMP',
    description='Image resampling.',
    fields=[
        Field('method', 'str', True, 'Resampling method'),
        Field('pixscale', 'float', False, 'Output pixel scale'),
    ]
)

my_type.name              # 'RESAMP'
my_type.description       # 'Image resampling.'
my_type.required_fields   # ['METHOD']
my_type.optional_fields   # ['PIXSCALE']
my_type.all_field_names   # ['METHOD', 'PIXSCALE']
my_type.fields            # {'METHOD': Field(...), 'PIXSCALE': Field(...)}
```

**Parameters:**

- `name` (str) — Entry type name. Automatically converted to uppercase. Max 8 characters recommended.
- `description` (str) — What this entry type represents.
- `fields` (list of Field) — The fields this entry type accepts.

**Properties:**

- `required_fields` — List of field names that are required.
- `optional_fields` — List of field names that are optional.
- `all_field_names` — List of all recognized field names.

---

#### get_schema(entry_type_name)

Look up an entry type by name.

```python
from fits_history.schemas import get_schema

schema = get_schema('DARKSUB')    # Returns EntryType object
schema = get_schema('darksub')    # Case insensitive — same result
schema = get_schema('BOGUS')      # Returns None
```

**Parameters:**

- `entry_type_name` (str) — The entry type name.

**Returns:** `EntryType` or `None` if not found.

---

#### list_entry_types()

Return all registered entry type names.

```python
from fits_history.schemas import list_entry_types

names = list_entry_types()
# ['ORIGIN', 'DARKSUB', 'FLATSUB', 'BIAS', 'SKYSUB', 'STACK',
#  'WCSCAL', 'PHOTCAL', 'SOFTWARE', 'FILTER', 'COSMIC', 'TRIM', 'PARENT']
```

**Returns:** List of strings.

---

#### register_entry_type(entry_type)

Register a custom entry type for use cases not covered by the 13 defaults.

```python
from fits_history.schemas import register_entry_type, EntryType, Field

custom = EntryType(
    name='RESAMP',
    description='Image resampling.',
    fields=[
        Field('method', 'str', True, 'Resampling method'),
        Field('pixscale', 'float', False, 'Output pixel scale'),
    ]
)
register_entry_type(custom)
```

**Parameters:**

- `entry_type` (EntryType) — The custom entry type to register.

**Raises:** `ValueError` if the name conflicts with an existing entry type.

---

### parser.py

Reads raw HISTORY card strings and returns structured Python objects.

#### HistoryEntry

A single parsed HISTORY entry.

```python
entry.entry_type    # 'DARKSUB'
entry.fields        # {'FILE': 'dark.fits', 'METHOD': 'median', 'SCALE': 1.02}
entry.raw_cards     # ['HISTORY #DARKSUB FILE=dark.fits METHOD=median SCALE=1.02']

entry['FILE']                   # 'dark.fits'
entry.get('METHOD')             # 'median'
entry.get('MISSING', 'default') # 'default'
'FILE' in entry                 # True
'BOGUS' in entry                # False
```

**Attributes:**

- `entry_type` (str) — The entry type name (e.g., `'DARKSUB'`).
- `fields` (dict) — Parsed key-value pairs with types cast according to schema.
- `raw_cards` (list of str) — The original HISTORY card strings.

**Methods:**

- `__getitem__(key)` — Access field by name. Raises `KeyError` if missing.
- `get(key, default=None)` — Access field with fallback default.
- `__contains__(key)` — Check if field exists. Used by `in` operator.

---

#### parse_card(card_text)

Parse a single HISTORY card string.

```python
from fits_history.parser import parse_card

# Machine-readable entry
result = parse_card('HISTORY #DARKSUB FILE=dark.fits METHOD=median')
# Returns: ('DARKSUB', {'FILE': 'dark.fits', 'METHOD': 'median'})

# Continuation card
result = parse_card('HISTORY ## SCALE=1.02 EXPTIME=60.0')
# Returns: ('##', {'SCALE': '1.02', 'EXPTIME': '60.0'})

# Old free-form card
result = parse_card('HISTORY bias subtracted using bias frame')
# Returns: None
```

**Parameters:**

- `card_text` (str) — A single HISTORY card string.

**Returns:** Tuple of `(entry_type, fields_dict)`, `('##', fields_dict)` for continuations, or `None` for non-standard cards.

---

#### parse_history(history_cards)

Parse a list of HISTORY card strings into structured HistoryEntry objects. This is the main parsing function.

```python
from fits_history.parser import parse_history

cards = [
    'HISTORY #DARKSUB FILE=dark.fits METHOD=median',
    'HISTORY #ORIGIN TEL=VLT INST=HAWK-I',
    "HISTORY ## OBS='J. Smith'",
    'HISTORY Old free-form text is skipped',
    'HISTORY #SOFTWARE NAME=DRAGONS VER=3.1.0',
]

entries = parse_history(cards)

len(entries)              # 3 (free-form card was skipped)
entries[0].entry_type     # 'DARKSUB'
entries[1].entry_type     # 'ORIGIN'
entries[1]['OBS']         # 'J. Smith' (merged from ## continuation)
entries[2].entry_type     # 'SOFTWARE'
```

**Parameters:**

- `history_cards` (list of str) — Raw HISTORY card strings from a FITS header.

**Returns:** List of `HistoryEntry` objects.

**Behavior:**

- Cards without `#` prefix are silently skipped (old free-form HISTORY).
- `##` continuation cards are merged into the preceding entry.
- Orphan `##` cards (no preceding entry) are ignored.
- Values are automatically cast to `int` or `float` when the schema specifies it.
- Unknown entry types are parsed with all values kept as strings.

---

### writer.py

Produces compliant 80-character HISTORY card strings from structured data.

#### format_value(value)

Format a single value for a HISTORY card.

```python
from fits_history.writer import format_value

format_value('dark.fits')      # 'dark.fits'
format_value('VLT UT1')        # "'VLT UT1'"    (quoted — contains space)
format_value(3.14)             # '3.14'
format_value(20)               # '20'
format_value("it's")           # "'it''s'"      (escaped quote)
```

**Parameters:**

- `value` — Any value (str, int, float).

**Returns:** Formatted string ready for a HISTORY card.

---

#### format_entry(entry_type, fields)

Format a structured entry into 80-character HISTORY card strings. Automatically splits across `##` continuation cards when needed.

```python
from fits_history.writer import format_entry

# Fits in one card
cards = format_entry('DARKSUB', {'FILE': 'dark.fits', 'METHOD': 'median'})
# ['HISTORY #DARKSUB FILE=dark.fits METHOD=median                               ']

# Automatically splits across continuation cards
cards = format_entry('ORIGIN', {
    'TEL': 'VLT', 'INST': 'HAWK-I', 'SITE': 'Paranal',
    'OBS': 'J. Smith', 'DATE': '2024-01-15T14:30:00', 'PROG': '098.A-0123',
})
# ['HISTORY #ORIGIN TEL=VLT INST=HAWK-I SITE=Paranal OBS=\'J. Smith\'           ',
#  'HISTORY ## DATE=2024-01-15T14:30:00 PROG=098.A-0123                         ']
```

**Parameters:**

- `entry_type` (str) — The entry type name.
- `fields` (dict) — Key-value pairs.

**Returns:** List of 80-character strings.

**Raises:** `ValueError` if any single `KEY=value` fragment exceeds 69 characters (the maximum usable space on a continuation card).

---

#### write_entry(header, entry_type, fields)

Write a structured entry directly into an astropy FITS header.

```python
from astropy.io import fits
from fits_history.writer import write_entry

hdul = fits.open('image.fits', mode='update')
header = hdul[0].header

write_entry(header, 'DARKSUB', {'FILE': 'dark_60s.fits', 'METHOD': 'median'})
write_entry(header, 'SOFTWARE', {'NAME': 'MyPipeline', 'VER': '2.0.0'})

hdul.flush()
hdul.close()
```

**Parameters:**

- `header` (astropy.io.fits.Header) — The FITS header to write to.
- `entry_type` (str) — The entry type name.
- `fields` (dict) — Key-value pairs.

---

#### write_entries(header, entries)

Write multiple entries at once.

```python
from fits_history.writer import write_entries

entries = [
    ('BIAS',    {'FILE': 'bias_master.fits', 'METHOD': 'median'}),
    ('DARKSUB', {'FILE': 'dark_60s.fits', 'METHOD': 'median'}),
    ('FLATSUB', {'FILE': 'flat_K.fits', 'FILTER': 'K'}),
    ('SOFTWARE', {'NAME': 'MyPipeline', 'VER': '2.0.0'}),
]

write_entries(header, entries)
```

**Parameters:**

- `header` (astropy.io.fits.Header) — The FITS header to write to.
- `entries` (list of tuple) — Each tuple is `(entry_type, fields_dict)`.

---

### validator.py

Checks entries against their schemas for compliance.

#### ValidationResult

Result of validating a single entry.

```python
result.entry        # The HistoryEntry that was validated
result.is_valid     # True if no errors (warnings are acceptable)
result.errors       # List of error message strings
result.warnings     # List of warning message strings
result.report()     # Human-readable report string
```

**Properties:**

- `is_valid` (bool) — `True` if there are no errors. Warnings do not affect validity.

**Methods:**

- `add_error(message)` — Add an error.
- `add_warning(message)` — Add a warning.
- `report()` — Returns a formatted string summarizing the result.

---

#### validate_entry(entry)

Validate a single HistoryEntry against its schema.

```python
from fits_history.parser import parse_history
from fits_history.validator import validate_entry

entries = parse_history(['HISTORY #DARKSUB METHOD=median'])
result = validate_entry(entries[0])

result.is_valid     # False
result.errors       # ["Missing required field 'FILE'."]
```

**Checks performed:**

1. Entry type is recognized in the registry (warning if not)
2. All required fields are present (error if missing)
3. Field values match their expected types (error if wrong)
4. No unrecognized fields (warning if found)

**Parameters:**

- `entry` (HistoryEntry) — A parsed entry.

**Returns:** `ValidationResult`.

---

#### validate_history(history_cards)

Parse and validate all machine-readable entries in raw card strings.

```python
from fits_history.validator import validate_history

cards = [
    'HISTORY #DARKSUB FILE=dark.fits',
    'HISTORY #STACK NFRAMES=20',
    'HISTORY Old text ignored',
]

results = validate_history(cards)
# results[0].is_valid = True   (#DARKSUB — FILE present)
# results[1].is_valid = False  (#STACK — missing METHOD)
```

**Parameters:**

- `history_cards` (list of str) — Raw HISTORY card strings.

**Returns:** List of `ValidationResult`.

---

#### validate_header(header)

Validate all entries directly from an astropy FITS header.

```python
from astropy.io import fits
from fits_history.validator import validate_header, print_report

hdul = fits.open('image.fits')
results = validate_header(hdul[0].header)
print_report(results)
```

**Parameters:**

- `header` (astropy.io.fits.Header) — An astropy FITS header.

**Returns:** List of `ValidationResult`.

---

#### print_report(results)

Print a formatted validation report to the console.

```python
from fits_history.validator import validate_history, print_report

results = validate_history(cards)
print_report(results)
```

**Output:**

```
Validation Report
Entries checked: 3
Valid: 2  |  Invalid: 1

#DARKSUB: VALID
  All checks passed.

#STACK: INVALID
  ERROR:   Missing required field 'METHOD'.

#SOFTWARE: VALID
  All checks passed.
```

**Parameters:**

- `results` (list of ValidationResult) — Results from any validate function.

---

## Full Workflow Example

A complete example showing writing, reading back, and validating structured HISTORY in a FITS file:

```python
from astropy.io import fits
import numpy as np
from fits_history.writer import write_entry, write_entries
from fits_history.parser import parse_history
from fits_history.validator import validate_header, print_report


# === CREATE A FITS FILE WITH STRUCTURED HISTORY ===

data = np.zeros((100, 100), dtype=np.float32)
hdu = fits.PrimaryHDU(data)

write_entries(hdu.header, [
    ('ORIGIN',   {'TEL': 'VLT', 'INST': 'HAWK-I', 'SITE': 'Paranal'}),
    ('PARENT',   {'FILE': 'raw_001.fits', 'ROLE': 'science'}),
    ('PARENT',   {'FILE': 'raw_002.fits', 'ROLE': 'science'}),
    ('BIAS',     {'FILE': 'bias_master.fits', 'METHOD': 'median', 'NFRAMES': 50}),
    ('DARKSUB',  {'FILE': 'dark_60s_K.fits', 'METHOD': 'median', 'SCALE': 1.02}),
    ('FLATSUB',  {'FILE': 'flat_K_norm.fits', 'FILTER': 'K', 'METHOD': 'divide'}),
    ('SKYSUB',   {'METHOD': 'median', 'NFRAMES': 5, 'LEVEL': 245.3}),
    ('COSMIC',   {'METHOD': 'lacosmic', 'THRESH': 5.0, 'NREJ': 1523}),
    ('STACK',    {'METHOD': 'sigclip', 'NFRAMES': 20, 'LSIGMA': 3.0, 'HSIGMA': 2.5}),
    ('WCSCAL',   {'CATALOG': 'GAIA-DR3', 'NSTARS': 142, 'RMS': 0.12}),
    ('PHOTCAL',  {'ZP': 25.32, 'FILTER': 'K', 'CATALOG': '2MASS'}),
    ('TRIM',     {'X1': 50, 'X2': 2000, 'Y1': 50, 'Y2': 2000, 'REASON': 'overscan'}),
    ('SOFTWARE', {'NAME': 'MyPipeline', 'VER': '2.0.0', 'LANG': 'Python'}),
])

hdu.writeto('processed_image.fits', overwrite=True)


# === READ IT BACK ===

hdul = fits.open('processed_image.fits')
history_cards = [f"HISTORY {h}" for h in hdul[0].header.get('HISTORY', [])]
entries = parse_history(history_cards)

print(f"Found {len(entries)} structured HISTORY entries:\n")
for entry in entries:
    print(f"  #{entry.entry_type}: {entry.fields}")


# === PROGRAMMATIC QUERIES ===

# "Which dark frame was used?"
for entry in entries:
    if entry.entry_type == 'DARKSUB':
        print(f"\nDark frame: {entry['FILE']}, method: {entry['METHOD']}")

# "List all parent files"
parents = [e['FILE'] for e in entries if e.entry_type == 'PARENT']
print(f"Parent files: {parents}")

# "Was WCS calibration done? What was the RMS?"
for entry in entries:
    if entry.entry_type == 'WCSCAL':
        print(f"WCS: catalog={entry['CATALOG']}, RMS={entry['RMS']} arcsec")


# === VALIDATE ===

results = validate_header(hdul[0].header)
print_report(results)

hdul.close()
```

---

## Extending the Standard

Users can define custom entry types for use cases not covered by the 13 defaults:

```python
from fits_history.schemas import register_entry_type, EntryType, Field

register_entry_type(EntryType(
    name='RESAMP',
    description='Image resampling.',
    fields=[
        Field('method', 'str', True, 'Resampling method'),
        Field('pixscale', 'float', False, 'Output pixel scale (arcsec/pix)'),
        Field('kernel', 'str', False, 'Interpolation kernel'),
    ]
))

# Now the parser, writer, and validator all recognize #RESAMP
```

Custom types must have a unique name that does not conflict with the 13 built-in types.

---

## Running the Tests

```bash
python3 test_fits_history.py
```

The test suite runs 63 tests covering schemas, parser, writer, validator, and full round-trips for all 13 entry types.

---

## Design Decisions

**Why `#` as the prefix?**
It must be a character that never starts a normal HISTORY comment. The `#` character is universally recognized as a structured marker. Old parsers see it as part of the comment text and ignore it.

**Why `##` for continuation instead of `#+ ` or `&`?**
`##` is visually clear as "continuation of the above" and doesn't introduce new special characters. The `&` character is already used by the OGIP CONTINUE convention for long string values — reusing it would create ambiguity.

**Why uppercase keys?**
FITS keywords are uppercase. Making keys uppercase keeps the HISTORY content visually consistent with the rest of the FITS header.

**Why raise an error for oversized values instead of splitting them?**
Splitting values across cards (like OGIP CONTINUE does) adds complexity to both the writer and parser, and the whole point of this standard is simplicity. The 69-character limit per value is generous for most metadata. If a value truly needs more space, the user should reconsider their data model.

**Why warnings instead of errors for unknown types and extra fields?**
The standard must be extensible. Treating unknown types or extra fields as errors would break forward compatibility — a parser running an older version of the standard would reject entries from a newer version.
