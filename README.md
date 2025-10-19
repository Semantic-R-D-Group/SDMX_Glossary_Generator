# SDMX Glossary Generator  

## Overview  
**SDMX Glossary Generator** is a Python tool for transforming SDMX glossary concepts from XML into RDF models in Turtle (TTL) format.  
It supports semantic alignment with the outdated 2009 SDMX glossary model, applies label and hierarchy fixes, and produces additional files for manual tuning and analysis.  

## Features  
- Extracts concepts from XML and generates an RDF `skos:ConceptScheme`.  
- Supports semantic relations:  
  - `skos:broader`  
  - `skos:narrower`  
  - `skos:related`  
  - `skos:exactMatch`  
  - `skos:closeMatch`  
- Provides tuning mechanisms:  
  - **LABEL_FIXES** — corrections of typos and terminology changes.  
  - **BROADER_FIXES** — enforced broader hierarchy relations.  
- Exports results to:  
  - **TTL** file with RDF triples.  
  - **CSV** file with code list associations.  
  - Diagnostic files (`tuning_res.ttl`, `no_match_concepts.ttl`).  

## Project Structure  
```
SDMX_Glossary_Generator_3/
├── main.py                      # Entry point script
├── requirements.txt             # Python dependencies
├── codelist_associations.csv    # Code list associations (example output)
├── SDMX_Glossary.ttl            # Generated RDF glossary
├── tuning_res.ttl               # Tuning results
├── no_match_concepts.ttl        # Concepts without matches
├── comment_output.txt           # Processing comments/logs
├── src/
│   ├── __init__.py
│   └── sdmxglossgen/            # Core implementation
│       ├── __init__.py
│       ├── sdmxglossgen.py      # Main logic orchestrator
│       ├── logic_prepair.py     # Concept preparation (labels, descriptions, annotations)
│       ├── logic_triplets.py    # RDF relations (broader, narrower, related, matches)
│       ├── logic_function.py    # Utility functions (normalization, formatting, transforms)
│       ├── logic_templates.py   # Dictionaries for label/hierarchy fixes
│       ├── xml_extractor.py     # XML parser for extracting concepts
│       ├── loadparser.py        # Loader for XML and RDF models
│       ├── tuning.py            # Alignment and tuning between models
│       ├── cl_concept_writer.py # Exports code list associations to CSV
│       └── gen_template.py      # RDF triple string templates
```

## Installation  
1. Clone the repository or extract the archive.  
2. Create and activate a virtual environment (optional but recommended):  
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/Mac
   .venv\Scripts\activate      # Windows
   ```
3. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

## Usage  
Run the generator:  
```bash
python main.py
```

Depending on configuration, the script will:  
- Parse XML with concepts.  
- Align with the outdated SDMX glossary model.  
- Apply label and hierarchy fixes.  
- Write outputs to `.ttl` and `.csv`.  

## Output Files  
- **SDMX_Glossary.ttl** — RDF model of the glossary.  
- **codelist_associations.csv** — code list associations.  
- **tuning_res.ttl** — alignment and tuning results.  
- **no_match_concepts.ttl** — unmatched concepts for manual review.  
- **comment_output.txt** — analysis logs.  

## License

### Code
The source code of this project is licensed under the **Apache License 2.0**.  
See the [LICENSE](LICENSE) file for details.

### Generated data
The generated datasets, RDF/TTL files, and code lists produced by this tool
are licensed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.  
See the [DATA_LICENSE](DATA_LICENSE) file or visit  
<https://creativecommons.org/licenses/by/4.0/> for the full license text.

**Attribution:**  
This project includes or derives from materials © [SDMX Community](https://sdmx.org)  
(Statistical Data and Metadata eXchange).  
Original materials are licensed under CC BY 4.0.  
Modifications by © 2025 *Semantic R&D Group* —  
automatic RDF/TTL generation and semantic enrichment.

### Third-party libraries
This project uses open-source Python packages under permissive licenses  
(BSD, MIT, Apache 2.0, MPL 2.0).  
See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for details.

---

**Summary**

| Component | License | File |
|------------|----------|------|
| Code | Apache-2.0 | [`LICENSE`](LICENSE) |
| Generated data | CC BY 4.0 | [`DATA_LICENSE`](DATA_LICENSE) |
| Third-party libraries | BSD / MIT / Apache / MPL 2.0 | [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md) |
