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
    print(token_lst)
    return token_lst
