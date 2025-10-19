# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

from typing import Dict, List, Tuple, Optional
from xml.etree.ElementTree import Element
from .logic_function import format_literal
from .gen_template import NEW_PREF

def prepair_concepts(
        concept: Element,
        namespaces: Dict[str, str],
        include_context: bool,
        codelist_associations: List[Tuple[str, str]]
) -> Tuple[List[str], List[str], Optional[str], Optional[Element], Optional[Element], List[Element]]:
    """
    Prepares RDF triples for a concept from an XML document.

    Parameters:
    ----------
    :param concept: Element
        XML element representing the concept.
    :param namespaces: Dict[str, str]
        XML namespaces for element lookup.
    :param include_context: bool
        Flag indicating whether to include contextual annotations.
    :param codelist_associations: List[Tuple[str, str]]
        List of pairs (codelist, concept) used to link concepts to codelists.

    Return value:
    -------------
    :return: Tuple[List[str], List[str], Optional[str], Optional[Element], Optional[Element], List[Element]]
        - `triples`: list of strings representing RDF triples of the concept.
        - `texts`: list of strings containing metadata and annotations of the concept.
        - `concept_id`: identifier of the concept (if specified).
        - `concept_name`: XML element containing the concept name.
        - `concept_description`: XML element containing the concept description.
        - `related_terms`: list of XML elements representing related terms.

    Description:
    ------------
    - Extracts `id`, `urn`, `name`, and `description` of the concept.
    - Adds RDF triples for `skos:Concept`, `rdfs:label`, `skos:definition`, and others.
    - Processes annotations `CONTEXT`, `RECOMMENDED_REPRESENTATION`, `CODELIST_ID`, and `RELATED_TERMS`.
    - Fills the `codelist_associations` list with links between concepts and codelists.

    Example usage:
    --------------
    >>> from xml.etree.ElementTree import fromstring
    >>> xml_data = '<Concept id="C1" urn="urn:example:C1"><Name>Concept One</Name><Description>First concept</Description></Concept>'
    >>> concept_element = fromstring(xml_data)
    >>> namespaces = {"com": "http://example.com/ns"}
    >>> triples, texts, concept_id, concept_name, concept_description, related_terms = prepair_concepts(concept_element, namespaces, False, [])
    >>> print(triples)
    ['{NEW_PREF}-concept:C1 a skos:Concept', '    rdfs:label "Concept One"@en', '    skos:definition "First concept"@en', '    skos:notation "urn:example:C1"', '    skos:inScheme {NEW_PREF}-concept:cog']
    """
    concept_id = concept.get("id")
    concept_urn = concept.get("urn")
    concept_name = concept.find("com:Name", namespaces)
    concept_description = concept.find("com:Description", namespaces)

    context_annotation = (
        concept.find(".//com:Annotation[com:AnnotationType='CONTEXT']/com:AnnotationText", namespaces)
        if include_context else None
    )
    recommended_representation = concept.find(
        ".//com:Annotation[com:AnnotationType='RECOMMENDED_REPRESENTATION']/com:AnnotationText", namespaces
    )
    codelist_id = concept.find(
        ".//com:Annotation[com:AnnotationType='CODELIST_ID']/com:AnnotationText", namespaces
    )

    triples = [f"{NEW_PREF}-concept:{concept_id} a skos:Concept"]
    texts = [f"{concept_id}"]

    if concept_name is not None and concept_name.text:
        triples.append(format_literal(concept_name.text, "rdfs:label"))
        texts.append(format_literal(concept_name.text, "rdfs:label"))

    if concept_description is not None and concept_description.text:
        triples.append(format_literal(concept_description.text, "skos:definition"))
        texts.append(format_literal(concept_description.text, "skos:definition"))

    triples.append(f"    skos:notation \"{concept_urn}\"")
    triples.append(f"    skos:inScheme {NEW_PREF}-concept:cog")

    if recommended_representation is not None and recommended_representation.text:
        triples.append(format_literal(f"Recommended representation: {recommended_representation.text}", "skos:note"))

    if codelist_id is not None and codelist_id.text:
        triples.append(format_literal(f"Codelist ID: {codelist_id.text}", "skos:note"))
        codelist_associations.append((codelist_id.text.strip(), concept_id))

    if context_annotation is not None and context_annotation.text:
        triples.append(format_literal(context_annotation.text, "rdfs:comment"))
        texts.append(format_literal(context_annotation.text, "rdfs:comment"))

    related_terms = concept.findall(
        ".//com:Annotation[com:AnnotationType='RELATED_TERMS']/com:AnnotationText", namespaces
    )

    return triples, texts, concept_id, concept_name, concept_description, related_terms
