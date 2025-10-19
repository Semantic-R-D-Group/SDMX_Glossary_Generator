# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

from typing import Dict

# Dictionary of concept label corrections
LABEL_FIXES: Dict[str, str] = {
    "timelinesst": "timeliness", # Error in the old model
    "coherence - cross-domain": "coherence - cross domain",  # Error in the new model
    "relevance - user satisifaction": "relevance - user satisfaction",  # Typo corrected

    # Changes in concept names between models (not errors)
    "asymmetry for mirror flow statistics": "asymmetry for mirror flows statistics - coefficient",
    "contact mail": "contact mail address",
    "sdmx registry interface": "sdmx registry interface (in the context of registry)",
    "contact organization unit": "contact organisation unit",
    "observation": "observation value",
    "data presentation": "data presentation - detailed description",
    "frequency": "frequency of observation",
    "contact person job title": "contact person function",
    "accuracy - sampling error": "sampling error",
    "quality management - assessment": "quality management - quality assessment",
    "coverage- time": "time coverage"
}

# Dictionary of hierarchical skos:broader relations
BROADER_FIXES: Dict[str, str] = {
    "DSD": "DATA_SET",
    "ATTRIBUTE": "DSD",
    "DIMENSION": "DSD",
    "MEASURE": "DSD",
    "CODING_FORMAT": "CODE",
    "CONSTRAINT": "CODELIST",
    "ORGANISATION_UNIT": "CONTACT",
    "CDC": "COG",
    "CDCL": "COG",
    "STAT_SUBJECT_MATTER": "COG",
    "LEVEL": "HIERARCHY",
    "MEMBER_SEL": "CONSTRAINT",
    "MSD": "META_SET",
    "REP_CATEGORY": "REPRESENT",
    "REP_TAXO": "REP_CATEGORY",
    "SDMX_REG_INTERFACE": "SDMX_REG",
    "SERIES_KEY": "SIBLING_GR",
    "STRUCT_VALIDATION": "STRUCT_META",
    "TIMELAG_FINAL": "TIMELINESS",
    "TIMELAG_FIRST": "TIMELINESS",

    # Empty values mean keeping `skos:related` relations
    "DATAFLOW": "",
    "DATA_VALIDATION": "",
    "HIERARCHY": "",
    "DATA_SET": ""
}

def get_label_fixes() -> Dict[str, str]:
    """
    Returns a dictionary of corrected concept names.

    Description:
    ------------
    This dictionary fixes typos and changes in concept names between
    the old and the new model. It is used to ensure consistency.

    Return value:
    -------------
    :return: Dict[str, str]
        Dictionary where the key is the original concept name
        and the value is the corrected name.

    Example:
    --------
    >>> get_label_fixes()["timelinesst"]
    'timeliness'
    """
    return LABEL_FIXES

def get_broader_fixes() -> Dict[str, str]:
    """
    Returns a dictionary of enforced skos:broader relations.

    Description:
    ------------
    Defines parent `skos:broader` relations for concepts
    to correct their position in the hierarchy.

    Return value:
    -------------
    :return: Dict[str, str]
        Dictionary where the key is the concept name
        and the value is its parent concept.

    Example:
    --------
    >>> get_broader_fixes()["DSD"]
    'DATA_SET'
    """
    return BROADER_FIXES
