from Sexpr import Sexpr, find_close_paren


def _read_clean_text(path):
    """Read file and remove '#' comments and blank lines."""
    pieces = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if "#" in line:
                line = line[: line.find("#")]
            line = line.strip()
            if line:
                pieces.append(line)
    return " ".join(pieces)


def _parse_top_level_expressions(text):
    """Split one big string into top-level parenthesized S-expressions."""
    exprs = []
    i = 0
    n = len(text)
    while i < n:
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break
        if text[i] != "(":
            raise ValueError("Expected '(' at top level while parsing PDDL text.")
        j = i + find_close_paren(text[i:])
        expr_text = text[i : j + 1]
        exprs.append(Sexpr(expr_text))
        i = j + 1
    return exprs


def _sexpr_to_literal(expr):
    """
    Convert a literal S-expression to tuple form.
    Examples:
        (on A B) -> ("on", "A", "B")
        (hand-empty) -> ("hand-empty",)
        (not (hand-empty)) -> ("hand-empty",)  with neg flag returned separately
        (not hand-empty) -> ("hand-empty",)    with neg flag returned separately
    """
    if expr.atom is not None:
        return (expr.atom,), False

    if not expr.list:
        raise ValueError("Empty expression cannot be converted to a literal.")

    head = expr.list[0].atom
    if head == "not":
        inner = expr.list[1]
        if inner.atom is not None:
            return (inner.atom,), True
        return tuple(item.atom for item in inner.list), True

    return tuple(item.atom for item in expr.list), False


def _get_key_value_pairs(action_expr):
    """
    Parse action fields and support both styles:
        (:parameters (...))
        :parameters (...)
    Also supports :precondition/:preconditions and :effect/:effects.
    """
    pairs = {}
    items = action_expr.list
    i = 2  # skip :action and action name
    while i < len(items):
        item = items[i]

        if item.atom is not None and item.atom.startswith(":"):
            key = item.atom.lower()
            value = items[i + 1] if i + 1 < len(items) else Sexpr("()")
            pairs[key] = value
            i += 2
            continue

        if item.list and item.list[0].atom is not None and item.list[0].atom.startswith(":"):
            key = item.list[0].atom.lower()
            value = item.list[1] if len(item.list) > 1 else Sexpr("()")
            pairs[key] = value
            i += 1
            continue

        i += 1

    return pairs


def _flatten_conjunction(expr):
    """Return list of literals from either (and ...) or a single literal."""
    if expr.atom is not None:
        return [expr]
    if expr.list and expr.list[0].atom == "and":
        return expr.list[1:]
    return [expr]


def parse_blocksworld_actions(path):
    """
    Parse Blocksworld operators from PDDL-like file.

    Returns list of dictionaries with fields:
        name, parameters, preconditions, add_effects, delete_effects
    """
    text = _read_clean_text(path)
    top_level = _parse_top_level_expressions(text)
    actions = []

    for expr in top_level:
        if not expr.list or expr.list[0].atom != ":action":
            continue

        action_name = expr.list[1].atom
        fields = _get_key_value_pairs(expr)

        params_expr = fields.get(":parameters", Sexpr("()"))
        pre_expr = fields.get(":precondition", fields.get(":preconditions", Sexpr("()")))
        eff_expr = fields.get(":effect", fields.get(":effects", Sexpr("()")))

        parameters = []
        if params_expr.atom is None:
            for p in params_expr.list:
                if p.atom is not None:
                    parameters.append(p.atom)

        preconditions = set()
        for lit_expr in _flatten_conjunction(pre_expr):
            lit, is_negative = _sexpr_to_literal(lit_expr)
            if not is_negative:
                preconditions.add(lit)

        add_effects = set()
        delete_effects = set()
        for lit_expr in _flatten_conjunction(eff_expr):
            lit, is_negative = _sexpr_to_literal(lit_expr)
            if is_negative:
                delete_effects.add(lit)
            else:
                add_effects.add(lit)

        actions.append(
            {
                "name": action_name,
                "parameters": parameters,
                "preconditions": preconditions,
                "add_effects": add_effects,
                "delete_effects": delete_effects,
            }
        )

    return actions
