The Following are the pre-built entry types

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

### #DARKSUB — Dark frame subtraction

| Field   | Required | Type  | Description                        |
| ------- | -------- | ----- | ---------------------------------- |
| FILE    | yes      | str   | Dark frame filename                |
| METHOD  | no       | str   | median / mean / scaled             |
| SCALE   | no       | float | Scale factor applied               |
| EXPTIME | no       | float | Dark frame exposure time (seconds) |

```
HISTORY #DARKSUB FILE=dark_60s_K.fits METHOD=median SCALE=1.02
```

### #FLATSUB — Flat field correction

| Field  | Required | Type  | Description         |
| ------ | -------- | ----- | ------------------- |
| FILE   | yes      | str   | Flat field filename |
| FILTER | no       | str   | Filter band used    |
| METHOD | no       | str   | divide / multiply   |
| NORM   | no       | float | Normalization value |

```
HISTORY #FLATSUB FILE=flat_K_norm.fits FILTER=K METHOD=divide
```

### #BIAS — Bias subtraction

| Field   | Required | Type | Description                     |
| ------- | -------- | ---- | ------------------------------- |
| FILE    | yes      | str  | Bias frame filename             |
| METHOD  | no       | str  | median / mean                   |
| NFRAMES | no       | int  | Number of frames in master bias |

```
HISTORY #BIAS FILE=bias_master.fits METHOD=median NFRAMES=50
```

### #SKYSUB — Sky subtraction

| Field   | Required | Type  | Description                          |
| ------- | -------- | ----- | ------------------------------------ |
| METHOD  | yes      | str   | median / model / offset / polynomial |
| LEVEL   | no       | float | Sky level subtracted (ADU)           |
| NFRAMES | no       | int   | Number of sky frames used            |
| FILE    | no       | str   | Sky model filename if applicable     |

```
HISTORY #SKYSUB METHOD=median NFRAMES=5 LEVEL=245.3
```

### #STACK — Image combination / stacking

| Field   | Required | Type  | Description                      |
| ------- | -------- | ----- | -------------------------------- |
| METHOD  | yes      | str   | median / mean / sigclip / minmax |
| NFRAMES | yes      | int   | Number of input frames           |
| REJECT  | no       | str   | Rejection algorithm              |
| LSIGMA  | no       | float | Lower sigma clipping threshold   |
| HSIGMA  | no       | float | Upper sigma clipping threshold   |
| OUTPUT  | no       | str   | Output filename                  |

```
HISTORY #STACK METHOD=sigclip NFRAMES=20 REJECT=sigclip
HISTORY ## LSIGMA=3.0 HSIGMA=3.0 OUTPUT=mosaic_K.fits
```

### #WCSCAL — World Coordinate System calibration

| Field   | Required | Type  | Description             |
| ------- | -------- | ----- | ----------------------- |
| CATALOG | yes      | str   | Reference catalog used  |
| NSTARS  | no       | int   | Number of matched stars |
| RMS     | no       | float | RMS of fit (arcseconds) |
| METHOD  | no       | str   | Fitting method          |

```
HISTORY #WCSCAL CATALOG=GAIA-DR3 NSTARS=142 RMS=0.12
```

### #PHOTCAL — Photometric calibration

| Field   | Required | Type  | Description                   |
| ------- | -------- | ----- | ----------------------------- |
| ZP      | yes      | float | Zero point magnitude          |
| FILTER  | yes      | str   | Filter band                   |
| CATALOG | no       | str   | Reference catalog             |
| NSTARS  | no       | int   | Number of standard stars used |
| EXTINCT | no       | float | Extinction coefficient        |

```
HISTORY #PHOTCAL ZP=25.32 FILTER=K CATALOG=2MASS NSTARS=15
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

### #COSMIC — Cosmic ray rejection

| Field  | Required | Type  | Description                        |
| ------ | -------- | ----- | ---------------------------------- |
| METHOD | yes      | str   | lacosmic / dcr / crmedian / manual |
| NREJ   | no       | int   | Number of pixels rejected          |
| THRESH | no       | float | Detection threshold (sigma)        |
| ITER   | no       | int   | Number of iterations               |

```
HISTORY #COSMIC METHOD=lacosmic THRESH=5.0 NREJ=1523 ITER=3
```

### #TRIM — Image trimming / cropping

| Field  | Required | Type | Description         |
| ------ | -------- | ---- | ------------------- |
| X1     | yes      | int  | Start pixel X       |
| X2     | yes      | int  | End pixel X         |
| Y1     | yes      | int  | Start pixel Y       |
| Y2     | yes      | int  | End pixel Y         |
| REASON | no       | str  | Reason for trimming |

```
HISTORY #TRIM X1=50 X2=2000 Y1=50 Y2=2000 REASON=overscan
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
