# codeplug-doc-gen
Documentation generation from codeplug descriptions. This tool reads the catalog of all known 
codeplugs and either generates a complete documentation of these codeplugs or documents the 
differences between codeplugs. 

The generator can create HTML and [Typst](https://github.com/typst/typst) documents. The latter
can be used to create PDF documents. 

## Usage
The following sections describe the command line interface to the documentation generator.

The overall command line interface structure is like
```
codeplug-doc-gen [global options] Command [command options] CatalogFile
```

### Global Options
Irrespective of the command, there are some common global options:

| Option                         | Description                                                                                                       |
|--------------------------------|-------------------------------------------------------------------------------------------------------------------|
| `-h`, `--help`                 | Prints a help message and quits the application.                                                                  |
| `-f FORMAT`, `--format=FORMAT` | Selects the output format. This must be either `html` or `typst`. Default is HTML.                                |
| `-M`, `--multi-document`       | If output format is HTML, splits generated documentation in multiple files. This applies only to HTML generation. |
| `-O PATH`, `--output=PATH`     | Specifies the output directory. Default `.`.                                                                      |
| `Command`                      | What to do. Must be `generate` or `diff`.                                                                         |
| `CatalogFile`                  | Specifies the path to the codeplug calalog XML file.                                                              | 

### Documenting Codeplugs
When generating the documentation for the entire catalog, there are no additional command specific options. Just supply 
`generate` as the command. To generate the codeplug documentation in HTML split over several files run 
```
 codeplug-doc-gen --format=html --multi-document --output=./output/html generate ../codeplugs/catalog.xml
```
To generate a typst docuement (only single-file) run
```
 codeplug-doc-gen --format=typst --output=./output/typst generate ../codeplugs/catalog.xml
```

### Documenting Differences
When reverse engineering a new firmware release, it is hard to remember what changed. To document only differences 
between two codeplugs (or revisions) the `diff` command can be used. The two codeplugs must then be specified as 
command-specific options. 

The codeplug is specified as `MODEL_ID/VERSION_NAME`. E.g. `d168uv/1.07`. To compare releases R20250119 and R20260131 
of the OpenGD77 codeplugs, call
```
codeplug-doc-gen --format=html --output=./output/html diff opengd77/R20250119 opengd77/R20260131 ../codeplugs/catalog.xml
```

## License
codeplug-doc-gen  Copyright (C) 2025 -- 2026  Hannes Matuschek

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.