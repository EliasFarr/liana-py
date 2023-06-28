import pandas as pd
import plotnine as p9


def target_metrics(misty, stat, top_n=None, figure_size=(7,5), return_fig=True):
    target_metrics = misty.uns['target_metrics'].copy()
    
    if top_n is not None:
        target_metrics = target_metrics.sort_values(stat).head(top_n)
    
    # get order of target by decreasing intra.R2
    targets = target_metrics.sort_values(by=stat, ascending=False)['target'].values
    # targets as categorical variable
    target_metrics['target'] = pd.Categorical(target_metrics['target'],
                                              categories=targets, 
                                              ordered=True)
    
    p = (p9.ggplot(target_metrics, p9.aes(x='target', y=stat)) +
         p9.geom_point(size=3) + 
         p9.theme_bw() +
         p9.theme(axis_text_x=p9.element_text(rotation=90),
                  figure_size=figure_size)
         )
    
    if return_fig:
        return p
    p.draw()
    
    
def contributions(misty, figure_size=(7, 5), stat=None, top_n=None, return_fig=True):
    contributions = misty.uns['target_metrics'].copy()
    
    if top_n is not None:
        target_metrics = target_metrics.sort_values(stat).head(top_n)

    view_names = misty.view_names.copy()
    if 'intra' not in contributions.columns:
        view_names.remove('intra')

    contributions = contributions[['target', *view_names]]
    contributions = contributions.melt(id_vars='target', var_name='view', value_name='contribution')

    p = (p9.ggplot(contributions, p9.aes(x='target', y='contribution', fill='view')) +
            p9.geom_bar(stat='identity') +
            p9.theme_bw(base_size=14) +
        p9.theme(axis_text_x=p9.element_text(rotation=90),
                    figure_size=figure_size) +
            p9.scale_fill_brewer(palette=2, type='qual')
    )

    if return_fig:
        return p
    p.draw()


def interactions(misty, view, top_n = None, ascending=None, figure_size=(7,5), return_fig=True):
    interactions = misty.uns['interactions'].copy()
    interactions = interactions[interactions['view'] == view]
    grouped = interactions.groupby('predictor')['importances'].apply(lambda x: x.isna().all())
    interactions = interactions[~interactions['predictor'].isin(grouped[grouped].index)]
    
    if top_n is not None:
        if ascending is None:
            key = lambda x: abs(x)
        else:
            key = None
        interactions = interactions.sort_values(by='importances', key=key, ascending=False)
    
    
    p = (p9.ggplot(interactions, 
                   p9.aes(x='predictor',
                          y='target',
                          fill='importances')
                   ) +
    p9.geom_tile() +
    p9.theme_minimal(base_size=12) +
    p9.theme(axis_text_x=p9.element_text(rotation=90),
             figure_size=figure_size) +
    p9.labs(x='Predictor', y='Target', fill='Importance')
    )
    
    if return_fig:
        return p
    p.draw()
