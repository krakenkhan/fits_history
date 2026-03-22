"""
SYNTAX RULES:
    HISTORY #TYPE key=value key=value
    HISTORY ## key=value key=value        (continuation)
 
    - '#' at column 9 signals a machine-readable entry
    - '##' signals a continuation of the previous entry
    - Keys are uppercase, alphanumeric + underscore
    - Values with spaces are wrapped in single quotes: key='some value'
    - Values without spaces can be unquoted: key=3.14
"""
class Field:
    """Defines a single field within an entry type schema."""
 
    def __init__(self, name, dtype, required, description):
        '''Parameters:'''
        self.name = name.upper()
        self.dtype = dtype
        self.required = required
        self.description = description
 
    def __repr__(self):
        if self.required:
            req = "required"
        else:
            req = "optional"
        return f"Field('{self.name}', {self.dtype}, {req})"
 
 
class EntryType:
    """Entry type schema used by all the types"""
 
    def __init__(self, name, description, fields):
        self.name = name.upper()
        self.description = description
        self.fields = {}
        for f in fields:
            """ 'fieldname': FIELD('fieldname', 'dtype', 'req') """
            self.fields[f.name] = f
 
    @property
    def required_fields(self):
        """Return list of field names that are required."""
        return [f.name for f in self.fields.values() if f.required]
 
    @property
    def optional_fields(self):
        """Return list of field names that are optional."""
        return [f.name for f in self.fields.values() if not f.required]
 
    @property
    def all_field_names(self):
        """Return list of all recognized field names."""
        return list(self.fields.keys())
 
    def __repr__(self):
        req = ', '.join(self.required_fields)
        return f"EntryType('{self.name}', required=[{req}])"
 
 

# THE 4 Pre defined STANDARD ENTRY TYPES

 
ORIGIN = EntryType(
    name='ORIGIN',
    description='Where the raw data came from.',
    fields=[
        Field('tel',  'str', True,  'Telescope name'),
        Field('inst', 'str', True,  'Instrument name'),
        Field('site', 'str', False, 'Observatory site'),
        Field('obs',  'str', False, 'Observer name'),
        Field('date', 'str', False, 'Observation date (ISO 8601)'),
        Field('prog', 'str', False, 'Program/proposal ID'),
    ]
)
 
SOFTWARE = EntryType(
    name='SOFTWARE',
    description='Processing software used.',
    fields=[
        Field('name', 'str', True,  'Software name'),
        Field('ver',  'str', True,  'Version string'),
        Field('lang', 'str', False, 'Language / platform'),
        Field('ref',  'str', False, 'URL or citation'),
    ]
)
 
FILTER = EntryType(
    name='FILTER',
    description='Filtering / smoothing applied.',
    fields=[
        Field('type',   'str',   True,  'Type: gaussian / median / boxcar / butterworth'),
        Field('size',   'float', True,  'Kernel size (pixels)'),
        Field('kernel', 'str',   False, 'Custom kernel name or shape'),
        Field('axis',   'str',   False, 'Axis filtered: x / y / both'),
    ]
) 
PARENT = EntryType(
    name='PARENT',
    description='Links to source file(s).',
    fields=[
        Field('file',     'str', True,  'Source filename'),
        Field('hdu',      'int', False, 'HDU index in source file'),
        Field('role',     'str', False, 'Role: science / calibration / reference'),
        Field('checksum', 'str', False, 'File checksum for verification'),
    ]
)
 
 
# SCHEMA REGISTRY
# Central lookup: maps entry type name -> EntryType object.
 
REGISTRY = {
    'ORIGIN':  ORIGIN,
    'SOFTWARE': SOFTWARE,
    'FILTER':  FILTER,
    'PARENT':  PARENT,
}
 
 
def get_schema(entry_type_name):
    """ Look up an entry type by name """

    return REGISTRY.get(entry_type_name.upper())
 
 
def list_entry_types():
    """Return a list of all registered entry type names."""
    return list(REGISTRY.keys())
 
 
def register_entry_type(entry_type):
    """ Register a custom entry type."""
    if entry_type.name in REGISTRY:
        raise ValueError(
            f"Entry type '{entry_type.name}' already exists in the registry. "
            f"Use a different name for custom types."
        )
    REGISTRY[entry_type.name] = entry_type
    
    
# The 4 built-in types that cannot be deleted
BUILTIN_TYPES = set(REGISTRY.keys())


def unregister_entry_type(name):
    """ Remove a custom entry type from the registry. """
    name = name.upper()
    if name in BUILTIN_TYPES:
        raise ValueError(
            f"Cannot remove built-in entry type '{name}'."
        )
    if name not in REGISTRY:
        raise KeyError(
            f"Entry type '{name}' not found in the registry."
        )
    del REGISTRY[name]