import sys

from unittest import TestCase

if sys.version_info.major < 3:
    raise RuntimeError('Python {version} not supported, please use Python >= 3'.format(
        version=sys.version.split(' ')[0]
    ))

class FieldElement:
    def __init__(self, num, prime):
        if num >= prime or num < 0:
            error = 'Num {} is not in the field of range 0 to {}'.format(
                num,
                prime - 1
            )

            raise ValueError(error)

        self.num = num
        self.prime = prime

    def __repr__(self):
        return 'FieldElement(num={num}, prime={prime})'.format(**self.__dict__)

    def __eq__(self, other):
        if other is None:
            return False

        return self.num == other.num and self.prime == self.prime

    def __ne__(self, other):
        return not (self == other)

    def __add__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers of different Fields')

        num = (self.num + other.num) % self.prime

        return self.__class__(num, self.prime)

    def __sub__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers of different Fields')

        num = (self.num - other.num) % self.prime

        return self.__class__(num, self.prime)

    def __mul__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers of different Fields')

        num = self.num * other.num % self.prime

        return self.__class__(num, self.prime)

    def __pow__(self, exponent):
        n = exponent % (self.prime - 1)

        num = pow(self.num, n, self.prime)

        return self.__class__(num, self.prime)

    def __truediv__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers of different Fields')

        if other.num == 0:
            raise ValueError('Cannot divide by 0')

        num = (self.num * pow(other.num, self.prime - 2, self.prime)) % self.prime

        return self.__class__(num, self.prime)

    def __rmul__(self, coefficient):
        num = (self.num * coefficient) % self.prime

        return self.__class__(num, self.prime)

class FieldElementTest(TestCase):

    def test_ne(self):
        a = FieldElement(2, 31)
        b = FieldElement(2, 31)
        c = FieldElement(15, 31)
        self.assertEqual(a, b)
        self.assertTrue(a != c)
        self.assertFalse(a != b)

    def test_add(self):
        a = FieldElement(2, 31)
        b = FieldElement(15, 31)
        self.assertEqual(a + b, FieldElement(17, 31))
        a = FieldElement(17, 31)
        b = FieldElement(21, 31)
        self.assertEqual(a + b, FieldElement(7, 31))

    def test_sub(self):
        a = FieldElement(29, 31)
        b = FieldElement(4, 31)
        self.assertEqual(a - b, FieldElement(25, 31))
        a = FieldElement(15, 31)
        b = FieldElement(30, 31)
        self.assertEqual(a - b, FieldElement(16, 31))

    def test_mul(self):
        a = FieldElement(24, 31)
        b = FieldElement(19, 31)
        self.assertEqual(a * b, FieldElement(22, 31))

    def test_rmul(self):
        a = FieldElement(24, 31)
        b = 2
        self.assertEqual(b * a, a + a)

    def test_pow(self):
        a = FieldElement(17, 31)
        self.assertEqual(a**3, FieldElement(15, 31))
        a = FieldElement(5, 31)
        b = FieldElement(18, 31)
        self.assertEqual(a**5 * b, FieldElement(16, 31))

    def test_div(self):
        a = FieldElement(3, 31)
        b = FieldElement(24, 31)
        self.assertEqual(a / b, FieldElement(4, 31))
        a = FieldElement(17, 31)
        self.assertEqual(a**-3, FieldElement(29, 31))
        a = FieldElement(4, 31)
        b = FieldElement(11, 31)
        self.assertEqual(a**-4 * b, FieldElement(13, 31))

class Point:
    def __init__(self, x, y, a, b):
        self.a = a
        self.b = b
        self.x = x
        self.y = y

        if self.x is None and self.y is None:
            return

        if not self._on_curve():
            raise ValueError('({}, {}) is not in the curve'.format(x, y))

    def _on_curve(self):
        return (self.y ** 2) == (self.x ** 3) + (self.a * self.x) + self.b

    def __repr__(self):
        return 'Point(x={x}, y={y}, a={a}, b={b})'.format(**self.__dict__)

    def __eq__(self, other):
        if other is None:
            return False

        return self.x == other.x and self.y == other.y and \
               self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not (self == other)

    def __add__(self, other):
        if self.a != other.a or self.b != other.b:
            raise TypeError('{} and {} are not in the same curve'.format(self, other))

        if self.x is None:
            return other

        if other.x is None:
            return self

        if self.x == other.x and self.y != other.y:
            return self.__class__(None, None, self.a, self.b)

        if self.x != other.x:
            s = (other.y - self.y) / (other.x - self.x)
            x = (s ** 2) - self.x - other.x
            y = s * (self.x - x) - self.y

            return self.__class__(x, y, self.a, self.b)

        if self == other and self.y == 0 * self.x:
            return self.__class__(None, None, self.a, self.b)

        if self == other:
            s = (3 * self.x ** 2 + self.a) / (2 * self.y)
            x = s ** 2 - 2 * self.x
            y = s * (self.x - x) - self.y

            return self.__class__(x, y, self.a, self.b)

    def __rmul__(self, coefficient):
        # Inefficient way
        #product = self.__class__(None, None, self.a, self.b)

        #for _ in range(coefficient):
            #product += self

        #return product

        # Efficient way
        coef = coefficient
        current = self
        result = self.__class__(None, None, self.a, self.b)

        while coef:
            if coef & 1:
                result += current

            current += current
            coef >>= 1

        return result

class ECCTest(TestCase):
    def test_on_curve(self):
        prime = 223

        a = FieldElement(0, prime)
        b = FieldElement(7, prime)

        valid_points = ((192, 105), (17, 56), (1, 193))
        invalid_points = ((200, 119), (42, 99))

        for x_raw, y_raw in valid_points:
            x = FieldElement(x_raw, prime)
            y = FieldElement(y_raw, prime)

            Point(x, y, a, b)

        for x_raw, y_raw in invalid_points:
            x = FieldElement(x_raw, prime)
            y = FieldElement(y_raw, prime)

            with self.assertRaises(ValueError):
                Point(x, y, a, b)

    def test_add(self):
        prime = 223

        a = FieldElement(0, prime)
        b = FieldElement(7, prime)

        additions = [
            (
                Point(FieldElement(192, prime), FieldElement(105, prime), a, b),
                Point(FieldElement(17, prime), FieldElement(56, prime), a, b),
                Point(FieldElement(170, prime), FieldElement(142, prime), a, b),
            ),
            (
                Point(FieldElement(47, prime), FieldElement(71, prime), a, b),
                Point(FieldElement(117, prime), FieldElement(141, prime), a, b),
                Point(FieldElement(60, prime), FieldElement(139, prime), a, b),
            ),
            (
                Point(FieldElement(143, prime), FieldElement(98, prime), a, b),
                Point(FieldElement(76, prime), FieldElement(66, prime), a, b),
                Point(FieldElement(47, prime), FieldElement(71, prime), a, b),
            ),
        ]

        for (p1, p2, p3) in additions:
            self.assertEqual(p1 + p2, p3)

    def test_mul(self):
        # Point of infinity
        prime = 223

        a = FieldElement(0, prime)
        b = FieldElement(7, prime)
        x = FieldElement(15, prime)
        y = FieldElement(86, prime)

        p = Point(x, y, a, b)
        result = Point(None, None, a, b)

        self.assertTrue(7 * p, result)

P = (2 ** 255) + (2 ** 32) - 977

class S256Field(FieldElement):
    def __init__(self, num, prime=None):
        super().__init__(num=num, prime=P)

    def __repr__(self):
        return 'S256Field(num={num}) # => {x}'.format(
            num=self.num,
            x='{:x}'.format(self.num).zfill(64)
        )
