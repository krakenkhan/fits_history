# The Following are the pre-built entry types

### #ORIGIN — Where the raw data came from

| Field | Required | Type | Description                 |
| ----- | -------- | ---- | --------------------------- |
| TEL   | yes      | str  | Telescope name              |
| INST  | yes      | str  | Instrument name             |
| SITE  | no       | str  | Observatory site            |
| OBS   | no       | str  | Observer name               |
| DATE  | no       | str  | Observation date (ISO 8601) |
| PROG  | no       | str  | Program/proposal ID         |

```
HISTORY #ORIGIN TEL=VLT INST=HAWK-I SITE=Paranal
HISTORY ## OBS='J. Smith' DATE=2024-01-15T14:30:00
```

### #SOFTWARE — Processing software used

| Field | Required | Type | Description         |
| ----- | -------- | ---- | ------------------- |
| NAME  | yes      | str  | Software name       |
| VER   | yes      | str  | Version string      |
| LANG  | no       | str  | Language / platform |
| REF   | no       | str  | URL or citation     |

```
HISTORY #SOFTWARE NAME=DRAGONS VER=3.1.0 LANG=Python
```

### #FILTER — Filtering / smoothing applied

| Field  | Required | Type  | Description                              |
| ------ | -------- | ----- | ---------------------------------------- |
| TYPE   | yes      | str   | gaussian / median / boxcar / butterworth |
| SIZE   | yes      | float | Kernel size (pixels)                     |
| KERNEL | no       | str   | Custom kernel name or shape              |
| AXIS   | no       | str   | Axis filtered: x / y / both              |

```
HISTORY #FILTER TYPE=gaussian SIZE=3.5 AXIS=both
```

### #PARENT — Links to source files

| Field    | Required | Type | Description                       |
| -------- | -------- | ---- | --------------------------------- |
| FILE     | yes      | str  | Source filename                   |
| HDU      | no       | int  | HDU index in source file          |
| ROLE     | no       | str  | science / calibration / reference |
| CHECKSUM | no       | str  | File checksum for verification    |

```
HISTORY #PARENT FILE=raw_001.fits ROLE=science
HISTORY #PARENT FILE=std_star.fits ROLE=calibration
```
