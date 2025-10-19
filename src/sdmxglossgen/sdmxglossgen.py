# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

# sdmxglossgen.py
from datetime import date
from rdflib import Namespace
from .loadparser import loader_parse_xml_ttl_from_url
from .xml_extractor import extract_xml_content
from .cl_concept_writer import write_codelist_csv
from .logic_triplets import process_concepts
from .tuning import compare_ID
from .gen_template import XML_URL, OLD_MODEL_URL, NEW_MODEL_DOC, NEW_MODEL_URL, NEW_PREF

def parse_xml_to_ttl_from_url(ttl_output, codelist_output, tuning_output, comment_output, include_context=False, tuning = True):
    """
    Main function for parsing XML, loading the old model, and generating a new RDF model.

    Parameters:
    ----------
    :param XML_URL: str
        URL of the XML document containing the source concepts.
    :param OLD_MODEL_URL: str
        URL of the old model in Turtle format, used for comparison.
    :param NEW_MODEL_DOC: str
        URL of the new model documentation.
    :param NEW_MODEL_URL: str
        URL of the new model to be created.
    :param ttl_output: str
        Path to save the generated Turtle file (TTL).
    :param codelist_output: str
        Path to save the CSV file with codelist associations.
    :param tuning_output: str
        Path to save the file with additional data for tuning.
    :param comment_output: str
        Path to save comments about concepts (for translation).
    :param include_context: bool, optional
        Flag indicating whether to include contextual annotations in the model (default `False`).
    :param tuning: bool, optional
        Flag to enable tuning mode, which records additional data about concepts (default `True`).

    Return value:
    -------------
    :return: Tuple[int, int]
        A tuple of two values:
        1. Number of processed concepts.
        2. Total number of `skos:broader` relations found in the concepts.

    Description:
    ------------
    1. Loads the XML document and RDF graph of the old model.
    2. Defines namespaces for XML and RDF data processing.
    3. Extracts concepts from the XML document.
    4. Builds the new RDF model, including prefixes, concept scheme, and relations between concepts.
    5. Writes the RDF model in Turtle format.
    6. Creates a CSV file with codelist associations.
    7. Performs tuning and compares concept IDs between the new and old model.
    8. Outputs a list of concepts that can be further analyzed for matching with the old model.

    Example usage:
    --------------
    >>> parse_xml_to_ttl_from_url(
    ...     "https://example.com/concepts.xml",
    ...     "https://example.com/old_model.ttl",
    ...     "https://example.com/new_model_doc",
    ...     "https://example.com/new_model",
    ...     "output.ttl",
    ...     "codelist.csv",
    ...     "tuning_output.txt",
    ...     "comments.txt",
    ...     include_context=True,
    ...     tuning=True
    ... )

    Limitations:
    ------------
    - Requires the availability of the XML file and the old RDF model.
    - May take significant time when processing a large number of concepts.

    Dependencies:
    -------------
    - datetime.date
    - rdflib.Namespace
    - loader_parse_xml_ttl_from_url (from loadparser)
    - extract_xml_content (from xml_extractor)
    - write_codelist_csv (from cl_concept_writer)
    - process_concepts (from logic_triplets)
    - compare_ID (from tuning)
    """

    # 1. Load data: XML and old model
    root, old_graph = loader_parse_xml_ttl_from_url(XML_URL, OLD_MODEL_URL)

    # 2. Define namespaces for XML and RDF

    SDMX = Namespace("http://www.sdmx.org/resources/sdmxml/schemas/v3_0/structure")
    SDMX_CONCEPT = Namespace(OLD_MODEL_URL)
    SDMX_COMMON = Namespace("http://www.sdmx.org/resources/sdmxml/schemas/v3_0/common")
    NEW_NS = Namespace(NEW_MODEL_URL)
    DCTERMS = Namespace("http://purl.org/dc/terms/")

    NAMESPACES = {'str': SDMX, 'com': SDMX_COMMON}

    # 3. Process XML to extract concepts
    concepts = extract_xml_content(root, NAMESPACES)

    # 4. Prepare prefixes for the Turtle file of the new model

    PREFIXES = f"""
    @prefix rdf:           <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:          <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:           <http://www.w3.org/2001/XMLSchema#> .
@prefix dcterms:       <{DCTERMS}> .
@prefix foaf:          <http://xmlns.com/foaf/0.1/> .
@prefix skos:          <http://www.w3.org/2004/02/skos/core#> .
@prefix sdmx-concept:  <{SDMX_CONCEPT}> .
@prefix {NEW_PREF}-concept:   <{NEW_NS}> .
    """.strip()

    # 5. Define the concept scheme for the new model
    current_date = date.today().isoformat()
    rdf_template = f'''
dcterms:creator [
    a foaf:Organization ;
    foaf:name "SemanticPro - E-projecting R&D Group" ;
    foaf:homepage <http://www.semanticpro.org>
] ;
dcterms:issued "{current_date}"^^xsd:date .'''
    concept_str = f"{NEW_PREF}-concept:cog a skos:ConceptScheme ; \n" + \
                  "rdfs:label \"Content Oriented Guidelines concept scheme\"@en ; \n" + \
                  f"rdfs:isDefinedBy <{NEW_MODEL_DOC}> ; \n" + \
                  f"dcterms:replaces <{OLD_MODEL_URL}> ; \n" + \
                  "rdfs:comment \"The new model replaces the outdated version from 2009.\"@en ; " + \
                  rdf_template

    concept_scheme = concept_str.strip()

    # 6. Processing and writing results

    print("Wait ...")

    codelist_associations = []

    # Open file for writing additional information during tuning
    t = open(tuning_output, "w", encoding="utf-8") if tuning else None
    # Open file for writing concept definitions and comments for later translation
    c = open(comment_output, "w", encoding="utf-8") if tuning else None

    # Open file for writing the new model
    with open(ttl_output, "w", encoding="utf-8") as f:
        # Write prefixes and concept scheme
        f.write(PREFIXES + "\n\n")
        f.write(concept_scheme + "\n")
        t_concept = 1

        num_broaders = 0
        # Process concepts
        for concept in root.findall(".//str:Concept", NAMESPACES):
            triples, texts, codelist_associations, num_broader = process_concepts(concept, NAMESPACES, include_context, concepts, codelist_associations, old_graph)
            num_broaders += num_broader
            concept_id = concept.get("id")  # Concept ID

            # Write comment before concept
            if concept_id:
                f.write(f"\n# {concept_id}\n")
                if tuning and c:
                    c.write("\n")
            if concept_id and tuning and (num_broader > 0) :
                t.write(f"\n# {t_concept}. {concept_id}  skos:broader - {num_broader}\n")

            # Write triples for the current concept
            f.write(" ;\n".join(triples) + " .\n")
            # Write definitions and comments for the current concept
            if tuning and c:
                c.write(" ;\n".join(texts) + " .\n")

            if concept_id and tuning and t and (num_broader > 0) :
                t.write(" ;\n".join(triples) + " .\n")
                t_concept += 1

            if num_broader == 0:
                f.write(f"\n{NEW_PREF}-concept:cog skos:hasTopConcept {NEW_PREF}-concept:{concept_id} .\n")
        if t:
            t.close()
        if c:
            c.close()
    # 7. Write codelist associations into CSV
    write_codelist_csv(codelist_output, codelist_associations)

    # 8. Tuning alignments with the old model
    if tuning :
        no_match_concepts = "no_match_concepts.ttl"
        filtered_concepts = compare_ID(OLD_MODEL_URL, ttl_output, no_match_concepts)

        if filtered_concepts :
            print("No relations established between the following concepts of the new and old model:")
            for filtered_concept in filtered_concepts:
                print(filtered_concept)

    return t_concept - 1, num_broaders
