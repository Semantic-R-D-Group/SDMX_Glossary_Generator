# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

from src.sdmxglossgen.sdmxglossgen import parse_xml_to_ttl_from_url

if __name__ == '__main__':

    # Define output files
    ttl_output = "SDMX_Glossary.ttl"
    codelist_output = "codelist_associations.csv"

    tuning = True  # For fine-tuning skos:broader
    tuning_output = "tuning_res.ttl"

    comment_output = "comment_output.txt" # For further translation

    # Run the function
    t_concept, num_broaders = parse_xml_to_ttl_from_url(ttl_output, codelist_output, tuning_output, comment_output, include_context=True, tuning=tuning)

    print(f"Semantic model saved to {ttl_output}")
    print(f"Codelist associations saved to {codelist_output}")
    if tuning :
        print(f"{t_concept} concepts for skos:broader({num_broaders})-tuning saved to {tuning_output}")


