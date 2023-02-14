from pandas import DataFrame
from numpy import array, mean, zeros, median, diff, divide, zeros_like
from scipy.sparse import csr_matrix
from scipy.stats import gmean, hmean


def mean_per_cell(adata, genes):
        if genes == []:
            return zeros(adata.shape[0])
        return array(mean(adata[:,genes].X, axis=1)).flatten()

def nnzmean_per_cell(adata, genes):
        if genes == []:
            return zeros(adata.shape[0])
        a = adata[:,genes].X
        sums = a.sum(axis=1).A1
        counts = diff(a.indptr)
        averages = divide(sums, counts, out=zeros_like(sums), where=counts!=0)
        return averages

def max_per_cell(adata, genes):
        if genes == []:
            return zeros(adata.shape[0])
        a = adata[:,genes].X.max(axis=1).toarray().flatten()
        return a

def gmean_per_cell(adata, genes):
        if genes == []:
            return zeros(adata.shape[0])
        return array(gmean(adata[:,genes].X)).flatten()

def hmean_per_cell(adata, genes):
        if genes == []:
            return zeros(adata.shape[0])
        return array(hmean(adata[:,genes].X)).flatten()


def _metalinks_estimation(me_res, adata, verbose, est_fun = 'mean_per_cell') -> DataFrame: 
    """
    Estimate metabolite abundances 
    Parameters
    ----------
    me_res : pandas.core.frame.DataFrame
        metabolite-gene associations
    
    adata : anndata.AnnData
        object with gene expression data

    est_fun : function
        function to aggregate gene expression values to metabolite abundance estimates

    verbose : bool
        verbosity

    Returns
    -------
    met_est : pandas.core.frame.DataFrame
        metabolite abundance estimates

    """

    # write dictionary that links est_fun to method name
    est_fun_dict = {'mean_per_cell': mean_per_cell,
                    'nnzmean_per_cell': nnzmean_per_cell,
                    'gmean_per_cell': gmean_per_cell,
                    'hmean_per_cell': hmean_per_cell,
                    'max_per_cell': max_per_cell}

    if est_fun not in est_fun_dict.keys():
        raise ValueError(f"est_fun must be one of {est_fun_dict.keys()}")

    est_fun = est_fun_dict[est_fun]
    
    metabolites = me_res['HMDB'].unique()

    prod_genes = array([get_gene_sets(i, 'producing', me_res, adata.var_names) for i in metabolites], dtype=object)
    deg_genes = array([get_gene_sets(i, 'degrading', me_res, adata.var_names) for i in metabolites], dtype=object)

    prod_vals = array([est_fun(adata, prod) for prod in prod_genes])
    deg_vals = array([est_fun(adata, deg) for deg in deg_genes])

    # Get final estimates and clip negative values to 0 to prevent product errors later in the pipeline
    final_estimates = get_est(prod_vals, deg_vals).clip(0, None)
    
    if verbose:
        print(f"Metabolites with gene expression: {160}")
        print(f"Metabolites without gene expression: {len(metabolites) - 160}")


    return DataFrame(final_estimates, columns=adata.obs_names, index=metabolites)



def get_gene_sets(i, direction, me_res, vars):
        return get_genesets(i, me_res, vars, direction)

def get_genesets(x, df, vars, direction):
    genes = df.loc[(df['HMDB'] == x) & (df['direction'] == direction),'GENE']
    genes = [x for x in genes if x in vars]
    return genes

def get_est(prod, deg):
    return prod - deg


