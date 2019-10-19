from App.Common.DateBase.SelectError import SelectError

def test_SelectError_initialize():
    SelectError()
def test_SelectError_is_instance_KeyError():
    assert isinstance(SelectError(), KeyError)