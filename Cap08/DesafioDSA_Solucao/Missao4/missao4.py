from nose.tools import assert_equal, assert_raises


class TestSelectionSort(object):

    def test_selection_sort(self, func):
        print('None input')
        assert_raises(TypeError, func, None)

        print('Input vazio')
        assert_equal(func([]), [])

        print('Um elemento')
        assert_equal(func([5]), [5])

        print('Dois ou mais elementos')
        data = [5, 1, 7, 2, 6, -3, 5, 7, -10]
        assert_equal(func(data), sorted(data))

        print('Sua solução foi executada com sucesso! Parabéns!')


def main():
    test = TestSelectionSort()
    try:
        selection_sort = SelectionSort()
        test.test_selection_sort(selection_sort.sort)
    except NameError:
        pass


if __name__ == '__main__':
    main()