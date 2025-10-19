# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

import re
from .logic_templates import get_label_fixes

def format_literal(value: str, predicate: str) -> str:
    """
    Formats a string for use in RDF triples by adding quotes and a language tag.

    Parameters:
    ----------
    :param value: str
        The string to be formatted.
    :param predicate: str
        RDF predicate (e.g., `rdfs:label`, `skos:definition`, etc.).

    Return value:
    -------------
    :return: str
        A string containing the correct RDF triple representation.

    Example usage:
    --------------
    >>> format_literal("Example Concept", "rdfs:label")
    '    rdfs:label "Example Concept"@en'

    >>> format_literal('Concept with "quotes"', "skos:definition")
    '    skos:definition \"""Concept with "quotes\"\""\"@en'
    """
    value = value.strip()
    if '"' in value:
        return f'    {predicate} """{value}"""@en'
    return f'    {predicate} "{value}"@en'

def split_by_separator(s):
    """
    Splits a string by the first occurrence of the separator " - ".

    Parameters:
    ----------
    :param s: str
        Input string to split.

    Return value:
    -------------
    :return: Tuple[int, str, str]
        - Position of the separator (if found, otherwise -1).
        - First part of the string before the separator.
        - Second part of the string after the separator.

    Example usage:
    --------------
    >>> split_by_separator("concept - definition")
    (7, 'concept', 'definition')

    >>> split_by_separator("no separator here")
    (-1, '', '')
    """
    separator = " - "
    pos = s.find(separator)
    if pos != -1:
        part1, part2 = s[:pos], s[pos + len(separator):]
        return pos, part1, part2
    return -1, '', ''

def find_first_difference(str1, str2):
    """
    Finds the first difference between two strings.

    Parameters:
    ----------
    :param str1: str
        The first string for comparison.
    :param str2: str
        The second string for comparison.

    Return value:
    -------------
    :return: Tuple[int, str, str]
        - Index of the first difference (if strings are identical, returns -1).
        - Character from `str1` that differs (or the remaining part of the string).
        - Character from `str2` that differs (or the remaining part of the string).

    Example usage:
    --------------
    >>> find_first_difference("quality", "quantity")
    (1, 'u', 'a')

    >>> find_first_difference("same", "same")
    (-1, '', '')
    """
    min_length = min(len(str1), len(str2))
    for i in range(min_length):
        if str1[i] != str2[i]:
            return i, str1[i], str2[i]
    if len(str1) != len(str2):
        return min_length, str1[min_length:] if len(str1) > len(str2) else '', str2[min_length:] if len(str2) > len(str1) else ''
    return -1, '', ''

def normalize_text(text):
    """
    Normalizes text: removes non-alphabetic characters and converts to lowercase.

    Parameters:
    ----------
    :param text: str
        Input text to normalize.

    Return value:
    -------------
    :return: str
        Normalized text without special characters, in lowercase.

    Example usage:
    --------------
    >>> normalize_text("Hello, World! 123")
    'hello world'
    """
    text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
    text = text.lower()
    return ' '.join(text.split())

def normalize_label(label):
    """
    Normalizes a concept label considering predefined fixes.

    Parameters:
    ----------
    :param label: str
        Input concept label.

    Return value:
    -------------
    :return: str
        Corrected and normalized label.

    Example usage:
    --------------
    >>> normalize_label("timelinesst")
    'timeliness'
    """
    label = label.lower().strip()
    return get_label_fixes().get(label, label)

def transform_concept_id(id):
    """
    Transforms a concept identifier by adding underscores before uppercase letters.

    Parameters:
    ----------
    :param id: str
        Original concept identifier.

    Return value:
    -------------
    :return: str
        Transformed identifier in uppercase with underscores.

    Example usage:
    --------------
    >>> transform_concept_id("ConceptID")
    'CONCEPT_ID'
    """
    transformed_id = re.sub(r'(?<!^)([A-Z])', r'_\1', id).upper()
    return transformed_id
