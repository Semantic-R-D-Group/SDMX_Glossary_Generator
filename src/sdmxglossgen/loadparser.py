# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

import requests
import xml.etree.ElementTree as ET
from rdflib import Graph
from typing import Tuple, Optional

def loader_parse_xml_ttl_from_url(xml_url: str, old_model_url: str) -> Optional[Tuple[ET.Element, Graph]]:
    """
    Loads an XML document and an RDF model in Turtle format from the given URLs.

    Parameters:
    ----------
    :param xml_url: str
        URL to load the XML document.
    :param old_model_url: str
        URL to load the old RDF model in Turtle format.

    Return value:
    -------------
    :return: Optional[Tuple[ET.Element, Graph]]
        A tuple containing:
        - `root`: The root XML element if loading was successful.
        - `old_graph`: RDF graph containing the old model data.
        Returns `None` in case of an error.

    Description:
    ------------
    - Loads the XML file from the specified `XML_URL` and parses it using `xml.etree.ElementTree`.
    - Loads the RDF model from `OLD_MODEL_URL` and parses it in `turtle` format using `rdflib.Graph`.
    - In case of an error (unavailable URL, parsing issues), prints an error message and returns `None`.

    Example usage:
    --------------
    >>> XML_URL = "http://example.com/sample.xml"
    >>> OLD_MODEL_URL = "http://example.com/sample.ttl"
    >>> result = loader_parse_xml_ttl_from_url(XML_URL, OLD_MODEL_URL)
    >>> if result:
    ...     root, old_graph = result
    ...     print("Data successfully loaded and processed.")

    Possible errors:
    ----------------
    - `requests.RequestException`: Error while fetching XML or RDF model.
    - `ET.ParseError`: Error while parsing XML.
    - `ValueError`, `TypeError`: Errors while parsing the RDF model.

    Dependencies:
    -------------
    - `requests`
    - `xml.etree.ElementTree`
    - `rdflib.Graph`
    """
    old_graph = Graph()

    try:
        # Load XML file from URL
        response = requests.get(xml_url, timeout=10)
        response.raise_for_status()  # Check of successful upload
        xml_content = response.content

        # Parse XML
        root = ET.fromstring(xml_content)
    except requests.RequestException as e:
        print(f"Failed to fetch the XML file: {e}")
        return None
    except ET.ParseError as e:
        print(f"Failed to parse the XML content: {e}")
        return None

    try:
        # Load old model via requests
        old_model_response = requests.get(old_model_url, timeout=10)
        old_model_response.raise_for_status()
        old_model_content = old_model_response.text

        # Parse old model
        old_graph.parse(data=old_model_content, format="turtle")
        print("Old model successfully loaded.")
    except requests.RequestException as e:
        print(f"Failed to fetch the old model: {e}")
        return None
    except (ET.ParseError, ValueError, TypeError) as e:
        print(f"Failed to parse the old model: {e}")
        return None

    return root, old_graph
