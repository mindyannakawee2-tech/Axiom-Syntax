from axiomc import compile_source


def test_conditions_and_class():
    src = '''
cls. Character;
    f. init = (self, hp)
        self.hp = hp
    fend.
clsend.

i. 1 < 2 do
    log("ok")
ef. 2 < 1 do
    log("no")
e. do
    log("else")
end
'''
    py = compile_source(src)
    assert 'class Character:' in py
    assert 'def __init__(self, hp):' in py
    assert 'if 1 < 2:' in py
    assert 'elif 2 < 1:' in py
    assert 'else:' in py


if __name__ == '__main__':
    test_conditions_and_class()
    print('tests passed')
