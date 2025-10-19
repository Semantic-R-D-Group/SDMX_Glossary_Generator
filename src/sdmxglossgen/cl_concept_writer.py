# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

import csv
import operator
from pathlib import Path
from typing import List, Tuple

def write_codelist_csv(codelist_output: str, codelist_associations: List[Tuple[str, str]]) -> None:
    """
    Writes associations of codelists and concepts into a CSV file.

    Parameters:
    ----------
    :param codelist_output: str
        Path to the output CSV file where the information will be saved.
    :param codelist_associations: List[Tuple[str, str]]
        List of associations between codelists and concepts as tuples (Codelist ID, Concept ID).

    Description:
    ------------
    - Sorts the associations by codelist identifier (`Codelist ID`).
    - Writes the data into a CSV file with headers `"Codelist ID"` and `"Concept ID"`.

    Return value:
    -------------
    :return: None
        The function writes data into the file and does not return any values.

    Example usage:
    --------------
    >>> codelist_associations = [
    ...     ("CL_001", "C1"),
    ...     ("CL_002", "C2"),
    ...     ("CL_001", "C3")
    ... ]
    >>> write_codelist_csv("output.csv", codelist_associations)

    After execution, `output.csv` will be created with the following content:
    ```
    Codelist ID,Concept ID
    CL_001,C1
    CL_001,C3
    CL_002,C2
    ```
    """
    # Sort associations by Codelist ID
    sorted_associations = sorted(codelist_associations, key=operator.itemgetter(0))

    output_path = Path(codelist_output)
    with output_path.open("w", encoding="utf-8", newline="") as csvfile:
        fieldnames = ["Codelist ID", "Concept ID"]
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvwriter.writeheader()
        for codelist, concept_id in sorted_associations:
            csvwriter.writerow({"Codelist ID": codelist, "Concept ID": concept_id})
