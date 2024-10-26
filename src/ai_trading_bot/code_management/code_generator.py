import logging
from typing import Dict, Any
import openai
from pathlib import Path

class CodeGenerator:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.code_management.generator')

    async def generate_changes(
        self,
        insights: Dict[str, Any],
        module_path: str,
        change_type: str
    ) -> Dict[str, Any]:
        try:
            # Read existing code
            existing_code = self._read_module(module_path)

            # Generate improved code
            changes = await self._generate_code(
                existing_code,
                insights,
                change_type
            )

            # Validate syntax
            if not self._validate_syntax(changes['files']):
                raise ValueError("Generated code has syntax errors")

            return changes

        except Exception as e:
            self.logger.error(f"Failed to generate changes: {e}")
            raise

    def _read_module(self, module_path: str) -> Dict[str, str]:
        try:
            module_dir = Path(module_path)
            files = {}
            
            if module_dir.is_file():
                files[module_dir.name] = module_dir.read_text()
            else:
                for file_path in module_dir.rglob('*.py'):
                    files[str(file_path.relative_to(module_dir))] = file_path.read_text()
                    
            return files
        except Exception as e:
            self.logger.error(f"Failed to read module: {e}")
            raise

    async def _generate_code(
        self,
        existing_code: Dict[str, str],
        insights: Dict[str, Any],
        change_type: str
    ) -> Dict[str, Any]:
        try:
            prompt = self._create_prompt(
                existing_code,
                insights,
                change_type
            )

            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert code generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            generated = self._parse_response(response.choices[0].message.content)
            
            return {
                'files': generated['files'],
                'type': change_type,
                'description': generated['description']
            }

        except Exception as e:
            self.logger.error(f"Failed to generate code: {e}")
            raise

    def _create_prompt(
        self,
        existing_code: Dict[str, str],
        insights: Dict[str, Any],
        change_type: str
    ) -> str:
        return f"""
Given the following existing code and insights, generate improved code that implements the necessary changes.

Existing Code:
{self._format_code_for_prompt(existing_code)}

Insights:
{insights.get('description', '')}

Change Type: {change_type}

Requirements:
1. Maintain or improve code quality
2. Ensure backward compatibility
3. Follow Python best practices
4. Include proper error handling
5. Add comprehensive logging
6. Update tests as needed

Please provide:
1. Modified code files
2. A clear description of changes
3. Any necessary migration steps
"""

    def _format_code_for_prompt(self, code_files: Dict[str, str]) -> str:
        formatted = []
        for file_name, content in code_files.items():
            formatted.append(f"File: {file_name}\n```python\n{content}\n```\n")
        return "\n".join(formatted)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        # Implement response parsing logic
        return {
            'files': {},
            'description': ''
        }

    def _validate_syntax(self, files: Dict[str, str]) -> bool:
        try:
            for content in files.values():
                compile(content, '<string>', 'exec')
            return True
        except SyntaxError:
            return False