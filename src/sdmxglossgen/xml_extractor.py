# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

import xml.etree.ElementTree as ET
from typing import Dict, Tuple

def extract_xml_content(root: ET.Element, namespaces: Dict[str, str]) -> Dict[str, Tuple[str, str]]:
    """
    Extracts labels and descriptions of concepts from an XML document.

    Parameters:
    ----------
    :param root: ET.Element
        Root XML element containing concepts.
    :param namespaces: Dict[str, str]
        XML namespaces for proper element lookup.

    Return value:
    -------------
    :return: Dict[str, Tuple[str, str]]
        Dictionary where the key is `Concept ID`, and the value is a tuple (`label`, `description`).

    Description:
    ------------
    - The function searches for all `<Concept>` elements in the XML document.
    - Extracts the concept `id`, its `Name`, and `Description`.
    - If `Name` or `Description` are missing, they are replaced with empty strings.
    - Converts the description (`Description`) to lowercase and removes extra spaces.

    Example usage:
    --------------
    >>> from xml.etree.ElementTree import fromstring
    >>> xml_data = '''
    ... <Structure xmlns:str="http://example.com/structure" xmlns:com="http://example.com/common">
    ...     <str:Concept id="C1">
    ...         <com:Name>Concept One</com:Name>
    ...         <com:Description>First concept description.</com:Description>
    ...     </str:Concept>
    ... </Structure>
    ... '''
    >>> root = fromstring(xml_data)
    >>> namespaces = {"str": "http://example.com/structure", "com": "http://example.com/common"}
    >>> extract_xml_content(root, namespaces)
    {'C1': ('Concept One', 'first concept description.')}
    """
    concepts = {}
    for concept in root.findall(".//str:Concept", namespaces):
        concept_id = concept.get("id")
        if concept_id is None:
            continue

        label = concept.find("com:Name", namespaces)
        description = concept.find("com:Description", namespaces)

        normalized_label = label.text if label is not None else ""
        concept_description = description.text.strip().lower() if description is not None else ""

        concepts[concept_id] = (normalized_label, concept_description)

    return concepts
