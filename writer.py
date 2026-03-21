""" Writer for Machine-Readable FITS HISTORY Cards. """

from .schemas import get_schema

HISTORY_PREFIX = 'HISTORY '
CARD_LENGTH = 80
MAX_CONTENT_LENGTH = CARD_LENGTH - len(HISTORY_PREFIX)  # 72 characters usable




def write_entry(header, entry_type, fields):
    """ Write a structured HISTORY entry into an astropy FITS header. """
    cards = format_entry(entry_type, fields)
    for card in cards:
        # Extract just the content after 'HISTORY '
        content = card[len(HISTORY_PREFIX):].rstrip()
        header.add_history(content)


def write_entries(header, entries):
    """ Write multiple structured HISTORY entries into an astropy FITS header. """
    for entry_type, fields in entries:
        write_entry(header, entry_type, fields)


def format_value(value):
    """
    Format a value for writing into a HISTORY card.
    Strings with spaces get single quotes, everything else is unquoted.
    """
    str_value = str(value)
    if ' ' in str_value:
        # Quote it — also escape any single quotes inside
        escaped = str_value.replace("'", "''")
        return f"'{escaped}'"
    return str_value


def format_entry(entry_type, fields):
    """
    Format a single entry into a list of HISTORY card strings.

    Automatically splits across continuation (##) cards
    if the content exceeds 72 characters.
    """
    entry_type = entry_type.upper()

    # Build all KEY=value fragments
    fragments = []
    for key, value in fields.items():
        formatted = format_value(value)
        fragments.append(f"{key.upper()}={formatted}")

    # First card starts with #TYPE
    first_prefix = f"#{entry_type} "
    continuation_prefix = "## "

    cards = []
    current_line = first_prefix
    max_fragment_length = MAX_CONTENT_LENGTH - len(continuation_prefix)
    for fragment in fragments:
        # Check if adding this fragment would exceed the limit
        if len(fragment) > max_fragment_length:
            raise ValueError(
                f"Field '{fragment[:fragment.index('=')]}' value is too long "
                f"({len(fragment)} chars, max {max_fragment_length}). "
                f"Shorten the value or split across multiple entries."
            )
        test_line = current_line + fragment

        if len(test_line) <= MAX_CONTENT_LENGTH:
            # If fits (no pun intended) — add it
            current_line = test_line + " "
        else:
            # Doesn't fit — flush current line and start a continuation
            if current_line.strip():
                cards.append(_pad_card(current_line.rstrip()))

            current_line = continuation_prefix + fragment + " "

    # Flush the last line
    if current_line.strip():
        cards.append(_pad_card(current_line.rstrip()))

    return cards


def _pad_card(content):
    """ Pad a HISTORY card content to exactly 80 characters. """
    full_card = HISTORY_PREFIX + content
    if len(full_card) > CARD_LENGTH:
        raise ValueError(
            f"Card content too long ({len(full_card)} chars): {full_card[:50]}..."
        )
    # Padding the back
    return full_card.ljust(CARD_LENGTH)

