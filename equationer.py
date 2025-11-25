import ast
import re

class HOI4Converter(ast.NodeVisitor):
    def __init__(self, target):
        self.target = target
        self.temp_index = 0
        self.lines = []

    def new_temp(self):
        self.temp_index += 1
        return f"temp_{self.temp_index}"

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if left.startswith("temp_") or left == self.target:
            out = left
        else:
            out = self.new_temp()
            self.lines.append(f"set_variable = {{ var = {out} value = {left} }}")

        if isinstance(node.op, ast.Add):
            self.lines.append(f"add_to_variable = {{ var = {out} value = {right} }}")
        elif isinstance(node.op, ast.Sub):
            self.lines.append(f"subtract_from_variable = {{ var = {out} value = {right} }}")
        elif isinstance(node.op, ast.Mult):
            self.lines.append(f"multiply_variable = {{ var = {out} value = {right} }}")
        elif isinstance(node.op, ast.Div):
            self.lines.append(f"divide_variable = {{ var = {out} value = {right} }}")

        return out

    def visit_Name(self, node):
        return node.id

    def visit_Constant(self, node):  # for Python 3.8+
        return str(node.value)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id.upper() == "ROUND":
            val = self.visit(node.args[0])
            decimals = int(self.visit(node.args[1]))

            out = val if val.startswith("temp_") else self.new_temp()
            if out != val:
                self.lines.append(f"set_variable = {{ var = {out} value = {val} }}")

            if decimals == 0:
                self.lines.append(f"round_variable = {out}")
            else:
                scale = 10 ** decimals if decimals > 0 else 1 / (10 ** abs(decimals))
                self.lines.append(f"multiply_variable = {{ var = {out} value = {scale} }}")
                self.lines.append(f"round_variable = {out}")
                self.lines.append(f"divide_variable = {{ var = {out} value = {scale} }}")

            return out
        raise ValueError("Unsupported function call")

    def convert(self, expr):
        tree = ast.parse(expr, mode='eval')
        result = self.visit(tree.body)
        if result != self.target:
            self.lines.append(f"set_variable = {{ var = {self.target} value = {result} }}")
        return "\n".join(self.lines)


def parse_assignment(expr: str):
    """If expression includes '=', extract variable and right-hand expression."""
    match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", expr)
    if match:
        return match.group(1), match.group(2)
    return None, expr


if __name__ == "__main__":
    print("HOI4 Math Converter")

    raw_expr = input("Enter your expression (e.g. result = ROUND(a * 3.2, 2)): ").strip()
    target, expr = parse_assignment(raw_expr)

    if not target:
        target = input("Enter target variable (e.g. result): ").strip()

    try:
        converter = HOI4Converter(target)
        output = converter.convert(expr)
        print("\nConverted output:\n")
        print(output)
    except Exception as e:
        print(f"\nError: {e}")

    input("\nPress Enter to exit...")
