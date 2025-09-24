import json
import re


class JsonHelper:
    @staticmethod
    def normalize_json(data_str):
        """
        Function to normalize JSON with inconsistent escaping.
        This handles cases where JSON strings are nested or double-serialized.
        """
        # If it's already a Python object, not a string
        if not isinstance(data_str, str):
            return JsonHelper.process_nested_json(data_str)

        # Try to parse as-is first
        try:
            parsed_data = json.loads(data_str)
            # Process any nested JSON strings
            return JsonHelper.process_nested_json(parsed_data)
        except json.JSONDecodeError:
            # Not valid JSON, try to fix it
            pass

        # Try a safer approach using ast.literal_eval for Python dict strings
        try:
            import ast
            # Use ast.literal_eval to safely evaluate Python literals
            parsed_data = ast.literal_eval(data_str)
            return JsonHelper.process_nested_json(parsed_data)
        except (SyntaxError, ValueError):
            # Not a valid Python literal, continue with other approaches
            pass

        # If all attempts failed, try a more detailed diagnosis
        try:
            # Try to identify and fix specific issues
            # 1. Replace single quotes with double quotes, but only for keys and string values
            # This regex matches keys or string values in quotes
            fixed_str = re.sub(r'\'([^\']+)\'', r'"\1"', data_str)

            # 2. Fix Python literals
            fixed_str = fixed_str.replace("None", "null").replace("True", "true").replace("False", "false")

            # 3. Fix trailing commas in objects and arrays (common Python vs JSON issue)
            fixed_str = re.sub(r',\s*}', '}', fixed_str)
            fixed_str = re.sub(r',\s*\]', ']', fixed_str)

            # Try to parse the fixed string
            parsed_data = json.loads(fixed_str)
            return JsonHelper.process_nested_json(parsed_data)
        except json.JSONDecodeError as e:
            # Return detailed error information for debugging
            return {
                "error": f"Failed to parse JSON after all attempts: {str(e)}",
                "original_data": data_str[:50] + "..." if len(data_str) > 50 else data_str,
                "position": e.pos,
                "line": e.lineno,
                "column": e.colno
            }

    @staticmethod
    def process_nested_json(data):
        """
        Recursively process nested JSON strings in the data structure.
        """
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if isinstance(value, str):
                    if (value.startswith('{') and value.endswith('}')) or (
                            value.startswith('[') and value.endswith(']')):
                        try:
                            # Try to parse as JSON directly
                            parsed_value = json.loads(value)
                            result[key] = JsonHelper.process_nested_json(parsed_value)
                        except json.JSONDecodeError:
                            try:
                                # Try to fix Python-style dict/list strings
                                import ast
                                parsed_value = ast.literal_eval(value)
                                result[key] = JsonHelper.process_nested_json(parsed_value)
                            except (SyntaxError, ValueError):
                                # If both approaches fail, keep as string
                                result[key] = value
                    else:
                        result[key] = value
                elif isinstance(value, (dict, list)):
                    result[key] = JsonHelper.process_nested_json(value)
                else:
                    result[key] = value
            return result

        elif isinstance(data, list):
            result = []
            for item in data:
                if isinstance(item, str):
                    if (item.startswith('{') and item.endswith('}')) or (item.startswith('[') and item.endswith(']')):
                        try:
                            parsed_item = json.loads(item)
                            result.append(JsonHelper.process_nested_json(parsed_item))
                        except json.JSONDecodeError:
                            try:
                                import ast
                                parsed_item = ast.literal_eval(item)
                                result.append(JsonHelper.process_nested_json(parsed_item))
                            except (SyntaxError, ValueError):
                                result.append(item)
                    else:
                        result.append(item)
                elif isinstance(item, (dict, list)):
                    result.append(JsonHelper.process_nested_json(item))
                else:
                    result.append(item)
            return result

        else:
            return data

    @staticmethod
    def unify_json_response(response_data):
        """
        Utility function to ensure consistent JSON formatting in API responses.
        """
        if isinstance(response_data, str):
            return JsonHelper.normalize_json(response_data)
        else:
            return JsonHelper.process_nested_json(response_data)

    @staticmethod
    def debug_json_string(json_str):
        """
        Helper method to debug a problematic JSON string by showing characters around error position
        """
        try:
            json.loads(json_str)
            return {"status": "Valid JSON"}
        except json.JSONDecodeError as e:
            # Get the error position
            pos = e.pos

            # Calculate a window around the error
            start = max(0, pos - 20)
            end = min(len(json_str), pos + 20)

            # Extract the problematic section
            context = json_str[start:end]
            pointer = " " * (pos - start) + "^"  # Point to the exact error position

            return {
                "error": str(e),
                "position": pos,
                "line": e.lineno,
                "column": e.colno,
                "context": context,
                "pointer": pointer,
                "message": f"Error at position {pos}, line {e.lineno}, column {e.colno}"
            }


json_helper = JsonHelper()