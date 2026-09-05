"""
Продвинутый многоуровневый ИИ-Наставник (Deep AI Error Inspector & Live Mentor).
Выполняет многослойный статический и семантический анализ кода на лету,
находит синтаксические, логические и типовые ошибки с авто-исправлением в 1 клик.
"""

import ast
import re
import builtins
import difflib
from typing import Dict, Any, List, Optional, Set

# Стандартные модули для автоопределения пропущенных импортов
COMMON_MODULES = {
    "re": ["search", "match", "findall", "sub", "compile", "split"],
    "json": ["loads", "dumps", "load", "dump"],
    "math": ["sqrt", "sin", "cos", "tan", "pi", "floor", "ceil", "pow", "log"],
    "os": ["path", "environ", "listdir", "remove", "mkdir", "getcwd"],
    "sys": ["argv", "exit", "path", "version", "executable"],
    "pathlib": ["Path"],
    "asyncio": ["run", "sleep", "create_task", "gather", "TaskGroup", "Semaphore", "Queue"],
    "time": ["sleep", "time", "perf_counter"],
    "datetime": ["datetime", "date", "timedelta", "timezone"],
    "random": ["randint", "choice", "shuffle", "random", "sample"],
    "sqlite3": ["connect", "Row"],
    "requests": ["get", "post", "put", "delete"],
    "pydantic": ["BaseModel", "Field", "field_validator"],
    "typing": ["List", "Dict", "Optional", "Union", "Any", "Callable", "Tuple", "Set"]
}

class ScopeAnalyzer(ast.NodeVisitor):
    """Анализатор областей видимости и необъявленных переменных"""
    def __init__(self):
        self.defined_names: Set[str] = set(dir(builtins))
        self.used_names: List[tuple[str, int, int]] = [] # (name, lineno, col_offset)
        self.imports: Set[str] = set()
        self.functions_defined: Set[str] = set()

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname or alias.name
            self.defined_names.add(name)
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            name = alias.asname or alias.name
            self.defined_names.add(name)
            if node.module:
                self.imports.add(f"{node.module}.{alias.name}")
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.defined_names.add(node.name)
        self.functions_defined.add(node.name)
        # Добавляем аргументы функции в локальную область
        for arg in node.args.args:
            self.defined_names.add(arg.arg)
        if node.args.vararg:
            self.defined_names.add(node.args.vararg.arg)
        if node.args.kwarg:
            self.defined_names.add(node.args.kwarg.arg)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        self.defined_names.add(node.name)
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.defined_names.add(target.id)
            elif isinstance(target, (ast.Tuple, ast.List)):
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        self.defined_names.add(elt.id)
        self.generic_visit(node)

    def visit_For(self, node):
        if isinstance(node.target, ast.Name):
            self.defined_names.add(node.target.id)
        elif isinstance(node.target, (ast.Tuple, ast.List)):
            for elt in node.target.elts:
                if isinstance(elt, ast.Name):
                    self.defined_names.add(elt.id)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_names.append((node.id, node.lineno, node.col_offset))
        self.generic_visit(node)


