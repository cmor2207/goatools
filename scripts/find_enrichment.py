#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
python find_enrichment.py study.file population.file gene-association.file

This program returns P-values for functional enrichment in a cluster of study
genes using Fisher's exact test, and corrected for multiple testing (including
Bonferroni, Holm, Sidak, and false discovery rate).

About significance cutoff:
--alpha: test-wise alpha; for each GO term, what significance level to apply
        (most often you don't need to change this other than 0.05 or 0.01)
--pval: experiment-wise alpha; for the entire experiment, what significance
        level to apply after Bonferroni correction
"""

__copyright__ = "Copyright (C) 2010-2018, H Tang et al. All rights reserved."
__author__ = "various"

import sys
import os.path as op
from goatools.cli.find_enrichment import get_arg_parser
from goatools.cli.find_enrichment import rd_files
from goatools.cli.find_enrichment import chk_genes
from goatools.cli.find_enrichment import get_objgoea
from goatools.cli.find_enrichment import get_results_sig
from goatools.cli.find_enrichment import prt_results
from goatools.cli.find_enrichment import prt_grouped
from goatools.grouper.read_goids import read_sections

sys.path.insert(0, op.join(op.dirname(__file__), ".."))


def main():
    """Run gene enrichment analysis."""
    args = get_arg_parser()
    study, pop, assoc = rd_files(args.filenames, args.compare, prt=sys.stdout)
    if not args.compare:  # sanity check
        chk_genes(study, pop, args.min_overlap)
    objgoea = get_objgoea(pop, assoc, args)
    results = objgoea.run_study(study)
    # Reduce results to significant results (pval<value)
    if args.pval is not None:
        results = get_results_sig(results, args)
    # Print results in a flat list
    prt_results(results, objgoea, args)
    sections = read_sections(args.sections) if args.sections is not None else None
    prt_grouped(results, objgoea, args)
    # print("AAAAAAAAAAAAAAAAAAAAAAAAA", args)


if __name__ == "__main__":
    main()

# Copyright (C) 2010-2018, H Tang et al. All rights reserved.
