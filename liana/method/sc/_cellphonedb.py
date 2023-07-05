import numpy as np
from ...method._Method import Method, MethodMeta
from ...method._pipe_utils._get_mean_perms import _calculate_pvals

# Internal Function to calculate CellPhoneDB LR_mean and p-values
def _cpdb_score(x, perm_stats) -> tuple:
    """
    Calculate CellPhoneDB-like LR means and p-values
    
    Parameters
    ----------
    x
        DataFrame with LIANA results
    perm_stats
        Permutation statistics (2 (ligand-receptor), n_perms (number of permutations, n_rows in lr_res)

    Returns
    -------
    A tuple with lr_mean and p-value for x

    """
    zero_msk = ((x['ligand_means'] == 0) | (x['receptor_means'] == 0))
    lr_means = np.mean((x['ligand_means'].values, x['receptor_means'].values), axis=0)
    lr_means[zero_msk] = 0
    
    cpdb_pvals = _calculate_pvals(lr_means, perm_stats, np.mean)

    return lr_means, cpdb_pvals


# Initialize CPDB Meta
_cellphonedb = MethodMeta(method_name="CellPhoneDB",
                          complex_cols=["ligand_means", "receptor_means"],
                          add_cols=[],
                          fun=_cpdb_score,
                          magnitude="lr_means",
                          magnitude_ascending=False,
                          specificity="cellphone_pvals",
                          specificity_ascending=True,
                          permute=True,
                          met=False,
                          reference="Efremova, M., Vento-Tormo, M., Teichmann, S.A. and "
                                    "Vento-Tormo, R., 2020. CellPhoneDB: inferring cell–cell "
                                    "communication from combined expression of multi-subunit "
                                    "ligand–receptor complexes. Nature protocols, 15(4), "
                                    "pp.1484-1506. "
                          )

# Initialize callable Method instance
cellphonedb = Method(_method=_cellphonedb)
