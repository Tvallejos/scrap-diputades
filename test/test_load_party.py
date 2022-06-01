from exceptions import DiputadeNotFound

def test_ctor_diputade_not_found():
    e = DiputadeNotFound("") 
    assert e.message == ""