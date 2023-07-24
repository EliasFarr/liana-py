from liana.resource._select_resource import _handle_resource, select_resource
import pytest

def test_select_interactions():
    # generate list of 2x strings
    interactions = [('a', 'b'), ('c', 'd')]
    
    resource = _handle_resource(interactions=interactions,
                                x_key='x',
                                y_key='y',
                                verbose=True,
                                # These should be ignored
                                resource=select_resource("consensus"), 
                                resource_name='consensus')
    
    assert resource.shape[0] == 2
    assert (resource.columns == ['x', 'y']).all()


def test_select_resource():
    resource = _handle_resource(interactions=None,
                                x_key='ligand',
                                y_key='receptor',
                                verbose=True,
                                resource=select_resource("consensus"), 
                                # This should be ignored
                                resource_name='ignore me'
                                )
    
    assert resource.shape[0] == 4701
    assert (resource.columns == ['ligand', 'receptor']).all()


def test_select_resource_name():
    resource = _handle_resource(interactions=None,
                                resource=None,
                                resource_name='cellchatdb',
                                x_key='x',
                                y_key='y',
                                verbose=True,
                                )
    
    assert resource.shape[0] == 1912
    assert (resource.columns == ['ligand', 'receptor']).all()


def test_resource_exception_none():
    with pytest.raises(ValueError):
        _handle_resource(interactions=None,
                         resource=None,
                         resource_name=None,
                         x_key='x',
                         y_key='y',
                         verbose=True,)
        

def test_resource_exception_xy():
    with pytest.raises(ValueError):
        _handle_resource(interactions=None, 
                         resource=select_resource("consensus"),
                         resource_name=None,
                         x_key='x',
                         y_key='y',
                         verbose=True,
                         )
    
