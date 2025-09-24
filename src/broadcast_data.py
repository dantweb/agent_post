# python
import json
import re
from collections import UserDict, deque
from typing import Any
import base64
from io import BytesIO
from PIL import Image


class BroadcastData(UserDict):
    def __init__(self, obj_input=None):
        super().__init__()
        self.properties = []
        self.image = None

        if obj_input is None:
            self.data = None
            return

        # Process input data without flattening
        processed_data = self._process_input(obj_input)

        if isinstance(processed_data, dict):
            self.data = processed_data
            self.properties = [type(v).__name__ for v in processed_data.values() if not isinstance(v, (dict, list))]
        elif isinstance(processed_data, list):
            self.data = processed_data
            self.properties = []
            for item in processed_data:
                if isinstance(item, dict):
                    self.properties.extend([type(v).__name__ for v in item.values() if not isinstance(v, (dict, list))])
                elif isinstance(item, Image.Image):
                    self.image = item
                    self.properties.append("Image")
                else:
                    self.properties.append(type(item).__name__)
        elif isinstance(processed_data, Image.Image):
            self.image = processed_data
            self.data = {}
            self.properties.append("Image")
        else:
            self.data = {}
            self.properties.append(type(processed_data).__name__)

    def _process_input(self, data, depth=0, max_depth=100):
        if depth > max_depth:
            return data

        if isinstance(data, BroadcastData):
            return self._process_input(data.data, depth + 1, max_depth)

        if isinstance(data, str):
            parsed = self._try_parse_json(data)
            if parsed is not None:
                return self._process_input(parsed, depth + 1, max_depth)
            return data

        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                result[key] = self._process_input(value, depth + 1, max_depth)
            return result

        if isinstance(data, list):
            return [self._process_input(item, depth + 1, max_depth) for item in data]

        if isinstance(data, Image.Image):
            self.image = data
            return data

        return data

    def _try_parse_json(self, text: str):
        if not isinstance(text, str):
            return None
        text = text.strip()
        if not self._looks_like_json(text):
            return None

        # Try parsing with original quotes
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try normalizing single quotes to double quotes
        normalized = re.sub(r"(?<!\\)'", '"', text)
        try:
            return json.loads(normalized)
        except json.JSONDecodeError:
            pass

        # Handle escaped quotes
        normalized = re.sub(r"\\(['\"])", r'\1', normalized)  # Remove escaping for quotes
        normalized = normalized.replace("True", "true").replace("False", "false").replace("None", "null")
        normalized = re.sub(r'(\w+):', r'"\1":', normalized)  # Quote unquoted keys
        normalized = re.sub(r',\s*}', '}', normalized)  # Remove trailing commas
        normalized = re.sub(r',\s*]', ']', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)

        try:
            return json.loads(normalized)
        except json.JSONDecodeError:
            return None

    def _looks_like_json(self, text: str) -> bool:
        if not isinstance(text, str):
            return False
        text = text.strip()
        return (text.startswith('{') and text.endswith('}')) or \
            (text.startswith('[') and text.endswith(']'))

    def has(self, key):
        if isinstance(self.data, dict):
            return key in self.data
        elif isinstance(self.data, list):
            return any(isinstance(item, dict) and key in item for item in self.data)
        else:
            return False

    def set(self, key, value):
        if not isinstance(self.data, dict):
            self.data = {}
        self.data[key] = value
        if type(value).__name__ not in self.properties:
            self.properties.append(type(value).__name__)

    def get(self, key, default=None):
        if isinstance(self.data, dict):
            return self.data.get(key, default)
        elif isinstance(self.data, list):
            values = [item[key] for item in self.data if isinstance(item, dict) and key in item]
            return values if values else default
        else:
            return default

    def to_json(self) -> str:
        try:
            return json.dumps(self.to_serializable(), ensure_ascii=False)
        except (TypeError, OverflowError) as e:
            raise ValueError(f"Data contains non-serializable values: {e}")

    def to_serializable(self):
        import datetime
        import decimal
        import uuid

        if isinstance(self.data, (dict, list)):
            return self._process_serializable(self.data)
        elif isinstance(self.data, Image.Image):
            return self.convert_to_base64(self.data)
        elif isinstance(self.data, datetime.datetime):
            return self.data.isoformat()
        elif isinstance(self.data, datetime.date):
            return self.data.isoformat()
        elif isinstance(self.data, datetime.time):
            return self.data.isoformat()
        elif isinstance(self.data, decimal.Decimal):
            return float(self.data)
        elif isinstance(self.data, uuid.UUID):
            return str(self.data)
        elif isinstance(self.data, bytes):
            return base64.b64encode(self.data).decode('utf-8')
        elif isinstance(self.data, set):
            return list(self.data)
        elif hasattr(self.data, '__dict__'):
            # Handle custom objects with attributes
            return {key: self._serialize_value(value) for key, value in self.data.__dict__.items()}
        return self.data

    def _process_serializable(self, data):
        """Process data recursively to handle non-serializable types"""
        if isinstance(data, dict):
            return {key: self._serialize_value(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._serialize_value(item) for item in data]
        else:
            return self._serialize_value(data)

    def _serialize_value(self, value):
        """Convert individual values to serializable types"""
        import datetime
        import decimal
        import uuid

        if isinstance(value, datetime.datetime):
            return value.isoformat()
        elif isinstance(value, datetime.date):
            return value.isoformat()
        elif isinstance(value, datetime.time):
            return value.isoformat()
        elif isinstance(value, decimal.Decimal):
            return float(value)
        elif isinstance(value, uuid.UUID):
            return str(value)
        elif isinstance(value, bytes):
            return base64.b64encode(value).decode('utf-8')
        elif isinstance(value, set):
            return list(value)
        elif isinstance(value, Image.Image):
            return self.convert_to_base64(value)
        elif isinstance(value, (dict, list)):
            return self._process_serializable(value)
        elif hasattr(value, '__dict__'):
            # Handle custom objects with attributes
            return {key: self._serialize_value(val) for key, val in value.__dict__.items()}
        else:
            return value

    def flatten_data(self):
        flat_dict = {}
        stack = deque([(self.data, "")])
        visited = set()

        while stack:
            obj, parent_key = stack.pop()
            obj_id = id(obj)

            if obj_id in visited:
                continue
            visited.add(obj_id)

            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{parent_key}_{key}" if parent_key else key
                    if new_key in flat_dict:
                        new_key = self.get_unique_key(new_key, flat_dict)
                    stack.append((value, new_key))
            elif isinstance(obj, list):
                for index, item in enumerate(obj):
                    new_key = f"{parent_key}_{index}" if parent_key else str(index)
                    if new_key in flat_dict:
                        new_key = self.get_unique_key(new_key, flat_dict)
                    stack.append((item, new_key))
            else:
                flat_dict[parent_key] = obj

        return flat_dict

    def get_unique_key(self, base_key, existing_keys):
        index = 1
        new_key = f"{base_key}_{index}"
        while new_key in existing_keys:
            index += 1
            new_key = f"{base_key}_{index}"
        return new_key

    def __json__(self):
        return self.to_serializable()

    def get_by_path(self, path: str):
        if not path:
            return self.data

        keys = path.split('/')
        stack = deque([(self.data, keys)])
        results = []

        while stack:
            current, remaining_keys = stack.pop()

            if not remaining_keys:
                results.append(current)
                continue

            key = remaining_keys[0]

            if isinstance(current, dict):
                if key in current:
                    stack.append((current[key], remaining_keys[1:]))
            elif isinstance(current, list):
                for item in current:
                    stack.append((item, remaining_keys))

        return results[0] if len(results) == 1 else results if results else None

    def find_value_recursive_by_key(self, field):
        if isinstance(field, str) and '/' in field:
            res = self.get_by_path(field)
            if res is None:
                return []
            return [res] if not isinstance(res, list) else res

        matches = []
        stack = deque([(self.data, False)])
        visited = set()

        while stack:
            data, parsed = stack.pop()
            obj_id = id(data)

            if obj_id in visited:
                continue
            visited.add(obj_id)

            if isinstance(data, dict):
                for k, v in data.items():
                    if k == field:
                        matches.append(v)
                    if isinstance(v, (dict, list)):
                        stack.append((v, False))
                    elif isinstance(v, str) and not parsed:
                        parsed_v = self._try_parse_json(v)
                        if parsed_v is not None:
                            stack.append((parsed_v, True))
            elif isinstance(data, list):
                for item in data:
                    stack.append((item, False))

        return matches

    def convert_to_base64(self, input_obj: Any) -> str:
        if isinstance(input_obj, Image.Image):
            buffered = BytesIO()
            input_obj.save(buffered, format="PNG")
            encoded_bytes = base64.b64encode(buffered.getvalue())
            return encoded_bytes.decode('utf-8')
        elif isinstance(input_obj, str):
            return base64.b64encode(input_obj.encode('utf-8')).decode('utf-8')
        else:
            raise TypeError(f"Unsupported type for base64 conversion: {type(input_obj)}")