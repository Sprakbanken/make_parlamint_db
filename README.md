# Make Parlamint database

Code for making an SQLITE database with the Parlamint-NO data. This is work in progress.

## Steps to make the database
1. Download and extract "v1.2_ParlaMint-NO.TEI.tar.gz" from [The Språkbanken repository](https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-77/)
2. Initialize the database: ```python initialize_pm_database.py /path/to/sqlite/database.db```
3. Populate the datavase: ```python populate_pm_database.py /path/to/sqlite/database.db -d /path/to/parlamint/root/folder```

Example code for extracting transcriptions can be found in ```extract_transcriptions.py```