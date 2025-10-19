**Description of the SDMX Glossary Generation Project** 
# **1. General Overview** 
The project is designed to replace the outdated SDMX glossary model (located at http://purl.org/linked-data/sdmx/2009/concept) with a new one, published at http://purl.semanticpro.org/linked-data/sdmx/concept. The main goal of the project is the automated transformation of concepts from an XML document into an RDF model in Turtle (TTL) format, with adjustments and tuning of correspondences between the new and the outdated models.The developed software is a tool for generating glossaries in RDF Data Cube format, which transforms concepts from XML and the current Turtle model into a new RDF model.
# **2. Project Architecture**
The software consists of the following main modules:
## **2.1 Main script — sdmxglossgen.py**
This module manages the transformation process of concepts (using the other functions):

-   Loads the XML document with source concepts and the RDF graph of the
    outdated model.
-   Defines namespaces for data processing.
-   Extracts concepts from the XML document.
-   Builds the new RDF model:
    -   Creates prefixes for Turtle.
    -   Defines the conceptual scheme (skos:ConceptScheme).
    -   Processes relationships between concepts (skos:broader, skos:narrower, skos:related, skos:exactMatch).
-   Writes the RDF model in Turtle format.
-   Creates a CSV file with codelist associations.
-   Performs tuning (matching concepts with the outdated model).
-   Writes a file with concept annotations for later translation (in tuning mode).
-   Writes a file of new model concepts that have a skos:broader relationship for further analysis (in tuning mode).

**Key function:**

-   `parse_xml_to_ttl_from_url(xml_url, old_model_url, new_model_doc, new_model_url, ...)` — main data processing function.
## **2.2 Concept preparation module — logic_prepair.py**

This module extracts labels, descriptions, and annotations of concepts from XML.

-   Defines concept id, name, and description.
-   Generates RDF triples for skos:Concept.
-   Processes annotations (CONTEXT, RECOMMENDED_REPRESENTATION, CODELIST_ID).

**Key function:**

-   `prepair_concepts(concept, namespaces, include_context, codelist_associations)`
## **2.3 Concept processing module — logic_triplets.py**

This module processes concepts extracted from XML and determines their RDF relationships.

-   Defines relationship types between concepts (skos:broader, skos:narrower, skos:related).
-   Matches new model concepts with the outdated model (skos:exactMatch, skos:closeMatch).
-   Uses templates (logic_templates.py) to fix errors and adjust hierarchy.
-   Generates RDF triples for the new model's concepts. If `include_context=True`, it also adds CONTEXT-type annotations.
-   Produces a list of annotations for later translation (in tuning mode).

**Key function:**

-   `process_concepts(concept, namespaces, include_context, concepts, codelist_associations, old_graph)`
## **2.4 Helper module for RDF and string processing — logic_function.py**

This module provides helper functions for handling strings and concepts:

-   Formats strings for RDF triples (`format_literal`).
-   Splits strings by a separator (`split_by_separator`).
-   Finds differences between strings (`find_first_difference`).
-   Normalizes text (`normalize_text`).
-   Transforms concept identifiers (`transform_concept_id`).
## **2.5 Templates and corrections — logic_templates.py**
-   Contains a dictionary of concept label corrections (LABEL_FIXES).
-   Defines hierarchy (BROADER_FIXES).

**Functions:** 

- `get_label_fixes()` — returns label corrections.
- `get_broader_fixes()` — returns predefined skos:broader relationships.
## **2.6 CSV generation with codelists — cl_concept_writer.py**
Writes mappings between codelists and concepts into CSV.

**Key function:** 

- `write_codelist_csv(codelist_output, codelist_associations)`
## **2.7 Matching tuning module — tuning.py**
Compares concept identifiers between the outdated and the new RDF model, finds mismatches, and saves them.

**Key function:** 

- `compare_ID(old_model_url, new_ttl_path, output_file)`
## **2.8 XML/RDF loading and parsing — loadparser.py**

This module loads the XML document and the RDF graph of the outdated model.

**Key function:** 

- `loader_parse_xml_ttl_from_url(xml_url, old_model_url)`
## **2.9 XML data extraction — xml_extractor.py**
This module parses the XML file and extracts concepts.

**Key function:** 

- `extract_xml_content(root, namespaces)`
# **3. Workflow**

1.  **Load XML and outdated model.**
    
    `loader_parse_xml_ttl_from_url` loads the XML document with concepts and the RDF graph of the old model.

2.  **Extract data from XML.**

    `extract_xml_content` extracts concept id, name, and description.

3.  **Process concepts.**

    `process_concepts` analyzes concepts and determines relationships (skos:broader, skos:narrower, skos:related).

4.  **Generate RDF model.**

    Builds a new skos:ConceptScheme and RDF triples.

5.  **Write to Turtle and CSV.**

    The model is written to a TTL file, codelists — to CSV.

6.  **Tuning and matching analysis.**

    When the `tuning` parameter is specified, files for result analysis are generated, supporting manual correction dictionaries (LABEL_FIXES, BROADER_FIXES).
# **4. Logic of concept and relationship processing**
## **4.1 Concept definition**
`logic_prepair.py` analyzes XML structure of concepts and extracts:

-   Identifier (id)
-   Name
-   Description
-   Additional annotations (context, codelists, recommended representations)

Extracted data is transformed into RDF format:

``` turtle
spr-concept:C1 a skos:Concept ;
    rdfs:label "Concept One"@en ;
    skos:definition "First concept description."@en ;
    skos:notation "urn:example:C1" ;
    skos:inScheme spr-concept:cog .
```
## **4.2 Determining relationships between new model concepts**
`logic_triplets.py` analyzes new model concepts and establishes their relationships:

-   `skos:broader` — broader concept
-   `skos:narrower` — narrower concept (if `narrow_include` is set – planned for future use)
-   `skos:related` — related concept

Relationship determination is based on analyzing labels, descriptions, and related terms. General rules include:

###### *General logic of relationship detection*

1.  **Semantic analysis of names and descriptions**
    1. If the description of one concept contains the name of another, a broader/narrower relation may exist.
    2. If the label contains a separator (e.g., `" - "`), the first part may indicate broader, the second narrower.
2.  **Annotation analysis in XML**
    1. If XML defines RELATED_TERMS, they may be interpreted as broader, narrower, or related depending on context.
3.  **Use of BROADER\_FIXES dictionary**
    1. If BROADER\_FIXES specifies a value, broader is forced, ignoring general logic.
    2. If value is empty, the concept retains only related relations.

## **4.3 Tuning based on concept label corrections**
During processing, tuning files are analyzed, mismatches identified, and a LABEL_FIXES dictionary is created to correct labels. This addresses typos, terminology changes, and mismatches.

Example corrections: 
- `timelinesst → timeliness` (typo correction)
- `coherence - cross-domain → coherence - cross domain` (format standardization)
- `relevance - user satisifaction → relevance - user satisfaction` (spelling correction)

Example LABEL\_FIXES (logic\_templates.py):

``` python
LABEL_FIXES = {
    "timelinesst": "timeliness",
    "coherence - cross-domain": "coherence - cross domain",
    "relevance - user satisifaction": "relevance - user satisfaction"
}
```

If a concept contains the typo `"timelinesst"`, it is automatically replaced with `"timeliness"`.

## **4.4 Concept hierarchy tuning**
Tuning also creates the BROADER_FIXES dictionary (logic_templates.py), defining forced skos:broader relationships.

Example:

``` python
BROADER_FIXES = {
    "DSD": "DATA_SET",
    "ATTRIBUTE": "DSD",
    "DIMENSION": "DSD",
    "MEASURE": "DSD",
    "ORGANISATION_UNIT": "CONTACT"
}
```

Thus, if `"ATTRIBUTE"` has no explicit skos:broader, it is forced to `"DSD"`, while all other links remain related.
## **4.5 Matching concepts between the new and the outdated model**
Matching the concepts of the new model with those of the old model is performed to determine semantic correspondence. Both automatic text analysis and additional identifier comparison are applied.

###### *General matching logic*
1. **Exact match of normalized names, labels, or descriptions**:  

   If the normalized names (identifiers) and the label (or description) of concepts in the new and old models match, a `skos:exactMatch` relation is established.

2. **Partial match**:  

   If the labels match, or the description of a concept in the new model fully or partially matches the description of a concept in the old model, a `skos:closeMatch` relation is established.

The `tuning.py` module performs additional matching of new model concepts with the outdated model based on the following criteria (without writing triples into the new model):

- `skos:exactMatch` — established if the concept identifier matches a header comment (`#`) in the outdated model, and the labels also match.  
- `skos:closeMatch` — established if the labels of the concepts are similar, but the identifiers differ.  

If concept identifiers in the new and outdated model (comment before the concept, like `# ID`) match but the labels do not, the concept’s triples are written into a separate file `no_match_concepts.ttl`.

-----
# **5. Conclusion**
The project provides a comprehensive solution for updating the SDMX glossary, including:

- Extracting concepts from XML.  
- Building an RDF model with `skos:broader`, `skos:related`, `skos:exactMatch`.  
- Correcting errors and fixing the concept hierarchy.  
- Matching with the outdated model and identifying inconsistencies.  

