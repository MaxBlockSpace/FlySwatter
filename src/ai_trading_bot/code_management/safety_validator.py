import logging
from typing import Dict, Any, List
import ast
from pathlib import Path

class SafetyValidator:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.code_management.validator')
        self.unsafe_patterns = {
            'system_calls': ['os.system', 'subprocess'],
            'file_operations': ['open', 'write', 'delete'],
            'network_calls': ['socket', 'requests'],
            'code_execution': ['eval', 'exec', 'compile']
        }
        self.protected_modules = [
            'north_star.py',
            'safety_validator.py',
            'core_config.py'
        ]

    async def validate_changes(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        try:
            issues = []
            
            # Check for protected file modifications
            protected_issues = self._check_protected_files(changes)
            if protected_issues:
                issues.extend(protected_issues)

            # Validate each file
            for file_path, content in changes['files'].items():
                file_issues = self._validate_file(file_path, content)
                issues.extend(file_issues)

            # Check for breaking changes
            breaking_issues = self._check_breaking_changes(changes)
            if breaking_issues:
                issues.extend(breaking_issues)

            return {
                'is_safe': len(issues) == 0,
                'issues': issues
            }

        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return {
                'is_safe': False,
                'issues': [str(e)]
            }

    def _check_protected_files(self, changes: Dict[str, Any]) -> List[str]:
        issues = []
        for file_path in changes['files']:
            if any(protected in file_path for protected in self.protected_modules):
                issues.append(f"Cannot modify protected file: {file_path}")
        return issues

    def _validate_file(self, file_path: str, content: str) -> List[str]:
        issues = []
        
        try:
            # Parse the code
            tree = ast.parse(content)
            
            # Check for unsafe patterns
            visitor = SafetyVisitor(self.unsafe_patterns)
            visitor.visit(tree)
            issues.extend(visitor.issues)
            
            # Check complexity
            complexity_issues = self._check_complexity(tree)
            issues.extend(complexity_issues)
            
            # Check imports
            import_issues = self._check_imports(tree)
            issues.extend(import_issues)
            
        except SyntaxError as e:
            issues.append(f"Syntax error in {file_path}: {str(e)}")
        except Exception as e:
            issues.append(f"Validation error in {file_path}: {str(e)}")
            
        return issues

    def _check_complexity(self, tree: ast.AST) -> List[str]:
        issues = []
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        if visitor.max_depth > 5:
            issues.append(f"Excessive nesting depth: {visitor.max_depth}")
            
        if visitor.max_complexity > 10:
            issues.append(f"Excessive cyclomatic complexity: {visitor.max_complexity}")
            
        return issues

    def _check_imports(self, tree: ast.AST) -> List[str]:
        issues = []
        visitor = ImportVisitor()
        visitor.visit(tree)
        
        for import_name in visitor.imports:
            if import_name in self.unsafe_patterns.values():
                issues.append(f"Unsafe import: {import_name}")
                
        return issues

    def _check_breaking_changes(self, changes: Dict[str, Any]) -> List[str]:
        issues = []
        
        # Check for interface changes
        interface_changes = self._find_interface_changes(changes)
        if interface_changes:
            issues.extend(interface_changes)
            
        # Check for dependency changes
        dependency_issues = self._check_dependencies(changes)
        if dependency_issues:
            issues.extend(dependency_issues)
            
        return issues

    def _find_interface_changes(self, changes: Dict[str, Any]) -> List[str]:
        issues = []
        
        for file_path, content in changes['files'].items():
            try:
                old_tree = ast.parse(Path(file_path).read_text())
                new_tree = ast.parse(content)
                
                old_interfaces = InterfaceVisitor()
                new_interfaces = InterfaceVisitor()
                
                old_interfaces.visit(old_tree)
                new_interfaces.visit(new_tree)
                
                # Check for removed or modified interfaces
                for name, sig in old_interfaces.interfaces.items():
                    if name not in new_interfaces.interfaces:
                        issues.append(f"Removed interface: {name}")
                    elif sig != new_interfaces.interfaces[name]:
                        issues.append(f"Modified interface: {name}")
                        
            except Exception as e:
                self.logger.error(f"Interface check failed for {file_path}: {e}")
                
        return issues

    def _check_dependencies(self, changes: Dict[str, Any]) -> List[str]:
        issues = []
        
        # Check for new dependencies
        for file_path, content in changes['files'].items():
            try:
                tree = ast.parse(content)
                visitor = DependencyVisitor()
                visitor.visit(tree)
                
                for dep in visitor.dependencies:
                    if not self._is_safe_dependency(dep):
                        issues.append(f"Unsafe dependency: {dep}")
                        
            except Exception as e:
                self.logger.error(f"Dependency check failed for {file_path}: {e}")
                
        return issues

    def _is_safe_dependency(self, dependency: str) -> bool:
        # Implement dependency safety checks
        return True


class SafetyVisitor(ast.NodeVisitor):
    def __init__(self, unsafe_patterns: Dict[str, List[str]]):
        self.unsafe_patterns = unsafe_patterns
        self.issues = []

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            for category, patterns in self.unsafe_patterns.items():
                if func_name in patterns:
                    self.issues.append(f"Unsafe {category} call: {func_name}")
        self.generic_visit(node)


class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.current_depth = 0
        self.max_depth = 0
        self.current_complexity = 0
        self.max_complexity = 0

    def visit(self, node: ast.AST):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        
        if isinstance(node, (ast.If, ast.While, ast.For)):
            self.current_complexity += 1
            self.max_complexity = max(self.max_complexity, self.current_complexity)
            
        super().visit(node)
        self.current_depth -= 1


class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports = set()

    def visit_Import(self, node: ast.Import):
        for name in node.names:
            self.imports.add(name.name)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self.imports.add(node.module)


class InterfaceVisitor(ast.NodeVisitor):
    def __init__(self):
        self.interfaces = {}

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.interfaces[node.name] = self._get_signature(node)

    def _get_signature(self, node: ast.FunctionDef) -> str:
        args = [arg.arg for arg in node.args.args]
        return f"{node.name}({', '.join(args)})"


class DependencyVisitor(ast.NodeVisitor):
    def __init__(self):
        self.dependencies = set()

    def visit_Import(self, node: ast.Import):
        for name in node.names:
            self.dependencies.add(name.name)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self.dependencies.add(node.module)