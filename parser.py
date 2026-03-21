""" Parser for Machine-Readable FITS HISTORY Cards. """

from .schemas import get_schema




def parse_card(card_text):
    """ Parse a single HISTORY card into its type and raw key-value pairs    """
    content = _strip_history_prefix(card_text)

    if not content.startswith('#'):
        # Old-style free-form HISTORY — not our standard
        return None

    if content.startswith('##'):
        # Continuation card
        remainder = content[2:].strip()
        pairs = _parse_key_value_pairs(remainder)
        return ('##', pairs)

    # Entry card: #TYPE KEY=value ...
    # Find the type name (first word after #)
    remainder = content[1:]  # strip the '#'
    parts = remainder.split(None, 1)  # split into 2 i.e. [TYPE, rest]

    if not parts:
        return None

    entry_type = parts[0].upper()
    kv_string = parts[1] if len(parts) > 1 else ''
    pairs = _parse_key_value_pairs(kv_string)

    return (entry_type, pairs)


def parse_history(history_cards):
    """
    Parse the list of all HISTORY card strings into structured HistoryEntry objects, skips non structured cards.
    """
    entries = []
    current_type = None
    current_fields = {}
    current_raw = []

    for card in history_cards:
        parsed = parse_card(card)

        if parsed is None:
            # Free-form text — finalize any current entry, then skip
            if current_type is not None:
                entry = _finalize_entry(current_type, current_fields, current_raw)
                entries.append(entry)
                current_type = None
                current_fields = {}
                current_raw = []
            continue

        tag, pairs = parsed

        if tag == '##':
            # Continuation — merge into current entry
            if current_type is not None:
                current_fields.update(pairs)
                current_raw.append(card)
            # If no current entry, ignore continuation
            continue

        # New entry card — finalize previous if exists
        if current_type is not None:
            entry = _finalize_entry(current_type, current_fields, current_raw)
            entries.append(entry)

        # Start new entry
        current_type = tag
        current_fields = pairs
        current_raw = [card]

    # Finalize last entry
    if current_type is not None:
        entry = _finalize_entry(current_type, current_fields, current_raw)
        entries.append(entry)

    return entries




"""Check if a HISTORY card is a machine-readable entry (starts with #)."""
def _is_entry_card(card_text):
    content = _strip_history_prefix(card_text)
    return content.startswith('#') and not content.startswith('##')



"""Check if a HISTORY card is a continuation card (starts with ##)."""
def _is_continuation_card(card_text):
    content = _strip_history_prefix(card_text)
    return content.startswith('##')



"""Remove the 'HISTORY ' prefix from a card string."""
def _strip_history_prefix(card_text):
    card_text = card_text.strip()
    if card_text.upper().startswith('HISTORY '):
        return card_text[8:]
    elif card_text.upper().startswith('HISTORY'):
        return card_text[7:]
    return card_text



""" A single parsed HISTORY entry."""
class HistoryEntry:

    def __init__(self, entry_type, fields, raw_cards):
        self.entry_type = entry_type
        self.fields = fields
        self.raw_cards = raw_cards

    def __repr__(self):
        return f"HistoryEntry('{self.entry_type}', {self.fields})"

    def __getitem__(self, key):
        """get a field value by key name."""
        return self.fields[key.upper()]

    def __contains__(self, key):
        """Check if the key exists"""
        return key.upper() in self.fields

    def get(self, key, default=None):
        """Get a field value with a default to None"""
        return self.fields.get(key.upper(), default)


""" Parse KEY=value pairs after the #TYPE pr ## """
def _parse_key_value_pairs(text):
    pairs = {}
    text = text.strip()
    i = 0
    txt_len = len(text)

    while i < txt_len:
        # Skip whitespaces
        while i < txt_len and text[i] == ' ':
            i += 1

        if i >= txt_len:
            break

        # Read key (everything up to '=')
        key_start = i
        while i < txt_len and text[i] != '=':
            i += 1

        if i >= txt_len:
            # No '=' found — malformed, skip rest
            break

        key = text[key_start:i].strip().upper()
        i += 1  # skip '='

        if i >= txt_len:
            # Key with no value
            pairs[key] = ''
            break

        # Read value
        if text[i] == "'":
            # Quoted string value
            i += 1  # skip opening quote
            value_chars = []
            while i < txt_len:
                if text[i] == "'":
                    # Check for escaped quote ('')
                    if i + 1 < txt_len and text[i + 1] == "'":
                        value_chars.append("'")
                        i += 2
                    else:
                        # Closing quote
                        i += 1
                        break
                else:
                    value_chars.append(text[i])
                    i += 1
            pairs[key] = ''.join(value_chars)
        else:
            # Unquoted value — read until next space or end
            value_start = i
            while i < txt_len and text[i] != ' ':
                i += 1
            pairs[key] = text[value_start:i]

    return pairs


def _cast_value(raw_value, dtype):
    """
    Cast a raw string value to the expected type.
    Returns original string if casting fails.
    """
    if dtype == 'int':
        try:
            return int(raw_value)
        except (ValueError, TypeError):
            return raw_value
    elif dtype == 'float':
        try:
            return float(raw_value)
        except (ValueError, TypeError):
            return raw_value
    else:
        return raw_value





def _finalize_entry(entry_type, raw_fields, raw_cards):
    """ Takes in data and makes a HistoryEntry object """
    schema = get_schema(entry_type)

    if schema is None:
        # Unknown type — keep everything as strings
        return HistoryEntry(entry_type, raw_fields, raw_cards)

    # Cast values using schema type info
    cast_fields = {}
    for key, value in raw_fields.items():
        key_upper = key.upper()
        if key_upper in schema.fields:
            field_def = schema.fields[key_upper]
            cast_fields[key_upper] = _cast_value(value, field_def.dtype)
        else:
            # Unrecognized field — keep as string
            cast_fields[key_upper] = value

    return HistoryEntry(entry_type, cast_fields, raw_cards)