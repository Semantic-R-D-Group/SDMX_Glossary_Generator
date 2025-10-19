# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

# logic_triplets.py
from rdflib.namespace import RDF, RDFS, SKOS
from .logic_function import normalize_label, normalize_text, transform_concept_id, split_by_separator, find_first_difference
from .logic_templates import get_broader_fixes
from .logic_prepair import prepair_concepts
from .gen_template import NEW_PREF

def process_concepts(concept, namespaces, include_context, concepts, codelist_associations, old_graph, narrow_include=False):
    """
    Processes concepts by determining their relationships: `skos:broader`, `skos:narrower`, `skos:related`
    and alignment with old concepts via `skos:exactMatch` and `skos:closeMatch`.

    Parameters:
    ----------
    :param concept: Element
        XML element of the concept.
    :param namespaces: Dict[str, str]
        XML namespaces.
    :param include_context: bool
        Flag to include contextual annotation.
    :param concepts: Dict[str, Tuple[str, str]]
        Dictionary of all concepts with their labels and descriptions.
    :param codelist_associations: List[Tuple[str, str]]
        List of associations between codelists and concepts.
    :param old_graph: Graph
        RDF graph of the old model used for concept alignment.
    :param narrow_include: bool, optional
        Whether to include `skos:narrower` if a `skos:broader` is found (default `False`).

    Return value:
    -------------
    :return: Tuple[List[str], List[str], List[Tuple[str, str]], int]
        - `triples`: list of strings with RDF triples of the concept.
        - `texts`: list of strings with annotations of the concept.
        - `codelist_associations`: updated list of associations between codelists and concepts.
        - `num_broader`: number of found `skos:broader` relations.

    Description:
    ------------
    - **Processes RDF triples of the concept** (using `prepair_concepts`).
    - **Normalizes labels and descriptions** of concepts for further analysis.
    - **Determines relationships** `skos:broader`, `skos:narrower`, `skos:related` based on labels and descriptions.
    - **Uses exceptions** from `get_broader_fixes()` to establish predefined `skos:broader` links.
    - **Compares concepts with old model data** and adds `skos:exactMatch` or `skos:closeMatch`.

    Example usage:
    --------------
    >>> from xml.etree.ElementTree import fromstring
    >>> from rdflib import Graph
    >>> xml_data = '''
    ... <Concept id="C1">
    ...     <Name>Concept One</Name>
    ...     <Description>First concept description.</Description>
    ... </Concept>
    ... '''
    >>> namespaces = {}
    >>> root = fromstring(xml_data)
    >>> concepts = {"C1": ("Concept One", "first concept description")}
    >>> old_graph = Graph()
    >>> codelist_associations = []
    >>> triples, texts, codelist_associations, num_broader = process_concepts(root, namespaces, False, concepts, codelist_associations, old_graph)
    >>> print(triples)
    ['{NEW_PREF}-concept:C1 a skos:Concept', '    rdfs:label "Concept One"@en', '    skos:definition "First concept description"@en', '    skos:notation "urn:example:C1"', '    skos:inScheme {NEW_PREF}-concept:cog']

    Possible issues:
    ----------------
    - **Cyclic references** (`concept_id == related_concept_id`) are ignored.
    - If `related_label` is not found in `concepts`, a warning is displayed.

    Dependencies:
    -------------
    - rdflib (RDF, RDFS, SKOS)
    - logic_function (normalize_label, normalize_text, transform_concept_id, split_by_separator, find_first_difference)
    - logic_templates (get_broader_fixes)
    - logic_prepair (prepair_concepts)
    """


    triples, texts, concept_id, concept_name, concept_description, related_terms = prepair_concepts(concept, namespaces, include_context, codelist_associations)

    # Normalize concept labels and descriptions
    normalized_concept_label = normalize_text(concept_name.text) if concept_name is not None else ""
    normalized_concept_description = normalize_text(
        concept_description.text) if concept_description is not None else ""

    # Build dictionaries of concept_labels and concept_descriptions for further analysis
    concept_labels = {label.strip().lower(): conceptID for conceptID, (label, description) in concepts.items() if label is not None}
    concept_descriptions = {conceptID: description for conceptID, (_, description) in concepts.items() if description}

    num_broader = 0

    for related_term in related_terms:
        related_labels = [normalize_label(term.strip()) for term in related_term.text.split(";")]
        for related_label in related_labels:
            if related_label in concept_labels:
                related_concept_id = concept_labels[related_label]
                related_concept_uri = f"{NEW_PREF}-concept:{related_concept_id}"

                # Exclude relations where the concept refers to itself
                if concept_id == related_concept_id:
                    print(f"Warning: Circular reference in related term {related_concept_id}")
                    continue

                # Determine relation type based on description
                # Normalize labels and descriptions of related concepts
                normalized_related_label = normalize_text(related_label)
                normalized_related_description = normalize_text(
                    concept_descriptions.get(related_concept_id, "")) if concept_description is not None else ""

                # Check conditions
                broader_condition = False
                narrower_condition = False
                broader_exception = False

                # Process exceptions
                broader_corrections = get_broader_fixes()

                if concept_id in broader_corrections:
                    broader_exception = True
                    for key, value in broader_corrections.items():
                        if not value:  # Check if the value is an empty string
                            break
                        if key == concept_id and value == related_concept_id:
                            broader_condition = True
                            break

                # Analyze labels of type "Accuracy - overall"
                if (concept_name is not None) and (not broader_condition) and (not broader_exception):
                    numb_sep, label1, label2 = split_by_separator(concept_name.text)
                    if numb_sep > 0 :
                        norm_label = normalize_text(label1)
                        for conceptID, data in list(concepts.items()):
                            label, description = data
                            broader_condition = (norm_label == label.strip().lower()) and (f"{NEW_PREF}-concept:" + conceptID == related_concept_uri)
                            if broader_condition :
                                break

                # Search for normalized labels in definitions of related concepts
                if not broader_condition and (not broader_exception) :
                    broader_condition = normalized_related_label in normalized_concept_description
                narrower_condition = normalized_concept_label in normalized_related_description

                # Add triples
                if broader_condition and narrower_condition:
                    triples.append(f"    skos:broader {related_concept_uri}")
                    num_broader += 1
                    if narrow_include:
                        triples.append(f"    skos:narrower {related_concept_uri}")
                        print(
                            f"Diagnostic: Both skos:broader and skos:narrower are applicable for {concept_id} and {related_concept_id}")
                elif broader_condition:
                    triples.append(f"    skos:broader {related_concept_uri}")
                    num_broader += 1
                elif narrower_condition and narrow_include :
                    triples.append(f"    skos:narrower {related_concept_uri}")
                else:
                    triples.append(f"    skos:related {related_concept_uri}")
            else:
                print(f"Warning: Related concept '{related_label}' not found for {concept_id}")

    # Align with concepts from the old model (exactMatch, closeMatch)
    for old_concept in old_graph.subjects(RDF.type, SKOS.Concept):
        old_label = old_graph.value(old_concept, RDFS.label)
        old_definition = old_graph.value(old_concept, RDFS.comment)
        old_concept_id = old_concept.split("#")[-1]
        old_concept_id_up = transform_concept_id(old_concept_id)      # For comparison with the new concept_id

        if old_label and concept_name is not None:
            labels_match = normalize_label(str(old_label)) == normalize_label(concept_name.text)
            definitions_match = old_definition and concept_description is not None and normalize_label(str(old_definition)) == normalize_label(concept_description.text)
            concept_id_match = old_concept_id_up == concept_id

            old_concept_uri = f"sdmx-concept:{old_concept_id}"

            if concept_id_match and (old_concept_id_up == "ID_FOR_DEBUG") :
                norm_old_label =normalize_label(str(old_label))
                norm_label = normalize_label(concept_name.text)
                dif_num, dif1, dif2 =find_first_difference(norm_old_label, norm_label)
                print("concept_id =", concept_id, norm_old_label, norm_label, labels_match, dif_num, dif1, dif2)

            if (concept_id_match and labels_match) or (concept_id_match and definitions_match):
                triples.append(f"    skos:exactMatch {old_concept_uri}")
            elif labels_match or (old_definition and concept_description and concept_description.text.lower() in str(old_definition).lower()):
                triples.append(f"    skos:closeMatch {old_concept_uri}")

    return triples, texts, codelist_associations, num_broader
