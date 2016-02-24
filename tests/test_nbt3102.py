#!/usr/bin/env python
"""Run a Gene Ontology Enrichment Analysis (GOEA), plots, etc.

    Nature 2014_0126; 
			Computational analysis of cell-to-cell heterogeneity
      in single-cell RNA-sequencing data reveals hidden
      subpopulations of cells
    http://www.nature.com/nbt/journal/v33/n2/full/nbt.3102.html#methods

		     ... revealed a significant enrichment in the set
         of 401 genes that were differentially expressed
         between the identified clusters (P = 0.001
         Hypergeometric Test). Further, Gene Ontology (GO)
         enrichment analysis showed that the differentially
         expressed genes contained statistically
         significant enrichments of genes involved in:
             * glycolysis 
             * cellular response to IL-4 stimulation
               NOW: BP GO:0071353 1.668e-03 D06 cellular response to interleukin-4 (5 genes)
                  * BP GO:0070670: response to interleukin-4
                  * BP GO:0071353: cellular response to interleukin-4
             * positive regulation of B-cell proliferation 
               NOW: BP GO:0030890 2.706e-04 D09 positive regulation of B cell proliferation (7 genes)

         * 401 genes: Supplementary table 4
           http://www.nature.com/nbt/journal/v33/n2/extref/nbt.3102-S4.xlsx
         * GO enrichment results are in: Supplementary table 6
           http://www.nature.com/nbt/journal/v33/n2/extref/nbt.3102-S6.xlsx
"""
import os
import sys
import xlrd

from PyBiocode.dnld.NCBI.genes_NCBI_mus_ProteinCoding import GeneID2nt as GeneID2nt_mus
from goatools.obo_parser import GODag
from goatools.go_enrichment import GOEnrichmentStudy
from goatools.associations import get_assoc_ncbi_taxids

def test_example(log=sys.stdout):
    """Run Gene Ontology Enrichment Analysis (GOEA) on Nature data."""
    # Load ontologies, associations, and population ids
    geneids_pop = GeneID2nt_mus.keys()
    geneids_study = get_geneids("nbt.3102-S4_GeneIDs.xlsx", log)
    goeaobj = get_goeaobj("fdr_bh", geneids_pop)
    # Run GOEA on study
    keep_if = lambda nt: nt.p_fdr_bh < 0.05 # if results are significant
    goea_results = goeaobj.run_study(geneids_study, keep_if=keep_if)
    geneids = goeaobj.get_study_items(goea_results)
    # Print GOEA results to xlsx and screen
    #prtfmt = "{NS} {GO} {p_fdr_bh:5.3e} D{depth:02} {name} ({study_count} genes)\n"
    #goeaobj.prt_txt(sys.stdout, goea_results, prtfmt)
    goeaobj.wr_xlsx("nbt3102.xlsx", goea_results)
    goeaobj.plot("nbt3102_{NS}.png", goea_results)
    log.write("{N} genes associated with {M} significant results\n".format(
        N=len(geneids), M=len(goea_results)))

def get_goeaobj(method, geneids_pop):
    """Load: ontologies, associations, and population geneids."""
    fin_obo = "go-basic.obo"
    if not os.path.isfile(fin_obo):
        os.system("wget http://geneontology.org/ontology/go-basic.obo") 
    obo_dag = GODag(fin_obo)
    assoc_geneid2gos = get_assoc_ncbi_taxids([10090])
    goeaobj = GOEnrichmentStudy(
        geneids_pop,
        assoc_geneid2gos,
        obo_dag,
        propagate_counts = False,
        alpha = 0.05,
        methods = [method])
    return goeaobj

def get_geneids(fin_xlsx, log):
    """Return Entrez GeneIDs for Nature gene list."""
    sym_gis_pval_lst = get_tbl_data(fin_xlsx, log)
    # All Entrez GeneIDs
    geneids_all = [g for s, g, p in sym_gis_pval_lst if g]
    # Keep protein-coding Entrez GeneIDs
    return set(geneids_all).intersection(set(GeneID2nt_mus.keys()))

def get_tbl_data(fin_xlsx, log):
    """Read xlsx file."""
    data_dir = os.path.dirname(os.path.abspath(__file__)) + "/data/nbt_3102"
    tbl_genes = "{DIR}/{FIN}".format(DIR=data_dir, FIN=fin_xlsx)
    book = xlrd.open_workbook(tbl_genes)
    pg = book.sheet_by_index(0)
    gene_pval_lst = [[pg.cell_value(r, c) for c in range(pg.ncols)] for r in range(pg.nrows)]
    log.write("  READ: {N:>3} items {FIN}\n".format(FIN=fin_xlsx, N=len(gene_pval_lst)))
    return gene_pval_lst
    #tbl_gos= "{DIR}/nbt.3102-S6.xlsx".format(DIR=data_dir)
    
if __name__ == '__main__':
    test_example()
