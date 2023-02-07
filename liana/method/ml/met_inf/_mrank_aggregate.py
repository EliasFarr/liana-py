from liana.method.ml._ml_Method import MetabMethodMeta
from liana.method.ml._ml_pipe import ml_pipe

from anndata import AnnData
from pandas import DataFrame, concat
from typing import Optional


class MetabAggregateClass(MetabMethodMeta):
    """LIANA's Method Consensus Class"""
    def __init__(self, methods, _SCORE):
        super().__init__(score_method_name=_SCORE.score_method_name,
                         fun=_SCORE.fun,
                         reference=_SCORE.reference
                         )

        self._SCORE = _SCORE
        self.methods = methods
        self.steady = 'steady_rank'
        self.steady_ascending = True



    def describe(self):
        """Briefly described the method"""
        print(
            f"fix !!! new metabolite method name: {self.score_method_name}"
        )

    def __call__(self,
                 adata: AnnData,
                 groupby: str,
                 resource_name: str = 'consensus',
                 expr_prop: float = 0.1,
                 min_cells: int = 5,
                 base: float = 2.718281828459045,
                 aggregate_method='rra',
                 return_all_lrs: bool = False,
                 consensus_opts=None,
                 use_raw: Optional[bool] = True,
                 de_method='t-test',
                 verbose: Optional[bool] = False,
                 resource: Optional[DataFrame] = None,
                 inplace=True):
        """
        Parameters
        ----------
        adata
            Annotated data object.
        groupby
            The key of the observations grouping to consider.
        resource_name
            Name of the resource to be loaded and use for ligand-receptor inference.
        expr_prop
            Minimum expression proportion for the ligands/receptors (and their subunits) in the
             corresponding cell identities. Set to `0`, to return unfiltered results.
        min_cells
            Minimum cells per cell identity (`groupby`) to be considered for downstream analysis
        base
            Exponent base used to reverse the log-transformation of matrix. Note that this is
            relevant only for the `logfc` method.
        aggregate_method
            Method aggregation approach, one of ['mean', 'rra'], where `mean` represents the
            mean rank, while 'rra' is the RobustRankAggregate (Kolde et al., 2014)
            of the interactions
        return_all_lrs
            Bool whether to return all LRs, or only those that surpass the `expr_prop`
            threshold. Those interactions that do not pass the `expr_prop` threshold will
            be assigned to the *worst* score of the ones that do. `False` by default.
        use_raw
            Use raw attribute of adata if present. True, by default.
        layer
            Layer in anndata.AnnData.layers to use. If None, use anndata.AnnData.X.
        de_method
            Differential expression method. `scanpy.tl.rank_genes_groups` is used to rank genes
            according to 1vsRest. The default method is 't-test'.
        verbose
            Verbosity flag
        n_perms
            Number of permutations for the permutation test. Note that this is relevant
            only for permutation-based methods - e.g. `CellPhoneDB`
        seed
            Random seed for reproducibility.
        resource
            Parameter to enable external resources to be passed. Expects a pandas dataframe
            with [`ligand`, `receptor`] columns. None by default. If provided will overrule
            the resource requested via `resource_name`
        inplace
            If true return `DataFrame` with results, else assign inplace to `.uns`.


        Returns
        -------
        If ``inplace = False``, returns a `DataFrame` with ligand-receptor results
        Otherwise, modifies the ``adata`` object with the following key:
            - :attr:`anndata.AnnData.uns` ``['liana_res']`` with the aforementioned DataFrame
        """
        ml_res = ml_pipe(adata=adata,
                               groupby=groupby,
                               resource_name=resource_name,
                               resource=resource,
                               expr_prop=expr_prop,
                               min_cells=min_cells,
                               base=base,
                               return_all_lrs=return_all_lrs,
                               de_method=de_method,
                               verbose=verbose,
                               _estimation=self,
                               use_raw=use_raw,
                               _methods=self.methods,
                               _aggregate_method=aggregate_method,
                               _consensus_opts=consensus_opts
                               )
        adata.obsm['ml_res'] = ml_res

        return None if inplace else ml_res

_mrank_aggregate_meta = \
    MetabMethodMeta(score_method_name="MRank_Aggregate",
               fun=None,  # change to _robust_rank
               score_reference='Dimitrov, D., Türei, D., Garrido-Rodriguez, M., Burmedi, P.L., '
                         'Nagai, J.S., Boys, C., Ramirez Flores, R.O., Kim, H., Szalai, B., '
                         'Costa, I.G. and Valdeolivas, A., 2022. Comparison of methods and '
                         'resources for cell-cell communication inference from single-cell '
                         'RNA-Seq data. Nature Communications, 13(1), pp.1-13. '
               )
