# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

import requests
import re
import rdflib
from pathlib import Path
from .gen_template import NEW_PREF

# Function to extract concepts and their comments
def extract_comments_from_text(content: list[str] | list[bytes]) -> set[str]:
    """
    Extracts comments from the provided text content.

    Parameters:
    ----------
    :param content: Iterable[str]
        A sequence of lines containing comments.

    Return value:
    -------------
    :return: Set[str]
        A set of unique comments found in the content.
    """
    comment_pattern = re.compile(r'#\s*(.+)')
    comments = {match.group(1).strip() for line in content if (match := comment_pattern.match(line.decode('utf-8') if isinstance(line, bytes) else line))}
    return comments


def filter_unmatched_concepts(new_ttl_path: str, matched_comments: set[str]) -> tuple[list[tuple[rdflib.URIRef, str]], rdflib.Graph]:
    """
    Filters concepts that have no matches in the new RDF graph.

    Parameters:
    ----------
    :param new_ttl_path: str
        Path to the file containing the new model in Turtle format.
    :param matched_comments: Set[str]
        Set of comments corresponding to concepts.

    Return value:
    -------------
    :return: Tuple[List[Tuple[rdflib.URIRef, str]], rdflib.Graph]
        List of unmatched concepts and the RDF graph.
    """
    new_graph = rdflib.Graph()
    new_graph.parse(new_ttl_path, format="turtle")

    skos = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
    sdmx_concept = rdflib.Namespace("http://purl.semanticpro.org/linked-data/sdmx/concept#")
    filtered_concepts = []

    for comment in matched_comments:
        concept_uri = next((subj for subj in new_graph.subjects(rdflib.RDF.type, skos.Concept) if str(subj).split("/")[-1].replace("concept#", "") == comment), None)
        if concept_uri and not any((concept_uri, prop, None) in new_graph for prop in (skos.closeMatch, skos.exactMatch)):
            filtered_concepts.append((concept_uri, comment))

    return filtered_concepts, new_graph


def save_filtered_concepts(filtered_concepts: list[tuple[rdflib.URIRef, str]], new_graph: rdflib.Graph, output_file: str) -> None:
    """
    Saves the filtered concepts and their triples into a Turtle file.

    Parameters:
    ----------
    :param filtered_concepts: List[Tuple[rdflib.URIRef, str]]
        List of concepts and their comments.
    :param new_graph: rdflib.Graph
        RDF graph containing the concepts.
    :param output_file: str
        Path to the output file.
    """
    output_path = Path(output_file)
    filtered_graph = rdflib.Graph()
    namespaces = {
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        f"{NEW_PREF}-concept": "http://purl.semanticpro.org/linked-data/sdmx/concept#",
        "sdmx-concept": "http://purl.semanticpro.org/linked-data/sdmx/concept#"
    }

    for prefix, uri in namespaces.items():
        filtered_graph.bind(prefix, rdflib.Namespace(uri))

    with output_path.open("w", encoding="utf-8") as f:
        for prefix, uri in namespaces.items():
            f.write(f"@prefix {prefix}: <{uri}> .\n")
        f.write("\n")

        for concept, comment in filtered_concepts:
            concept_name = str(concept).split("/")[-1].replace("concept#", "")
            f.write(f"\n# {concept_name}\n")
            for s, p, o in new_graph.triples((concept, None, None)):
                f.write(f"{s.n3(filtered_graph.namespace_manager)} {p.n3(filtered_graph.namespace_manager)} {o.n3(filtered_graph.namespace_manager)} .\n")
            old_concept_name = comment.lower().replace(" ", "")
            f.write(f"{NEW_PREF}-concept:{concept_name} skos:exactMatch sdmx-concept:{old_concept_name} .\n")

    print(f"Filtered concepts with all triples saved to {output_file}")


def compare_ID(old_model_url: str, new_ttl_path: str, output_file: str) -> list[tuple[rdflib.URIRef, str]] | None:
    """
    Compares concept identifiers between the old and the new RDF models.

    Parameters:
    ----------
    :param old_model_url: str
        URL of the old RDF model in Turtle format.
    :param new_ttl_path: str
        Path to the file containing the new RDF model.
    :param output_file: str
        Path to the file for saving the comparison results.

    Return value:
    -------------
    :return: List[Tuple[rdflib.URIRef, str]]
        List of concepts that have no matches in the old model.
    """
    try:
        old_model_content = [line.decode('utf-8') for line in requests.get(old_model_url, timeout=10).iter_lines()]
    except requests.RequestException as e:
        print(f"Failed to fetch the old model: {e}")
        return None

    new_model_content = Path(new_ttl_path).read_text(encoding="utf-8").splitlines()

    matched_comments = extract_comments_from_text(old_model_content) & extract_comments_from_text(new_model_content)
    filtered_concepts, new_graph = filter_unmatched_concepts(new_ttl_path, matched_comments)
    save_filtered_concepts(filtered_concepts, new_graph, output_file)
    return filtered_concepts
