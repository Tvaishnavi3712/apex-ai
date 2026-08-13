"""
Virtual Fields Service
Evaluates virtual columns and tables computed post-extraction

Supports:
- FORMULA: Mathematical expressions (subtotal + tax_amount)
- CONCATENATE: String concatenation (vendor_name + " - " + vendor_id)
- AGGREGATE: Array operations (sum, count, avg, min, max)
- CONDITIONAL: If/else expressions (if(amount > 1000, "HIGH", "LOW"))
- LOOKUP: Reference lookup from another field
"""

import re
import operator
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal
from functools import reduce


class VirtualFieldsProcessor:
    """
    Processes virtual columns and tables after document extraction.
    Enables data engineering without code.
    """

    # Supported operators for formulas
    OPERATORS = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '%': operator.mod,
        '==': operator.eq,
        '!=': operator.ne,
        '<': operator.lt,
        '<=': operator.le,
        '>': operator.gt,
        '>=': operator.ge,
    }

    # Aggregation functions
    AGGREGATIONS = {
        'sum': lambda arr: sum(arr) if arr else 0,
        'count': lambda arr: len(arr) if arr else 0,
        'avg': lambda arr: sum(arr) / len(arr) if arr else 0,
        'min': lambda arr: min(arr) if arr else None,
        'max': lambda arr: max(arr) if arr else None,
        'first': lambda arr: arr[0] if arr else None,
        'last': lambda arr: arr[-1] if arr else None,
    }

    def __init__(self):
        """Initialize the processor"""
        pass

    def process(
        self,
        extracted_data: Dict[str, Any],
        virtual_columns: List[Dict],
        virtual_tables: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process virtual fields and add them to extracted data.

        Args:
            extracted_data: The raw extracted data from BDA
            virtual_columns: List of VirtualColumn definitions
            virtual_tables: List of VirtualTable definitions

        Returns:
            Extracted data enhanced with virtual fields
        """
        result = dict(extracted_data)

        # Process virtual columns first
        for vc in virtual_columns:
            try:
                value = self._evaluate_virtual_column(vc, result)
                result[vc['name']] = value
            except Exception as e:
                result[vc['name']] = None
                result[f"_error_{vc['name']}"] = str(e)

        # Process virtual tables
        if virtual_tables:
            for vt in virtual_tables:
                try:
                    table_data = self._evaluate_virtual_table(vt, result)
                    result[vt['name']] = table_data
                except Exception as e:
                    result[vt['name']] = []
                    result[f"_error_{vt['name']}"] = str(e)

        return result

    def _evaluate_virtual_column(
        self,
        column: Dict,
        data: Dict[str, Any]
    ) -> Any:
        """Evaluate a single virtual column"""
        expression_type = column.get('expression_type', 'formula')
        expression = column.get('expression', '')

        if expression_type == 'formula':
            return self._evaluate_formula(expression, data)
        elif expression_type == 'concatenate':
            return self._evaluate_concatenate(expression, data)
        elif expression_type == 'aggregate':
            return self._evaluate_aggregate(expression, data)
        elif expression_type == 'conditional':
            return self._evaluate_conditional(expression, data)
        elif expression_type == 'lookup':
            return self._evaluate_lookup(expression, data)
        else:
            raise ValueError(f"Unknown expression type: {expression_type}")

    def _evaluate_formula(self, expression: str, data: Dict[str, Any]) -> Union[int, float]:
        """
        Evaluate a mathematical formula.
        Example: "subtotal + tax_amount" or "quantity * unit_price"
        """
        # Replace field references with actual values
        evaluated = self._substitute_fields(expression, data)

        # Safe evaluation of mathematical expression
        return self._safe_eval_math(evaluated)

    def _evaluate_concatenate(self, expression: str, data: Dict[str, Any]) -> str:
        """
        Evaluate string concatenation.
        Example: "vendor_name + ' - ' + vendor_id"
        """
        # Split by + and process each part
        parts = self._split_concat_expression(expression)
        result_parts = []

        for part in parts:
            part = part.strip()
            # Check if it's a string literal (quoted)
            if (part.startswith('"') and part.endswith('"')) or \
               (part.startswith("'") and part.endswith("'")):
                result_parts.append(part[1:-1])
            else:
                # It's a field reference
                value = self._get_field_value(part, data)
                result_parts.append(str(value) if value is not None else '')

        return ''.join(result_parts)

    def _evaluate_aggregate(self, expression: str, data: Dict[str, Any]) -> Any:
        """
        Evaluate an aggregation expression.
        Example: "sum(line_items.amount)" or "count(transactions)"
        """
        # Parse aggregation: func(array_field.property)
        match = re.match(r'(\w+)\(([^)]+)\)', expression.strip())
        if not match:
            raise ValueError(f"Invalid aggregation expression: {expression}")

        func_name = match.group(1).lower()
        field_path = match.group(2).strip()

        if func_name not in self.AGGREGATIONS:
            raise ValueError(f"Unknown aggregation function: {func_name}")

        # Get array values
        values = self._get_array_values(field_path, data)

        # Apply aggregation
        return self.AGGREGATIONS[func_name](values)

    def _evaluate_conditional(self, expression: str, data: Dict[str, Any]) -> Any:
        """
        Evaluate a conditional expression.
        Example: "if(amount > 1000, 'HIGH', 'LOW')"
        """
        # Parse: if(condition, true_value, false_value)
        match = re.match(r'if\s*\(\s*(.+?)\s*,\s*(.+?)\s*,\s*(.+?)\s*\)', expression.strip())
        if not match:
            raise ValueError(f"Invalid conditional expression: {expression}")

        condition = match.group(1).strip()
        true_value = match.group(2).strip()
        false_value = match.group(3).strip()

        # Evaluate condition
        condition_result = self._evaluate_condition(condition, data)

        # Return appropriate value
        if condition_result:
            return self._resolve_value(true_value, data)
        else:
            return self._resolve_value(false_value, data)

    def _evaluate_lookup(self, expression: str, data: Dict[str, Any]) -> Any:
        """
        Evaluate a lookup expression.
        Example: "vendor.payment_terms" or "totals.tax_rate"
        """
        return self._get_field_value(expression.strip(), data)

    def _evaluate_virtual_table(
        self,
        table: Dict,
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate a virtual table (aggregated view).

        Args:
            table: VirtualTable definition with source_array, group_by, aggregations
            data: Extracted data

        Returns:
            List of aggregated rows
        """
        source_array = table.get('source_array', '')
        group_by = table.get('group_by', [])
        aggregations = table.get('aggregations', [])

        # Get source array
        source_data = data.get(source_array, [])
        if not isinstance(source_data, list):
            return []

        if not group_by:
            # No grouping - aggregate entire array
            row = {}
            for agg in aggregations:
                agg_expr = agg.get('expression', '')
                # Replace array reference with source
                modified_expr = agg_expr.replace(source_array, '__source__')
                values = self._get_array_values_from_list(modified_expr, source_data)
                func_match = re.match(r'(\w+)\(', agg_expr)
                if func_match:
                    func_name = func_match.group(1).lower()
                    if func_name in self.AGGREGATIONS:
                        row[agg['name']] = self.AGGREGATIONS[func_name](values)
            return [row] if row else []

        # Group by specified fields
        groups = {}
        for item in source_data:
            key = tuple(item.get(g, '') for g in group_by)
            if key not in groups:
                groups[key] = []
            groups[key].append(item)

        # Build aggregated rows
        result = []
        for key, items in groups.items():
            row = dict(zip(group_by, key))

            for agg in aggregations:
                agg_expr = agg.get('expression', '')
                # Extract property from aggregation
                prop_match = re.search(r'\.(\w+)\)', agg_expr)
                if prop_match:
                    prop = prop_match.group(1)
                    values = [self._to_number(item.get(prop)) for item in items if item.get(prop) is not None]

                    func_match = re.match(r'(\w+)\(', agg_expr)
                    if func_match:
                        func_name = func_match.group(1).lower()
                        if func_name in self.AGGREGATIONS:
                            row[agg['name']] = self.AGGREGATIONS[func_name](values)

            result.append(row)

        return result

    def _substitute_fields(self, expression: str, data: Dict[str, Any]) -> str:
        """Replace field names with their values in an expression"""
        # Find all field references (word characters and dots)
        pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\b'

        def replacer(match):
            field_name = match.group(1)
            value = self._get_field_value(field_name, data)
            if value is None:
                return '0'
            if isinstance(value, (int, float, Decimal)):
                return str(float(value))
            return '0'

        return re.sub(pattern, replacer, expression)

    def _get_field_value(self, field_path: str, data: Dict[str, Any]) -> Any:
        """Get a field value by path (supports dot notation)"""
        parts = field_path.split('.')
        current = data

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and part.isdigit():
                idx = int(part)
                current = current[idx] if idx < len(current) else None
            else:
                return None

            if current is None:
                return None

        return current

    def _get_array_values(self, field_path: str, data: Dict[str, Any]) -> List:
        """Get values from an array field"""
        parts = field_path.split('.')

        if len(parts) == 1:
            # Direct array field
            arr = data.get(parts[0], [])
            return [self._to_number(v) for v in arr if v is not None]

        # Array.property pattern
        array_field = parts[0]
        property_path = '.'.join(parts[1:])

        arr = data.get(array_field, [])
        if not isinstance(arr, list):
            return []

        values = []
        for item in arr:
            value = self._get_field_value(property_path, item) if isinstance(item, dict) else None
            if value is not None:
                values.append(self._to_number(value))

        return values

    def _get_array_values_from_list(self, expression: str, items: List) -> List:
        """Get values from a list of items"""
        # Extract property from expression like "sum(__source__.amount)"
        match = re.search(r'__source__\.(\w+)', expression)
        if not match:
            return []

        prop = match.group(1)
        return [self._to_number(item.get(prop)) for item in items if isinstance(item, dict) and item.get(prop) is not None]

    def _split_concat_expression(self, expression: str) -> List[str]:
        """Split concatenation expression respecting quoted strings"""
        parts = []
        current = ""
        in_quotes = False
        quote_char = None

        for char in expression:
            if char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
                current += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current += char
            elif char == '+' and not in_quotes:
                if current.strip():
                    parts.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            parts.append(current.strip())

        return parts

    def _evaluate_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        """Evaluate a boolean condition"""
        # Find comparison operator
        for op in ['>=', '<=', '!=', '==', '>', '<']:
            if op in condition:
                left, right = condition.split(op, 1)
                left_val = self._resolve_value(left.strip(), data)
                right_val = self._resolve_value(right.strip(), data)

                left_num = self._to_number(left_val)
                right_num = self._to_number(right_val)

                return self.OPERATORS[op](left_num, right_num)

        # Default to truthy check
        value = self._resolve_value(condition, data)
        return bool(value)

    def _resolve_value(self, value_str: str, data: Dict[str, Any]) -> Any:
        """Resolve a value - could be literal or field reference"""
        value_str = value_str.strip()

        # String literal
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]

        # Number literal
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass

        # Boolean literals
        if value_str.lower() == 'true':
            return True
        if value_str.lower() == 'false':
            return False
        if value_str.lower() == 'null' or value_str.lower() == 'none':
            return None

        # Field reference
        return self._get_field_value(value_str, data)

    def _to_number(self, value: Any) -> Union[int, float]:
        """Convert a value to a number"""
        if value is None:
            return 0
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, str):
            try:
                # Remove currency symbols and commas
                cleaned = re.sub(r'[,$£€¥]', '', value)
                if '.' in cleaned:
                    return float(cleaned)
                return int(cleaned)
            except ValueError:
                return 0
        return 0

    def _safe_eval_math(self, expression: str) -> Union[int, float]:
        """
        Safely evaluate a mathematical expression.
        Only allows numbers and basic operators.
        """
        # Validate expression contains only safe characters
        if not re.match(r'^[\d\s\.\+\-\*\/\%\(\)]+$', expression):
            raise ValueError(f"Unsafe expression: {expression}")

        try:
            # Use eval with empty globals/locals for safety
            result = eval(expression, {"__builtins__": {}}, {})
            return result
        except Exception as e:
            raise ValueError(f"Failed to evaluate expression '{expression}': {e}")


# Convenience function
def process_virtual_fields(
    extracted_data: Dict[str, Any],
    blueprint: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process virtual fields for a blueprint.

    Args:
        extracted_data: Raw extracted data from BDA
        blueprint: Blueprint definition with virtual_columns and virtual_tables

    Returns:
        Enhanced extracted data with virtual fields
    """
    processor = VirtualFieldsProcessor()

    virtual_columns = blueprint.get('virtual_columns', [])
    virtual_tables = blueprint.get('virtual_tables', [])

    if not virtual_columns and not virtual_tables:
        return extracted_data

    return processor.process(extracted_data, virtual_columns, virtual_tables)
