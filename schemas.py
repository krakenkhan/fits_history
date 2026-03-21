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
 
 
# ============================================================
# THE 13 STANDARD ENTRY TYPES
# ============================================================
 
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
 
DARKSUB = EntryType(
    name='DARKSUB',
    description='Dark frame subtraction.',
    fields=[
        Field('file',    'str',   True,  'Dark frame filename'),
        Field('method',  'str',   False, 'Method: median / mean / scaled'),
        Field('scale',   'float', False, 'Scale factor applied'),
        Field('exptime', 'float', False, 'Dark frame exposure time (seconds)'),
    ]
)
 
FLATSUB = EntryType(
    name='FLATSUB',
    description='Flat field correction.',
    fields=[
        Field('file',   'str',   True,  'Flat field filename'),
        Field('filter', 'str',   False, 'Filter band used'),
        Field('method', 'str',   False, 'Method: divide / multiply'),
        Field('norm',   'float', False, 'Normalization value'),
    ]
)
 
BIAS = EntryType(
    name='BIAS',
    description='Bias subtraction.',
    fields=[
        Field('file',    'str', True,  'Bias frame filename'),
        Field('method',  'str', False, 'Method: median / mean'),
        Field('nframes', 'int', False, 'Number of frames in master bias'),
    ]
)
 
SKYSUB = EntryType(
    name='SKYSUB',
    description='Sky subtraction.',
    fields=[
        Field('method',  'str',   True,  'Method: median / model / offset / polynomial'),
        Field('level',   'float', False, 'Sky level subtracted (ADU)'),
        Field('nframes', 'int',   False, 'Number of sky frames used'),
        Field('file',    'str',   False, 'Sky model filename if applicable'),
    ]
)
 
STACK = EntryType(
    name='STACK',
    description='Image combination / stacking.',
    fields=[
        Field('method',  'str',   True,  'Method: median / mean / sigclip / minmax'),
        Field('nframes', 'int',   True,  'Number of input frames'),
        Field('reject',  'str',   False, 'Rejection algorithm'),
        Field('lsigma',  'float', False, 'Lower sigma clipping threshold'),
        Field('hsigma',  'float', False, 'Upper sigma clipping threshold'),
        Field('output',  'str',   False, 'Output filename'),
    ]
)
 
WCSCAL = EntryType(
    name='WCSCAL',
    description='World Coordinate System calibration.',
    fields=[
        Field('catalog', 'str',   True,  'Reference catalog used'),
        Field('nstars',  'int',   False, 'Number of matched stars'),
        Field('rms',     'float', False, 'RMS of fit (arcseconds)'),
        Field('method',  'str',   False, 'Fitting method'),
    ]
)
 
PHOTCAL = EntryType(
    name='PHOTCAL',
    description='Photometric calibration.',
    fields=[
        Field('zp',      'float', True,  'Zero point magnitude'),
        Field('filter',  'str',   True,  'Filter band'),
        Field('catalog', 'str',   False, 'Reference catalog'),
        Field('nstars',  'int',   False, 'Number of standard stars used'),
        Field('extinct', 'float', False, 'Extinction coefficient'),
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
 
COSMIC = EntryType(
    name='COSMIC',
    description='Cosmic ray rejection.',
    fields=[
        Field('method', 'str',   True,  'Method: lacosmic / dcr / crmedian / manual'),
        Field('nrej',   'int',   False, 'Number of pixels rejected'),
        Field('thresh', 'float', False, 'Detection threshold (sigma)'),
        Field('iter',   'int',   False, 'Number of iterations'),
    ]
)
 
TRIM = EntryType(
    name='TRIM',
    description='Image trimming / cropping.',
    fields=[
        Field('x1',     'int', True,  'Start pixel X'),
        Field('x2',     'int', True,  'End pixel X'),
        Field('y1',     'int', True,  'Start pixel Y'),
        Field('y2',     'int', True,  'End pixel Y'),
        Field('reason', 'str', False, 'Reason for trimming'),
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
    'DARKSUB': DARKSUB,
    'FLATSUB': FLATSUB,
    'BIAS':    BIAS,
    'SKYSUB':  SKYSUB,
    'STACK':   STACK,
    'WCSCAL':  WCSCAL,
    'PHOTCAL': PHOTCAL,
    'SOFTWARE': SOFTWARE,
    'FILTER':  FILTER,
    'COSMIC':  COSMIC,
    'TRIM':    TRIM,
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
    
    
# The 13 built-in types that cannot be deleted
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