class LiveErrorMentorService:
    @classmethod
    def inspect_code(cls, code: str) -> Dict[str, Any]:
        """
        Многоуровневый интеллектуальный анализ кода в реальном времени.
        """
        clean_code = code.strip()
        if not clean_code:
            return cls._format_response({
                "has_errors": False,
                "status": "empty",
                "severity": "info",
                "message": "Окно наставника активно. Начните писать код...",
                "line": None,
                "hint": None,
                "suggested_fix": None
            })

        # ---------------- СЛОЙ 1: КОМПИЛЯЦИЯ И СИНТАКСИС ----------------
        try:
            compile(code, "<editor>", "exec")
            tree = ast.parse(code)
        except SyntaxError as e:
            return cls._format_response(cls._diagnose_syntax_error(e, code))
        except Exception as e:
            return cls._format_response({
                "has_errors": True,
                "status": "syntax_error",
                "severity": "critical",
                "line": getattr(e, 'lineno', 1),
                "message": f"Критическая ошибка синтаксиса: {str(e)}",
                "hint": "Проверьте корректность расстановки скобок, кавычек и двоеточий.",
                "suggested_fix": None
            })

        # ---------------- СЛОЙ 2: АНАЛИЗ ПЕРЕМЕННЫХ И ИМПОРТОВ ----------------
        scope_error = cls._diagnose_scope_and_names(tree, code)
        if scope_error:
            return cls._format_response(scope_error)

        # ---------------- СЛОЙ 3: ЛОГИЧЕСКИЕ И ТИПОВЫЕ АНТИПАТТЕРНЫ ----------------
        ast_diagnostics = cls._diagnose_ast_deep(tree, code)
        if ast_diagnostics:
            return cls._format_response(ast_diagnostics)

        # Если все проверки пройдены
        return cls._format_response({
            "has_errors": False,
            "status": "clean",
            "severity": "success",
            "message": "✨ Отлично! Код синтаксически корректен, переменные объявлены верно.",
            "line": None,
            "hint": "Код готов к запуску или проверке тест-кейсов.",
            "suggested_fix": None
        })

    @classmethod
    def _format_response(cls, res: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        if res.get("has_errors") or res.get("severity") in ("warning", "critical", "error"):
            issues.append({
                "title": res.get("status", "error").replace("_", " ").title(),
                "message": res.get("message", ""),
                "advice": res.get("hint", ""),
                "line": res.get("line") or 1,
                "column": res.get("column") or 1,
                "severity": "error" if res.get("severity") == "critical" else (res.get("severity") or "warning"),
                "fix_code": res.get("suggested_fix")
            })
        res["issues"] = issues
        res["fix_code"] = res.get("suggested_fix")
        res["has_syntax_error"] = res.get("status") == "syntax_error"
        return res

    @classmethod
    def _diagnose_syntax_error(cls, err: SyntaxError, code: str) -> Dict[str, Any]:
        line_no = err.lineno or 1
        raw_msg = err.msg or ""
        lines = code.split("\n")
        problem_line = lines[line_no - 1] if 0 < line_no <= len(lines) else ""

        explanation = "Обнаружена синтаксическая ошибка."
        hint = "Проверьте структуру строки."
        suggested_fix = None

        # 1. Пропущено двоеточие в конце блока
        if "expected ':'" in raw_msg or re.search(r'^\s*(if|elif|else|for|while|def|class|with|try|except|finally)\b[^:]*$', problem_line):
            explanation = f"На строке {line_no} пропущено обязательное двоеточие `:` в конце заголовка блока."
            hint = "В Python после `if`, `elif`, `else`, `for`, `while`, `def`, `class` обязательно ставить двоеточие `:`."
            if problem_line.strip() and not problem_line.rstrip().endswith(":"):
                fixed_line = problem_line.rstrip() + ":"
                suggested_fix = cls._replace_line(code, line_no, fixed_line)

        # 2. Одиночное равно '=' в условии if / while
        elif "cannot assign to" in raw_msg or "invalid syntax. Maybe you meant '=='" in raw_msg or re.search(r'\b(if|elif|while)\s+[\w\.\'"]+\s*=\s*[\w\.\'"]+', problem_line):
            explanation = f"На строке {line_no} использован оператор присваивания `=` вместо оператора проверки равенства `==`."
            hint = "Для сравнения значений в условии используйте двойное равно `==` или ключевое слово `is`."
            fixed_line = re.sub(r'(\b(?:if|elif|while)\s+[\w\.\'"]+)\s*=\s*', r'\1 == ', problem_line)
            suggested_fix = cls._replace_line(code, line_no, fixed_line)

        # 3. Незакрытая скобка
        elif "was never closed" in raw_msg or "unmatched" in raw_msg or "(" in problem_line and ")" not in problem_line:
            bracket = "круглую `)`" if "(" in problem_line else "фигурную `}`" if "{" in problem_line else "квадратную `]`"
            explanation = f"На строке {line_no} открыта, но не закрыта {bracket} скобка."
            hint = f"Убедитесь, что каждая открытая скобка имеет соответствующую закрывающую."

        # 4. Нарушение отступов
        elif isinstance(err, (IndentationError, TabError)) or "indent" in raw_msg.lower():
            explanation = f"Ошибка отступов (IndentationError) на строке {line_no}."
            hint = "Блоки кода внутри функций и циклов должны иметь отступ в 4 пробела. Не смешивайте табуляцию и пробелы."
            fixed_line = "    " + problem_line.lstrip()
            suggested_fix = cls._replace_line(code, line_no, fixed_line)

        # 5. Незакрытая кавычка строки
        elif "unterminated string literal" in raw_msg or "EOL while scanning" in raw_msg:
            explanation = f"На строке {line_no} не закрыта кавычка строкового литерала."
            hint = "Строка должна начинаться и заканчиваться одинаковой кавычкой (`'` или `\"`)."

        # 6. Опечатки в ключевых словах (def, return, import, etc.)
        else:
            typo_map = {
                "fucn": "def", "func": "def", "df": "def", "reutrn": "return", "retrun": "return",
                "improt": "import", "impor": "import", "whlie": "while", "pritn": "print",
                "prnt": "print", "true": "True", "false": "False", "none": "None"
            }
            for typo, correct in typo_map.items():
                if re.search(r'\b' + re.escape(typo) + r'\b', problem_line):
                    explanation = f"На строке {line_no} найдена опечатка: `{typo}` вместо ключевого слова `{correct}`."
                    hint = f"Замените `{typo}` на `{correct}`."
                    fixed_line = re.sub(r'\b' + re.escape(typo) + r'\b', correct, problem_line)
                    suggested_fix = cls._replace_line(code, line_no, fixed_line)
                    break
            else:
                explanation = f"Синтаксическая ошибка на строке {line_no}: «{problem_line.strip()}»."
                hint = "Проверьте имена функций, операторы и скобки."

        return {
            "has_errors": True,
            "status": "syntax_error",
            "severity": "critical",
            "line": line_no,
            "problem_snippet": problem_line.strip(),
            "message": explanation,
            "hint": hint,
            "suggested_fix": suggested_fix
        }

    @classmethod
    def _diagnose_scope_and_names(cls, tree: ast.AST, code: str) -> Optional[Dict[str, Any]]:
        """Проверка на NameError и забытые импорты модулей"""
        analyzer = ScopeAnalyzer()
        analyzer.visit(tree)

        for name, line_no, _ in analyzer.used_names:
            if name not in analyzer.defined_names:
                # 1. Проверяем, не является ли это вызовом стандартного модуля без import
                for mod_name, methods in COMMON_MODULES.items():
                    if name == mod_name:
                        return {
                            "has_errors": True,
                            "status": "missing_import",
                            "severity": "critical",
                            "line": line_no,
                            "message": f"🚫 Использование модуля `{name}` на строке {line_no} без импорта (`NameError: name '{name}' is not defined`).",
                            "hint": f"Добавьте строку `import {name}` в самое начало файла.",
                            "suggested_fix": f"import {name}\n\n" + code
                        }
                    elif name in methods and name not in dir(builtins):
                        return {
                            "has_errors": True,
                            "status": "missing_import",
                            "severity": "critical",
                            "line": line_no,
                            "message": f"🚫 Функция `{name}` на строке {line_no} требует импорта из модуля `{mod_name}`.",
                            "hint": f"Добавьте строку `from {mod_name} import {name}` в начало программы.",
                            "suggested_fix": f"from {mod_name} import {name}\n\n" + code
                        }

                # 2. Поиск похожих объявленных имен (опечатки в переменных)
                all_known = list(analyzer.defined_names)
                close_matches = difflib.get_close_matches(name, all_known, n=1, cutoff=0.7)
                if close_matches:
                    suggestion = close_matches[0]
                    lines = code.split("\n")
                    prob_line = lines[line_no - 1] if 0 < line_no <= len(lines) else ""
                    fixed_line = re.sub(r'\b' + re.escape(name) + r'\b', suggestion, prob_line)
                    return {
                        "has_errors": True,
                        "status": "name_typo",
                        "severity": "critical",
                        "line": line_no,
                        "message": f"🚫 Переменная `{name}` на строке {line_no} не найдена. Возможно, вы имели в виду `{suggestion}`?",
                        "hint": f"Замените опечатку `{name}` на объявленную переменную `{suggestion}`.",
                        "suggested_fix": cls._replace_line(code, line_no, fixed_line)
                    }

                # Неопределенная переменная
                return {
                    "has_errors": True,
                    "status": "undefined_name",
                    "severity": "critical",
                    "line": line_no,
                    "message": f"🚫 Переменная `{name}` на строке {line_no} используется до её объявления (`NameError`).",
                    "hint": f"Обязательно присвойте значение переменной `{name}` перед её использованием.",
                    "suggested_fix": None
                }

        return None

    @classmethod
    def _diagnose_ast_deep(cls, tree: ast.AST, code: str) -> Optional[Dict[str, Any]]:
        """Глубокая проверка AST на логические ловушки и пропущенные конструкции"""
        for node in ast.walk(tree):
            # 1. Пропущенный 'self' в методе класса
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and not item.name.startswith("__"):
                        # Проверяем, если нет декоратора @staticmethod или @classmethod
                        decorators = [d.id for d in item.decorator_list if isinstance(d, ast.Name)]
                        if "staticmethod" not in decorators and "classmethod" not in decorators:
                            if not item.args.args or item.args.args[0].arg != "self":
                                line_no = item.lineno
                                lines = code.split("\n")
                                prob_line = lines[line_no - 1] if 0 < line_no <= len(lines) else ""
                                fixed_line = re.sub(r'def\s+' + re.escape(item.name) + r'\s*\((.*?)\)', r'def ' + item.name + r'(self, \1)', prob_line)
                                fixed_line = fixed_line.replace("(self, )", "(self)")
                                return {
                                    "has_errors": True,
                                    "status": "missing_self",
                                    "severity": "critical",
                                    "line": line_no,
                                    "message": f"⚠️ Метод `{item.name}` класса `{node.name}` (строка {line_no}) не содержит `self` в качестве первого аргумента.",
                                    "hint": "Все методы экземпляра класса в Python должны первым аргументом принимать `self`.",
                                    "suggested_fix": cls._replace_line(code, line_no, fixed_line)
                                }

            # 2. Вызов асинхронной функции без await
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                # Проверяем очевидные async вызовы (например, asyncio.sleep)
                if isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "sleep":
                    if isinstance(node.value.func.value, ast.Name) and node.value.func.value.id == "asyncio":
                        line_no = node.lineno
                        lines = code.split("\n")
                        prob_line = lines[line_no - 1] if 0 < line_no <= len(lines) else ""
                        if "await" not in prob_line:
                            fixed_line = prob_line.replace("asyncio.sleep", "await asyncio.sleep")
                            return {
                                "has_errors": True,
                                "status": "missing_await",
                                "severity": "critical",
                                "line": line_no,
                                "message": f"⚠️ Асинхронная корутина `asyncio.sleep()` на строке {line_no} вызвана без ключевого слова `await`.",
                                "hint": "Вызов корутины без `await` создает объект корутины, но не выполняет его!",
                                "suggested_fix": cls._replace_line(code, line_no, fixed_line)
                            }

            # 3. Сравнение строк или чисел через `is` вместо `==`
            elif isinstance(node, ast.Compare):
                for op in node.ops:
                    if isinstance(op, (ast.Is, ast.IsNot)):
                        if isinstance(node.comparators[0], (ast.Constant, ast.Str, ast.Num)):
                            if not (isinstance(node.comparators[0], ast.Constant) and node.comparators[0].value in (None, True, False)):
                                line_no = node.lineno
                                return {
                                    "has_errors": False,
                                    "status": "warning",
                                    "severity": "warning",
                                    "line": line_no,
                                    "message": f"⚠️ Использование оператора `is` с литералом (строка {line_no}).",
                                    "hint": "Оператор `is` проверяет идентичность объектов в памяти (id). Для проверки равенства значений используйте `==`.",
                                    "suggested_fix": None
                                }

            # 4. Изменяемый аргумент по умолчанию (def foo(items=[]))
            elif isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        line_no = getattr(node, 'lineno', 1)
                        return {
                            "has_errors": False,
                            "status": "mutable_default",
                            "severity": "warning",
                            "line": line_no,
                            "message": f"⚠️ Изменяемый аргумент по умолчанию в функции `{node.name}` (строка {line_no}).",
                            "hint": "Список или словарь по умолчанию разделяется между всеми вызовами функции. Рекомендуется использовать `arg=None`.",
                            "suggested_fix": None
                        }

            # 5. Деление на ноль в константах
            elif isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                if isinstance(node.right, ast.Constant) and node.right.value == 0:
                    line_no = getattr(node, 'lineno', 1)
                    return {
                        "has_errors": True,
                        "status": "zero_division",
                        "severity": "critical",
                        "line": line_no,
                        "message": f"🚫 Деление на ноль (ZeroDivisionError) на строке {line_no}.",
                        "hint": "Деление на 0 приведет к падению программы.",
                        "suggested_fix": None
                    }

        return None

    @classmethod
    def _replace_line(cls, code: str, line_no: int, new_line: str) -> str:
        lines = code.split("\n")
        if 0 < line_no <= len(lines):
            lines[line_no - 1] = new_line
        return "\n".join(lines)
