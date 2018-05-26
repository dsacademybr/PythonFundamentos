from nose.tools import assert_equal


class TestUniqueChars(object):

    def test_unique_chars(self, func):
        assert_equal(func(None), False)
        assert_equal(func(''), True)
        assert_equal(func('foo'), False)
        assert_equal(func('bar'), True)
        print('Sua solução foi executada com sucesso! Parabéns!')


def main():
    test = TestUniqueChars()
    try:
        unique_chars = UniqueChars()
        test.test_unique_chars(unique_chars.has_unique_chars)
    except NameError:
        pass


if __name__ == '__main__':
    main()