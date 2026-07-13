import ast
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python ast_parser.py <target_file.py>")
        sys.exit(1)

    target_file = sys.argv[1]

    if not os.path.exists(target_file):
        print(f"Error: File '{target_file}' not found.")
        sys.exit(1)

    with open(target_file, "r", encoding="utf-8") as f:
        source_code = f.read()

    try:
        # ast.parse() takes the raw source code text and converts it into an Abstract Syntax Tree (AST).
        # An AST is a tree representation of the syntactic structure of the code, making it easy to analyze programmatically.
        tree = ast.parse(source_code)
    except SyntaxError as e:
        print(f"Syntax error in target file at line {e.lineno}: {e.msg}")
        sys.exit(1)

    print(f"{'Line':<6} | {'Variable':<20} | {'Expression'}")
    print("-" * 60)

    # ast.walk() generates all nodes in the tree recursively, in no specified order.
    # It allows us to easily visit every single node in the AST without writing a custom recursive visitor class.
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            # TODO: Handle augmented assignments (+=, -=), annotated assignments (x: int = 5),
            # and multiple/tuple targets (a, b = 1, 2) in a later iteration.
            
            # For now, only focus on single-target Assign nodes where target is a Name
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                target = node.targets[0]
                line_number = node.lineno
                variable_name = target.id
                
                # ast.unparse() takes an AST node and converts it back into a readable string of Python code.
                # This is super useful for turning the parsed expression back into human-readable source text.
                expression = ast.unparse(node.value)
                
                print(f"{line_number:<6} | {variable_name:<20} | {expression}")

if __name__ == "__main__":
    main()
