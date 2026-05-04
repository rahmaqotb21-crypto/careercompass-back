import json
import re


def parse_learning_plan(raw_text):
    if raw_text is None:
        return None

    if isinstance(raw_text, dict):
        return raw_text if _is_valid_plan(raw_text) else None

    if isinstance(raw_text, (bytes, bytearray)):
        try:
            raw_text = raw_text.decode('utf-8', errors='ignore')
        except Exception:
            raw_text = str(raw_text)

    text = str(raw_text).strip()
    if not text:
        return None

    text = _strip_code_fences(text)
    json_candidate, _ = _extract_json_candidate(text)
    if not json_candidate:
        return None

    parsed = _try_parse_plan(_normalize_json(json_candidate))
    if parsed:
        return parsed

    fixed = _fix_message_inside_phases(json_candidate)
    if fixed != json_candidate:
        parsed = _try_parse_plan(_normalize_json(fixed))
        if parsed:
            return parsed

    relaxed = _quote_unquoted_keys(_normalize_single_quotes(_strip_json_comments(json_candidate)))
    relaxed = _fix_message_inside_phases(relaxed)
    relaxed = _append_missing_closers(relaxed)
    parsed = _try_parse_plan(_normalize_json(relaxed))
    if parsed:
        return parsed

    balanced = _append_missing_closers(json_candidate)
    parsed = _try_parse_plan(_normalize_json(balanced))
    return parsed


def _is_valid_plan(plan):
    return isinstance(plan, dict) and 'career_path' in plan and 'phases' in plan


def _try_parse_plan(value):
    try:
        parsed = json.loads(value)
    except Exception:
        return None

    return parsed if _is_valid_plan(parsed) else None


def _strip_code_fences(value):
    value = re.sub(r'^```(?:json)?\s*', '', value, flags=re.IGNORECASE)
    value = re.sub(r'\s*```$', '', value)
    return value.strip()


def _extract_json_candidate(value):
    start = value.find('{')
    if start == -1:
        return None, False

    in_string = False
    string_char = ''
    brace = 0
    bracket = 0
    found_start = False
    i = start

    while i < len(value):
        char = value[i]
        next_char = value[i + 1] if i + 1 < len(value) else ''

        if in_string:
            if char == '\\' and next_char:
                i += 2
                continue
            if char == string_char:
                in_string = False
                string_char = ''
            i += 1
            continue

        if char in ('"', "'"):
            in_string = True
            string_char = char
            i += 1
            continue

        if char == '{':
            brace += 1
            found_start = True
        elif char == '}':
            brace -= 1
        elif char == '[':
            bracket += 1
        elif char == ']':
            bracket -= 1

        if found_start and brace == 0 and bracket == 0:
            return value[start:i + 1], False

        i += 1

    last_brace = value.rfind('}')
    if last_brace > start:
        return value[start:last_brace + 1], True

    return value[start:], True


def _strip_json_comments(value):
    result = ''
    in_string = False
    string_char = ''
    in_line_comment = False
    in_block_comment = False
    i = 0

    while i < len(value):
        char = value[i]
        next_char = value[i + 1] if i + 1 < len(value) else ''

        if in_line_comment:
            if char == '\n':
                in_line_comment = False
                result += char
            i += 1
            continue

        if in_block_comment:
            if char == '*' and next_char == '/':
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue

        if in_string:
            if char == '\\' and next_char:
                result += char + next_char
                i += 2
                continue
            if char == string_char:
                result += '"'
                in_string = False
                string_char = ''
                i += 1
                continue
            if string_char == "'" and char == '"':
                result += '\\"'
                i += 1
                continue
            result += char
            i += 1
            continue

        if char == '/' and next_char == '/':
            in_line_comment = True
            i += 2
            continue

        if char == '/' and next_char == '*':
            in_block_comment = True
            i += 2
            continue

        if char in ('"', "'"):
            in_string = True
            string_char = char
            result += '"'
            i += 1
            continue

        result += char
        i += 1

    return result


def _normalize_single_quotes(value):
    result = ''
    in_string = False
    string_char = ''
    i = 0

    while i < len(value):
        char = value[i]
        next_char = value[i + 1] if i + 1 < len(value) else ''

        if in_string:
            if char == '\\' and next_char:
                result += char + next_char
                i += 2
                continue
            if char == string_char:
                result += '"'
                in_string = False
                string_char = ''
                i += 1
                continue
            if string_char == "'" and char == '"':
                result += '\\"'
                i += 1
                continue
            result += char
            i += 1
            continue

        if char in ('"', "'"):
            in_string = True
            string_char = char
            result += '"'
            i += 1
            continue

        result += char
        i += 1

    return result


def _quote_unquoted_keys(value):
    return re.sub(r'([,{]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*:)', r'\1"\2"\3', value)


def _find_matching_bracket(value, start_index):
    in_string = False
    string_char = ''
    depth = 0
    i = start_index

    while i < len(value):
        char = value[i]
        next_char = value[i + 1] if i + 1 < len(value) else ''

        if in_string:
            if char == '\\' and next_char:
                i += 2
                continue
            if char == string_char:
                in_string = False
                string_char = ''
            i += 1
            continue

        if char in ('"', "'"):
            in_string = True
            string_char = char
            i += 1
            continue

        if char == '[':
            depth += 1
        elif char == ']':
            depth -= 1
            if depth == 0:
                return i

        i += 1

    return -1


def _fix_message_inside_phases(value):
    phases_match = re.search(r'"phases"\s*:\s*\[', value)
    message_index = value.rfind('"message"')
    if not phases_match or message_index == -1 or message_index < phases_match.start():
        return value

    array_start = value.find('[', phases_match.start())
    if array_start == -1:
        return value

    closing_index = _find_matching_bracket(value, array_start)
    if closing_index != -1 and closing_index < message_index:
        return re.sub(r'(\])\s*"message"\s*:', r'\1, "message":', value)

    prefix = value[:message_index].rstrip()
    suffix = value[message_index:].lstrip()
    while prefix.endswith(','):
        prefix = prefix[:-1].rstrip()

    return f"{prefix}], {suffix}"


def _normalize_json(value):
    return re.sub(r',\s*([}\]])', r'\1', value)


def _append_missing_closers(value):
    brace = 0
    bracket = 0
    in_string = False
    string_char = ''
    i = 0

    while i < len(value):
        char = value[i]
        next_char = value[i + 1] if i + 1 < len(value) else ''

        if in_string:
            if char == '\\' and next_char:
                i += 2
                continue
            if char == string_char:
                in_string = False
                string_char = ''
            i += 1
            continue

        if char in ('"', "'"):
            in_string = True
            string_char = char
            i += 1
            continue

        if char == '{':
            brace += 1
        elif char == '}':
            brace -= 1
        elif char == '[':
            bracket += 1
        elif char == ']':
            bracket -= 1

        i += 1

    updated = value
    if bracket > 0:
        updated += ']' * bracket
    if brace > 0:
        updated += '}' * brace

    return updated
