"""
    Matrix
    ------

    Self made matrix mudule with step-by-step solution!
"""
from fractions import Fraction
from typing import Optional, Tuple, Union


class Matrix(list):
    """
    Self-made class for Matrix. Inherits list.

    Parameters
    ----------
    arg
        If given, initialize with given list.
        Else, initialize with blank list.
    """
    def __init__(self, arg: Optional[list] = None):
        def recurse_fractionalize(mat):
            if not isinstance(mat[0], list):
                return [Fraction(x) for x in mat]
            return [recurse_fractionalize(x) for x in mat]

        if arg is not None:
            list.__init__(self, arg)
            arg = recurse_fractionalize(self)
            list.__init__(self, arg)
        else:
            list.__init__(self, [])

    def __str__(self):
        """
        __str__ method for `str()`.
        """
        def recursive_str(mat, depth=1):
            to_return = ""
            for next_row in mat:
                if isinstance(next_row, list):
                    to_return += "["
                    if isinstance(next_row[0], list):
                        to_return += recursive_str(next_row, depth + 1)
                        to_return = to_return
                    else:
                        for next_elem in next_row:
                            to_return += str(next_elem)
                            to_return += " "
                        to_return = to_return[:-1]
                    to_return += "]\n"
                    to_return += " " * depth
                else:
                    to_return += str(next_row)
                    to_return += " "
            return to_return[:-(1 + depth)]

        def format_output(string):
            positions = []
            string_list = string.split("\n")
            if len(string_list) == 1:
                return string
            i = 0
            for next_string in string_list:
                positions.append([])
                next_string = next_string.replace("[", " ").replace("]", "")
                char_list = next_string.split(" ")
                char_list = [x for x in char_list if x != '']
                positions[i] = [len(x) for x in char_list]
                i += 1
            maximums = []
            for i in range(len(positions[0])):
                maximums.append(max([x[i] for x in positions]))
            positions = [[maximums[j] - positions[i][j]
                          for j in range(len(maximums))]
                         for i in range(len(positions))]
            i = 0
            j = 0
            to_return = ""
            manufacturing = False
            for next_chr in string:
                if next_chr in "[ ":
                    manufacturing = True
                if next_chr in "0123456789-/" and manufacturing:
                    to_return += " " * positions[i][j]
                    manufacturing = False
                    j += 1
                if next_chr == "\n":
                    j = 0
                    i += 1
                to_return += next_chr
            return to_return

        return format_output("[" + recursive_str(self) + "]")

    def __matmul__(self, other):
        """
        __matmul__ method for `@`.
        Based on PEP 465.

        Raises
        ------
        ValueError
            If matrix multiply is unsupported.
        """
        def fit(first, second):
            a, b = Matrix(first[:]), Matrix(second[:])
            swiched = False
            if len(b.shape) > len(a.shape):
                a, b = b, a
                swiched = True
            elif len(b.shape) == len(a.shape):
                return a, b
            b_shape = b.shape
            b = list(b)
            for _ in a.shape[:len(b_shape) - 1][::-1]:
                b = [[x for x in b] for _ in range(len(b))]
            if not swiched:
                return Matrix(a), Matrix(b)
            return Matrix(b), Matrix(a)
        if not isinstance(other, list):
            raise ValueError("Attempt to multiply matrix with {}"
                             .format(type(other).__name__))
        a = Matrix(self[:])
        b = Matrix(other[:])
        a_1d = False
        b_1d = False
        if len(a.shape) == 1:
            a_1d = True
            a = Matrix([a])
        if len(b.shape) == 1:
            b_1d = True
            b = Matrix([b]).T
        if len(a.shape) > 2 or len(b.shape) > 2:
            a, b = fit(a, b)
            to_return = []
            for i, self_next_row in enumerate(self):
                to_return.append(Matrix(self_next_row) @ Matrix(other[i]))
            return Matrix(to_return)

        if len(a[0]) != len(b):
            raise ValueError(
                'Attempt to multiply {}*{} matrix with {}*{} matrix'
                .format(len(a), len(a[0]), len(b), len(b[0])))
        b = b.T
        to_return = Matrix([[sum([i[n] * j[n] for n in range(len(i))])
                             for j in b] for i in a])
        if a_1d and b_1d:
            return to_return[0][0]
        if a_1d:
            return Matrix(to_return[0])
        if b_1d:
            return Matrix(to_return.T[0])
        return to_return

    def __imatmul__(self, other):
        """
        __imatmul__ method for `@=`.
        """
        self = self @ other
        return self

    def __mul__(self, other):
        """
        __mul__ method for `*`.
        If multiply matrix with matrix, it is element-wize,
        not matrix multiply.
        """
        if not isinstance(other, Matrix):
            return Matrix([[x * other for x in k] for k in self])
        if self.shape != other.shape:
            raise ValueError(
                'Cannot multiply elementwize with different size : {} and {}'
                .format(self.shape, other.shape))
        if len(self.shape) == 1:
            to_return = []
            for i, self_next_row in enumerate(self):
                to_return.append(self_next_row * other[i])
            return Matrix(to_return)
        to_return = []
        for i, self_next_row in enumerate(self):
            to_return.append(Matrix(self_next_row) * Matrix(other[i]))
        return Matrix(to_return)

    def __rmul__(self, other):
        """
        __rmul__ method for case like int * matrix.
        """
        return Matrix([[x * other for x in k] for k in self])

    def __imul__(self, other):
        """
        __imul__ method for `*=`.
        """
        self = self * other
        return self

    def __invert__(self):
        """
        __invert__ method for `~`.
        Return inverse matrix.

        Raises
        ------
        ZeroDivisionError
            If there is no inverse matrix.
        """
        try:
            return self.inverse_using_det()
        except ZeroDivisionError as e:
            err_str = e.args[0]
            a, _ = err_str.split(", ")
            a = a[9:]
            raise ZeroDivisionError("Error : Attempt to divide " + a +
                                    " with 0.")

    def gauss_elim(self, second: Optional['Matrix'] = None,
                   step_by_step: bool = False) -> 'Matrix':
        """
        Calculate with gauss elimination.
        Returns right-side matrix after calculation.

        Parameters
        ----------
        second
            Right-side matrix. can be 1D or 2D.
            If not given, this method calculates inverse matrix.
        step_by_step
            If true, print step by step solution.

        Raises
        ------
        ValueError
            If self is not square matrix, or length is different.
        ZeroDivisionError
            If cannot calculate due to divide with zero.
            It happens when determinent of self is zero.

        Returns
        -------
        Matrix
            Result of gauss elimination calculation.

        Examples
        --------
        Example of using gauss_elim with no option:

        >>> a = Matrix([[1,2,3],[2,5,3],[1,0,8]])
        >>> print(a.gauss_elim())
        [[-40 16  9]
         [ 13 -5 -3]
         [  5 -2 -1]]

        Example of using gauss_elim with option:

        >>> b = Matrix([[1,0,0],[0,1,0],[0,0,1]])
        >>> print(a.gauss_elim(b))
        [[-40 16  9]
         [ 13 -5 -3]
         [  5 -2 -1]]

        Example of using step by step solution:

        >>> a.gauss_elim(step_by_step=True) #doctest: +ELLIPSIS
        1 2 3 | 1 0 0
        2 5 3 | 0 1 0
        1 0 8 | 0 0 1
        Add row 1 * -2 to row 2
        ...

        """

        def print_gauss():
            string = str(first)
            str_list = string.split("\n")
            str_list = [x.strip().replace("[", "").replace("]", "")
                        for x in str_list]
            string2 = str(second)
            str2_list = string2.split("\n")
            str2_list = [x.strip().replace("[", "").replace("]", "")
                         for x in str2_list]
            for i in range(len(first)):
                print(str_list[i], "|", str2_list[i])

        def change_row(src, dest):
            if src != dest:
                if step_by_step:
                    print("Change row", src + 1, "with row", dest + 1)
                first[src], first[dest], second[src], second[dest] =\
                    first[dest], first[src], second[dest], second[src]
                if step_by_step:
                    print_gauss()

        def div_row(row, num):
            if step_by_step:
                print("Divide row", row + 1, "by", num)
            try:
                first[row] = [x / num for x in first[row]]
                second[row] = [x / num for x in second[row]]
            except ZeroDivisionError as e:
                err_str = e.args[0]
                a, _ = err_str.split(", ")
                a = a[9:]
                raise ZeroDivisionError("Error : Attempt to divide " + a +
                                        " with 0.")
            if step_by_step:
                print_gauss()

        def add_row(src, dest, to_mul):
            if step_by_step:
                print("Add row", src + 1, "*", to_mul, "to row", dest + 1)
            temp_first = first[:]
            temp_second = second[:]
            for i in range(len(first[src])):
                first[dest][i] += temp_first[src][i] * to_mul
            for i in range(len(second[src])):
                second[dest][i] += temp_second[src][i] * to_mul
            if step_by_step:
                print_gauss()

        first = Matrix(self[:])
        if second is None:
            second = Matrix.unit_mat(len(first))
        second = Matrix(second[:])
        if not isinstance(second[0], list):
            second = second.T
        if len(first) != len(first[0]):
            raise ValueError(
                'Matrix must be square to use Gauss elimination,'
                ' but given matrix is {}*{}'
                .format(len(first), len(first[0])))
        if len(first) != len(second):
            raise ValueError(
                'Length of argument is {}, while length of given matrix is {}'
                .format(len(second), len(first)))

        if step_by_step:
            print_gauss()
        for i, next_row in enumerate(first):
            if next_row[i] != 1:
                found = False
                non_zero = i
                for j in range(len(first) - i):
                    if first[j + i][i] == 1:
                        found = True
                        change_row(i, j + i)
                    elif next_row[i] == 0 and first[j + i][i] != 0\
                         and non_zero == i:
                        non_zero = j + i
                if not found:
                    change_row(i, non_zero)
                    div_row(i, first[i][i])

            for j in range(len(first) - i - 1):
                if first[j + i + 1][i] == 0:
                    continue
                add_row(i, j + i + 1, -first[j + i + 1][i])

        for i in range(len(first) - 1, -1, -1):
            if first[i][i] != 1:
                found = False
                for j in range(len(first) - i):
                    if first[j + i][i] == 1:
                        found = True
                        change_row(i, j + i)
                    elif first[i][i] == 0 and first[j + i][i] != 0\
                         and non_zero == i:
                        non_zero = j + i
                if not found:
                    change_row(i, non_zero)
                    div_row(i, first[i][i])

            for j in range(i - 1, -1, -1):
                if first[j][i] == 0:
                    continue
                add_row(i, j, -first[j][i])

        return Matrix(second)

    def inv_using_det(self, step_by_step: bool = False) -> 'Matrix':
        """
        Get inverse matrix using determinent.

        Parameters
        ----------
        step_by_step
            If True, print step by step solution

        Raises
        ------
        ZeroDivisionError
            If there is no inverse matrix.
        ValueError
            If matrix is not square.

        Returns
        -------
        Matrix
            calculated inverse matrix

        Examples
        --------
        Example of using inv_using_det:

        >>> a = Matrix([[1,2,3],[2,5,3],[1,0,8]])
        >>> print(a.inv_using_det())
        [[-40 16  9]
         [ 13 -5 -3]
         [  5 -2 -1]]

        Example of using step by step solution:

        >>> a.inv_using_det(step_by_step=True) #doctest:+ELLIPSIS
        Get adjugate matrix before transpose
        [[ 40 -13 -5]
         [-16   5  2]
         [ -9   3  1]]
        Transpose it
        ...

        """

        if len(self) != len(self[0]):
            raise ValueError(
                'Matrix must be square to get inverse, '
                'but given matrix is {}*{}'
                .format(len(self), len(self[0])))
        dest = Matrix(self[:])
        to_return = Matrix()
        for i, next_row in enumerate(dest):
            to_return.append([])
            for j, _ in enumerate(next_row):
                to_return[i].append(dest.get_cofactor(i, j).det *
                                    ((-1)**(i + j)))
        if step_by_step:
            print("Get adjugate matrix before transpose")
            print(Matrix(to_return))
        to_return = to_return.T
        if step_by_step:
            print("Transpose it")
            print(Matrix(to_return))
        det_dest = dest.det
        if step_by_step:
            print("Get determinant of given matrix")
            dest.det_step_by_step()
            print("Divide")
        try:
            to_return = [[x / det_dest for x in k] for k in to_return]
            if step_by_step:
                print(Matrix(to_return))
            return Matrix(to_return)
        except ZeroDivisionError as e:
            err_str = e.args[0]
            a, _ = err_str.split(", ")
            a = a[9:]
            raise ZeroDivisionError("Error : Attempt to divide " + a +
                                    " with 0.")

    def cramer(self, vals: Tuple[Union[int, float, Fraction], ...],
               step_by_step: bool = False) -> Tuple[Fraction, ...]:
        """
        Calculate polinomial linear expression using Cramer's formular.

        Parameters
        ----------
        vals
            Right-sided value to calculate.
        step_by_step
            If true, print step by step solution.

        Raises
        ------
        ZeroDivisionError
            If polinomial linear expression cannot be solved.
        ValueError
            If matrix is not square.

        Returns
        -------
        tuple
           Roots calculated. Type is Fraction.

        Examples
        --------
        Example of using cramer:

        >>> a = Matrix([[1,2,3],[2,5,3],[1,0,8]])
        >>> res = a.cramer((5, 2, 1))
        >>> print(tuple(int(x) for x in res))
        (-159, 52, 20)

        Example of using cramer with step by step solution:

        >>> a.cramer((5, 2, 1), step_by_step=True) #doctest:+ELLIPSIS
        Find Determinant of given matrix.
        Determinant of
        [[1 2 3]
         [2 5 3]
         [1 0 8]]
        is 40 - 26 + -15 = -1
        ...

        """

        if not len(self) == len(self[0]) == len(vals):
            raise ValueError(
                'Matrix must be square and have same size as numbers'
                " to use Cramer's formular,"
                ' but {}*{} matrix given with {} numbers.'
                .format(len(self), len(self[0]), len(vals)))

        if isinstance(vals, list):
            vals = tuple(vals)
        to_return = tuple()
        mat_det = self.det
        if step_by_step:
            print("Find Determinant of given matrix.")
            self.det_step_by_step()
        for i in range(len(self[0])):
            next_mat = Matrix(self[:])
            for j in range(len(self)):
                next_mat[j][i] = vals[j]
            if step_by_step:
                print("Find for variable", i + 1)
                next_mat.det_step_by_step()
            try:
                if step_by_step:
                    print("Divide", next_mat.det, "with", mat_det, ":",
                          next_mat.det / mat_det)
                to_return += (next_mat.det / mat_det,)
            except ZeroDivisionError as e:
                err_str = e.args[0]
                a, _ = err_str.split(", ")
                a = a[9:]
                raise ZeroDivisionError("Error : Attempt to divide " + a +
                                        " with 0.")

        return to_return

    def get_cofactor(self, i_selected: int, j_selected: int) -> 'Matrix':
        """
        Get cofactor with given index. Index starts with 0.

        Parameters
        ----------
        i_selected
            Row index to get cofactor.
        j_selected
            Colomn index to get coffactor.

        Returns
        -------
        Matrix
            Cofactor calculated.
        """
        to_return = self[:]
        del to_return[i_selected]
        for i, next_row in enumerate(to_return):
            to_return[i] = [next_elem for j, next_elem in enumerate(next_row)
                            if j != j_selected]
        return Matrix(to_return)

    def mat_input(self) -> None:
        """
        User input for matrix.

        Raises
        ------
        ValueError
            Raise if unappropriate value is given.
        """
        print("Input matrix. press enter key two time for exit."
              "\nElement is seperated with space.")
        while True:
            inputed = input().split(" ")
            if inputed != [""]:
                try:
                    self.append([Fraction(x) for x in inputed])
                except ValueError as e:
                    err_str = e.args[0]
                    raise ValueError(err_str[30:] + " is not a number.")
            else:
                break

    def det_step_by_step(self) -> Fraction:
        """
        Calculate determinant with printing step by step solution.

        Raises
        ------
        ValueError
            If matrix is not square.

        Returns
        -------
        Fraction
            calculated determinant.
        """
        if len(self) != len(self[0]):
            raise ValueError('Matrix must be square to get determinant,'
                             ' but given matrix is {}*{}'
                             .format(len(self), len(self[0])))
        if len(self) == 1:
            return self[0][0]
        if len(self) == 2:
            print("Determinant of")
            print(self)
            print("is", end=' ')
            print(self[0][0] * self[1][1] - self[0][1] * self[1][0])
            return self[0][0] * self[1][1] - self[0][1] * self[1][0]

        to_return = 0
        print("Determinant of")
        print(self)
        print("is", end=' ')
        for i in range(len(self)):
            if i == len(self) - 1:
                print(self[0][i] * self.get_cofactor(0, i).det *
                      ((-1)**i), end=' ')
            elif i % 2 == 0:
                print(self[0][i] * self.get_cofactor(0, i).det,
                      '-', end=' ')
            else:
                print(self[0][i] * self.get_cofactor(0, i).det,
                      '+', end=' ')
            to_return += self[0][i] * self.get_cofactor(0, i).det *\
                ((-1)**i)
        print('=', to_return)
        return to_return

    @classmethod
    def mul_stepbystep(cls, first: 'Matrix', second: 'Matrix') -> 'Matrix':
        """
        Multiply matrix with printing step by step solution.
        Calculates `first @ second`.

        Parameters
        ----------
        first
            Matrix to calculate with.
        second
            Matrix to calculate with.

        Raises
        ------
        ValueError
            If matrixes cannot be multiplied.

        Returns
        -------
        Matrix
            Calculated matrix.
        """
        if len(first[0]) != len(second):
            raise ValueError(
                'Attempt to multiply {}*{} matrix with {}*{} matrix'
                .format(len(first), len(first[0]),
                        len(second), len(second[0])))
        to_return = []
        for i, row_first in enumerate(first):
            to_return.append([])
            for j in range(len(second[0])):
                to_return[i].append(0)
                for k in range(len(first[0])):
                    print(row_first[k], "X", second[k][j], sep='', end='')
                    to_return[i][j] += row_first[k] * second[k][j]
                    if k < len(first[0]) - 1:
                        print("+", sep='', end='')
                if j < len(second[0]) - 1:
                    print(", ", end='')
            print()
        return Matrix(to_return)

    @classmethod
    def unit_mat(cls, size: int) -> 'Matrix':
        """
        Get unit matrix of given size.

        Parameters
        ----------
        size
            Size of unit matrix.

        Returns
        -------
        Matrix
            Calculated unit matrix.
        """
        to_return = []
        for i in range(size):
            to_return.append([])
            for j in range(size):
                if i == j:
                    to_return[i].append(1)
                else:
                    to_return[i].append(0)
        return Matrix(to_return)

    @property
    def det(self) -> Fraction:
        """
        Fraction: Determinant of the matrix.
        """
        if len(self) != len(self[0]):
            raise ValueError(
                'Matrix must be square to get determinant,'
                ' but given matrix is {}*{}'
                .format(len(self), len(self[0])))
        if len(self) == 1:
            return self[0][0]
        if len(self) == 2:
            return self[0][0] * self[1][1] - self[0][1] * self[1][0]

        to_return = 0
        for i in range(len(self)):
            to_return += self[0][i] * self.get_cofactor(0, i).det *\
                ((-1)**i)
        return to_return

    @property
    def T(self) -> 'Matrix':
        """
        Matrix: Transposed matrix.
        """
        if not isinstance(self[0], list):
            return Matrix([[x] for x in self])
        return Matrix([[temp[i] for temp in self]
                       for i in range(len(self[0]))])

    @property
    def shape(self) -> Tuple[int, ...]:
        """
        Tuple of int: Shape of the matrix.
        """
        if not isinstance(self[0], list):
            return (len(self),)
        return (len(self), ) + Matrix(self[0]).shape


if __name__ == "__main__":
    a = Matrix()
    b = Matrix()
    a.mat_input()
    b.mat_input()
    print("==Basic==\n")
    print("a : ")
    print(a)
    print()
    print("b : ")
    print(b)
    print()
    try:
        c = a @ b
        print("a @ b : ")
        print(c)
        print()
    except ValueError as e:
        print(e)
    print("a.T : ")
    print(a.T)
    print()
    print("det(a) : ", end='')
    try:
        print(a.det)
    except ValueError as e:
        print(e)
    print("\n==Gauss Elimination==\n")
    try:
        a.gauss_elim(b, step_by_step=True)
    except (ZeroDivisionError, ValueError) as e:
        print(e)
    print("\n==Inverse using determinent==\n")
    try:
        a.inv_using_det(step_by_step=True)
    except (ZeroDivisionError, ValueError) as e:
        print(e)
    print("\n==Cramer's formular==\n")
    try:
        a.cramer(tuple(b.T[0]), step_by_step=True)
    except (ZeroDivisionError, ValueError) as e:
        print(e)

