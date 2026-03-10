import pytest
import sys
import os
from io import StringIO
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBasicsB001:
    def test_hello_world(self):
        from basics.B001_hello_world import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue().strip()
            assert output == "Hello, World!"


class TestBasicsB002:
    def test_variable_operations(self):
        from basics.B002_variable_operations import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "10 + 3 = 13" in output
            assert "10 - 3 = 7" in output
            assert "10 * 3 = 30" in output
            assert "10 / 3 =" in output


class TestBasicsB003:
    def test_type_conversion(self):
        from basics.B003_type_conversion import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "字符串转整数: int('123') = 123" in output
            assert "浮点数转整数: int(3.14) = 3" in output
            assert "整数转字符串: str(99) = 99" in output


class TestBasicsB004:
    def test_string_basics(self):
        from basics.B004_string_basics import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "Python Programming" in output
            assert "长度: 18" in output
            assert "大写: PYTHON PROGRAMMING" in output


class TestBasicsB005:
    def test_string_slicing(self):
        from basics.B005_string_slicing import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "前5个字符: Hello" in output
            assert "最后5个字符: orld!" in output
            assert "第7-11个字符: World" in output


class TestBasicsB006:
    def test_boolean_comparison(self):
        from basics.B006_boolean_comparison import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "a > b: False" in output
            assert "a < b: True" in output
            assert "a == b: False" in output


class TestBasicsB007:
    def test_list_operations(self):
        from basics.B007_list_operations import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "列表操作后: ['apple', 'cherry', 'orange']" in output
            assert "第一个元素: apple" in output


class TestBasicsB008:
    def test_dict_operations(self):
        from basics.B008_dict_operations import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "Alice" in output
            assert "Beijing" in output
            assert "age" in output


class TestBasicsB009:
    def test_tuple_operations(self):
        from basics.B009_tuple_operations import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "元组: (10, 20)" in output
            assert "第一个元素: 10" in output
            assert "解包: x = 10, y = 20" in output


class TestBasicsB010:
    def test_set_operations(self):
        from basics.B010_set_operations import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "交集: {3, 4}" in output
            assert "并集:" in output
            assert "差集(set1-set2): {1, 2}" in output


class TestBasicsB011:
    def test_arithmetic_operators(self):
        from basics.B011_arithmetic_operators import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "加法 a + b = 22" in output
            assert "整除 a // b = 3" in output
            assert "取余 a % b = 2" in output
            assert "幂运算 a ** b = 1419857" in output


class TestBasicsB012:
    def test_logical_operators(self):
        from basics.B012_logical_operators import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "x and y = False" in output
            assert "x or y = True" in output
            assert "not x = False" in output


class TestBasicsB013:
    def test_assignment_operators(self):
        from basics.B013_assignment_operators import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "初始值: a = 10" in output
            assert "a += 5: a = 15" in output
            assert "a /= 4: a = 6.0" in output


class TestBasicsB014:
    def test_bitwise_operators(self):
        from basics.B014_bitwise_operators import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "a & b (按位与): 8" in output
            assert "a | b (按位或): 14" in output
            assert "a ^ b (按位异或): 6" in output


class TestBasicsB015:
    def test_operator_precedence(self):
        from basics.B015_operator_precedence import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "2 + 3 * 4 = 14" in output
            assert "(2 + 3) * 4 = 20" in output
            assert "2 ** 3 ** 2 = 512" in output


class TestBasicsB016:
    def test_if_statement(self):
        from basics.B016_if_statement import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "成绩 85 分，等级: B" in output


class TestBasicsB017:
    def test_for_loop(self):
        from basics.B017_for_loop import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "1到10的累加和: 55" in output


class TestBasicsB018:
    def test_while_loop(self):
        from basics.B018_while_loop import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "累加和超过100时停止" in output


class TestBasicsB019:
    def test_nested_loop(self):
        from basics.B019_nested_loop import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "1*1=1" in output
            assert "9*9=81" in output


class TestBasicsB020:
    def test_break_continue_else(self):
        from basics.B020_break_continue_else import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "找到的非3倍数数量:" in output
            assert "是否遇到10: True" in output


class TestBasicsB021:
    def test_function_definition(self):
        from basics.B021_function_definition import greet
        assert greet("Alice") == "Hello, Alice!"
        assert greet("Bob") == "Hello, Bob!"


class TestBasicsB022:
    def test_function_parameters(self):
        from basics.B022_function_parameters import power, sum_values
        assert power(3) == 9
        assert power(3, 3) == 27
        assert sum_values(1, 2, 3, 4, 5) == 15


class TestBasicsB023:
    def test_variable_scope(self):
        from basics.B023_variable_scope import global_var, modify_global
        initial = global_var
        modify_global()
        from basics import B023_variable_scope
        assert B023_variable_scope.global_var == 20


class TestBasicsB024:
    def test_function_return(self):
        from basics.B024_function_return import calculate
        s, diff, p, q = calculate(10, 3)
        assert s == 13
        assert diff == 7
        assert p == 30
        assert abs(q - 3.333) < 0.01


class TestBasicsB025:
    def test_lambda_functions(self):
        from basics.B025_lambda_functions import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "add(3, 5) = 8" in output
            assert "map乘2: [2, 4, 6, 8, 10]" in output
            assert "filter偶数: [2, 4]" in output


class TestBasicsB026:
    def test_class_definition(self):
        from basics.B026_class_definition import Person
        p = Person("Alice", 25)
        assert p.name == "Alice"
        assert p.age == 25
        assert p.introduce() == "My name is Alice, I am 25 years old."


class TestBasicsB027:
    def test_class_methods(self):
        from basics.B027_class_methods import Calculator
        calc = Calculator()
        result = calc.add(10).multiply(3).subtract(5).result
        assert result == 25


class TestBasicsB028:
    def test_inheritance(self):
        from basics.B028_inheritance import Dog, Cat
        dog = Dog("Buddy")
        cat = Cat("Whiskers")
        assert dog.speak() == "Buddy says Woof!"
        assert cat.speak() == "Whiskers says Meow!"


class TestBasicsB029:
    def test_module_import(self):
        from basics.B029_module_import import main
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert "math.pi" in output
            assert "random.randint" in output
            assert "当前时间:" in output


class TestBasicsB030:
    def test_exception_handling(self):
        from basics.B030_exception_handling import safe_divide
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(10, 0) == "Error: Division by zero!"
        assert safe_divide("10", 2) == "Error: Invalid type!"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
