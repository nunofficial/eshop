"""Архитектурные тесты: границы модулей проверяются автоматически (анализ import через ast)."""
import ast, pathlib, unittest

SRC = pathlib.Path(__file__).resolve().parent.parent / "src"
MODULES = {"users", "catalog", "orders", "billing"}
# Разрешённые зависимости между модулями (кто -> кого)
ALLOWED = {"users": set(), "catalog": set(), "billing": set(), "orders": {"users", "catalog"}}

def imports_of(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                yield a.name, 0
        elif isinstance(node, ast.ImportFrom):
            yield (node.module or ""), node.level

def collect():
    edges, violations = {m: set() for m in MODULES}, []
    for m in MODULES:
        for f in (SRC / m).rglob("*.py"):
            for name, level in imports_of(f):
                if level > 1:
                    violations.append(f"{f}: относительный импорт за пределы модуля")
                parts = name.split(".")
                if level == 0 and parts[0] == "src" and len(parts) > 1 and parts[1] in MODULES and parts[1] != m:
                    edges[m].add(parts[1])
                    if "internal" in parts:
                        violations.append(f"{f.relative_to(SRC)}: импорт internal модуля {parts[1]}")
    return edges, violations

class ArchitectureTests(unittest.TestCase):
    def test_no_internal_access(self):
        _, v = collect()
        self.assertEqual(v, [])

    def test_only_allowed_dependencies(self):
        edges, _ = collect()
        for m, deps in edges.items():
            self.assertLessEqual(deps, ALLOWED[m], f"{m} зависит от лишнего: {deps - ALLOWED[m]}")

    def test_no_cycles(self):
        edges, _ = collect()
        def dfs(n, stack):
            self.assertNotIn(n, stack, f"цикл: {stack + [n]}")
            for d in edges[n]:
                dfs(d, stack + [n])
        for m in MODULES:
            dfs(m, [])

    def test_billing_does_not_know_orders(self):
        edges, _ = collect()
        self.assertNotIn("orders", edges["billing"])

    def test_shared_kernel_is_independent(self):
        for f in (SRC / "shared_kernel").rglob("*.py"):
            for name, _ in imports_of(f):
                self.assertFalse(any(name.startswith(f"src.{m}") for m in MODULES), f"{f}: {name}")

if __name__ == "__main__":
    unittest.main()
