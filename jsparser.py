def _is_valid_string_rep(s):
    if s[0] != "\"" or s[-1] != "\"":
        return False
    for i in range(1, len(s) - 1):
        if s[i] == "\"" and s[i - 1] != "\\":
            return False
    return True

def _convert_to_number(n):
    try:
        return int(n)
    except ValueError:
        try:
            return float(n)
        except ValueError:
            return complex(n)

def _is_convertible_to_number(s):
    try:
        complex(s)
        return True
    except ValueError:
        return False

def _parse_obj(tokens):
    obj = None
    if tokens[0] == "[":
        obj = []
    elif tokens[0] == "{":
        obj = {}
    else:
        raise SyntaxError("Unexpected token {tokens[0]}")

    stack = []
    seen_value = False
    seen_key = isinstance(obj, list)
    key = None
    i = 1
    while i < len(tokens) - 1:
        if tokens[i] == "[":
            if not seen_key or seen_value or (isinstance(obj, dict) and tokens[i - 1] != ":"):
                raise SyntaxError(f"Unexpected token {tokens[i - 1]} before {tokens[i]}")
            stack.append(("]", i))
            curr = i
            while tokens[i] != "]" and stack[-1] != curr:
                if i == len(tokens) - 1:
                    raise SyntaxError("[ was never closed")
                if tokens[i] == "{":
                    stack.append(("}", i))
                elif tokens[i] == "[":
                    stack.append(("]", i))
                elif tokens[i] == "}":
                    if stack.pop()[0] != "}":
                        raise SyntaxError("{ was never closed")
                elif tokens[i] == "]":
                    if stack.pop()[0] != "]":
                        raise SyntaxError("[ was never closed")
                i += 1
            stack.pop()
            value = _parse_obj(tokens[curr: i + 1])
            if isinstance(obj, list):
                if seen_value:
                    raise SyntaxError(f"Unexpected token {tokens[i]} after {tokens[i - 1]}")
                seen_value = True
                obj.append(value)
            else:
                if (not seen_key) or (seen_value):
                    raise SyntaxError(f"Unexpected token {tokens[i]} after {tokens[i - 1]}")
                seen_value = True
                obj[key] = value

        elif tokens[i] == "{":
            if not seen_key or seen_value or (isinstance(obj, dict) and tokens[i - 1] != ":"):
                raise SyntaxError(f"Unexpected token {tokens[i - 1]} before {tokens[i]}")
            stack.append(("}", i))
            curr = i
            while tokens[i] != "}" and stack[-1] != curr:
                if i == len(tokens) - 2:
                    raise SyntaxError("{ was never closed")
                if tokens[i] == "{":
                    stack.append(("}", i))
                elif tokens[i] == "[":
                    stack.append(("]", i))
                elif tokens[i] == "}":
                    if stack.pop()[0] != "}":
                        raise SyntaxError("{ was never closed")
                elif tokens[i] == "]":
                    if stack.pop()[0] != "]":
                        raise SyntaxError("[ was never closed")
                i += 1
            stack.pop()
            value = _parse_obj(tokens[curr: i + 1])
            if isinstance(obj, list):
                if seen_value:
                    raise SyntaxError(f"Unexpected token {tokens[i]} after {tokens[i - 1]}")
                seen_value = True
                obj.append(value)
            else:
                if (not seen_key) or (seen_value):
                    raise SyntaxError(f"Unexpected token {tokens[i]} after {tokens[i - 1]}")
                seen_value = True
                obj[key] = value

        elif tokens[i] == ",":
            if i + 2 == len(tokens):
                raise SyntaxError(f"Encountered trailing comma")
            elif (not seen_key) or (not seen_value):
                raise SyntaxError(f"Unexpected token {tokens[i]} after {tokens[i - 1]}")
            seen_value = False
            if isinstance(obj, dict):
                seen_key = False
        
        elif tokens[i] == ":":
            if isinstance(obj, list) or not seen_key:
                raise SyntaxError(f"Unexpected token {tokens[i]}")
        
        elif tokens[i] == "true" or tokens[i] == "false" or tokens[i] == "null" or _is_convertible_to_number(tokens[i]):
            if (not seen_key) or (seen_value) or (isinstance(obj, dict) and tokens[i - 1] != ":"):
                raise SyntaxError(f"Unexpected token {tokens[i]} after {tokens[i - 1]}")
            seen_value = True
            
            value = None
            if tokens[i] == "true":
                value = True
            elif tokens[i] == "false":
                value = False
            elif tokens[i] == "null":
                pass
            else:
                value = _convert_to_number(tokens[i])

            if isinstance(obj, dict):
                obj[key] = value
                key = None
            else:
                obj.append(value)
        
        elif tokens[i][0] == "\"":
            if _is_valid_string_rep(tokens[i]):
                if isinstance(obj, list):
                    if not seen_value:
                        obj.append(tokens[i][1:-1])
                    else:
                        raise SyntaxError(f"Unexpected token {tokens[i]}")
                else:
                    if not seen_key and not seen_value:
                        key = tokens[i][1:-1]
                        seen_key = True
                    elif seen_key and not seen_value:
                        obj[key] = tokens[i][1:-1]
                        key = None
                        seen_value = True
                    else:
                        raise SyntaxError(f"Unexpected token {tokens[i]} after {tokens[i - 1]}")
            else:
                raise SyntaxError(f"Invalid syntax {tokens[i]}")
        
        else:
            raise SyntaxError(f"Invalid token {tokens[i]} after {tokens[i - 1]}")
        i += 1
    print(f"obj: {obj}")
    return obj

def parse(tokens):
    dic = {"data": None}
    if len(tokens) == 0:
        return dic
    if not (tokens[0] == "[" and tokens[-1] == "]") and not (tokens[0] == "{" and tokens[-1] == "}"):
        raise SyntaxError("Invalid JSON syntax")
    dic["data"] = _parse_obj(tokens)
    return dic

def _tokenize(s):
    """
    Returns a list of tokens from a give string
    """
    symbols = "{}[],:"
    token_lst = []
    curr_tkn = ""
    for c in s:
        if c in symbols:
            if len(curr_tkn) > 0:
                token_lst.append(curr_tkn)
                curr_tkn = ""
            token_lst.append(c)
        elif c.isspace():
            if len(curr_tkn) > 0:
                token_lst.append(curr_tkn)
                curr_tkn = ""
        else:
            curr_tkn += c
    return token_lst
