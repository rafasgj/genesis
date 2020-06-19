"""blah."""

import tokenize
from io import StringIO
import operator
import logging

log = logging.getLogger("genesis")


class GenesisIntepreter:
    """Genesis Game Design Engine language interpreter."""

    operations = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "**": operator.pow,
        "/": operator.truediv,
        "//": operator.floordiv,
        "%": operator.mod,
    }

    assignment_ops = {
        "=": lambda _, value: value,
        "+=": operator.iadd,
        "-=": operator.isub,
        "*=": operator.imul,
        "//=": operator.ifloordiv,
        "/=": operator.itruediv,
        "%=": operator.imod,
        "**=": operator.ipow,
    }

    commands = {
        "all": "_parse_command_all",
        "any": "_parse_command_any",
        "in": "_unexpected_command",
    }

    def __init__(self, game):
        """Initialize interpreter."""
        self.__game = game
        self.tokenizer = None
        self.__scope = None

    @staticmethod
    def as_number(value):
        """
        Return the value as a number.

        Raises a TypeError execption if value cannot be converted to a number.
        """
        number_as_int = int(value, 0)
        try:
            number_as_float = float(value, 0)
        except Exception:  # pylint: disable=broad-except.
            number_as_float = number_as_int

        if number_as_float == number_as_int:
            return number_as_int
        return number_as_float

    @staticmethod
    def is_number(value):
        """Test if the value can be converted to a number."""
        try:
            GenesisIntepreter.as_number(value)
        except ValueError:
            return False
        else:
            return True

    def execute(self, statement, **scope):
        """
        Parse and execute an action statement.

        Parameters:
            statement:
                The statement to be parsed.
            scope:
                Keyword arguments with the current scope variables.
                If `name` is present, than the scope is considered an object
                with that name.

        An `statement` has the grammar:
            statement: identifier [assignment_expression]

        If the statement is no an assignment, it is considered an expression.
        """
        self.__scope = scope.copy()
        with StringIO(statement) as stream:
            self.tokenizer = tokenize.generate_tokens(stream.readline)
            # identifier
            next_token = self.__next_token()
            next_token, identifier = self.__parse_identifier(next_token)
            # assign expression
            next_token, assignment = self.__parse_assignment(next_token)
            if next_token[0] != tokenize.ENDMARKER:
                raise Exception("Invalid statement: `%s`" % statement)
            if assignment:
                object_ref, member_name = self.__get_reference(identifier)
                oper, value = assignment
                original = getattr(object_ref, member_name)
                setattr(
                    object_ref,
                    member_name,
                    GenesisIntepreter.assignment_ops[oper](original, value),
                )
            else:
                value = self.__get_object_property(identifier)
            self.tokenizer = None
            return value

    def evaluate_expression(self, expression, **scope):
        """Evaluate an expression, with the statement parser."""
        self.__scope = scope.copy()
        with StringIO(expression) as stream:
            self.tokenizer = tokenize.generate_tokens(stream.readline)
            token, value = self.__parse_expression(self.__next_token())
            if token[0] != tokenize.ENDMARKER:
                raise Exception("Invalid expression: `%s`" % expression)
            self.tokenizer = None
            return value

    def __get_reference(self, identifier):
        """
        Retrieve a reference to an identifier.

        The reference might be used for both read and assignment.
        """
        objname, *member = identifier.split(".")
        if objname == "self":
            objname = member[0]
            member = member[1:]

        obj = self.__scope.get("caller")
        if obj is None:
            obj = self.__game.get_object(objname)
        if not member:
            if objname != obj.name:
                return (obj, objname)
            return (obj, None)

        error_msg = "Member reference not implemented: %s" % identifier
        raise NotImplementedError(error_msg)

    def __parse_assignment(self, next_token):
        """
        Parse an assignment expression.

        As with all parser functions, it receives the next_token and return
        a tuple (next_token, value). The value for an assignment expression
        is a tuple (assignment_operator, value).

        The grammar for the assignment expression is:
            assignment_expression: [assignment_operator expression]
        """
        token, oper, *_ = next_token
        result = None
        if token == tokenize.OP and oper in GenesisIntepreter.assignment_ops:
            next_token, value = self.__parse_expression(self.__next_token())
            result = (oper, value)
        return next_token, result

    def __parse_identifier(self, next_token):
        """
        Retrieve a fully qualified identifier from the token stream.

        The grammar is:
            qualified_identifier : identifier [. identifier]*
        """
        qualified_id = []
        while next_token[0] == tokenize.NAME:
            if next_token[1] in GenesisIntepreter.commands:
                if not qualified_id:  # it is a language command.
                    return self.__next_token(), next_token[1]
                # otherwise, it is an invalid name.
                msg = "Cannot use `%s` in object identifier." % next_token[1]
                raise Exception(msg)
            qualified_id.append(next_token[1])
            next_token = self.__next_token()
            if next_token[0] == tokenize.OP and next_token[1] == ".":
                next_token = self.__next_token()
        return next_token, ".".join(qualified_id)

    @staticmethod
    def __perform_operation(oper_rhs, lhs):
        """
        Ensure an operaton with the form `lhs operator rhs` is executed.

        `oper_rhs` is a tuple, containing an operator and the right hand side
        value. `lhs` is the left hand side value. If `oper_rhs` is None, `lhs`
        is returned as the result of the operation.
        """
        value = lhs
        if oper_rhs is not None:
            operation, rhs = oper_rhs
            value = GenesisIntepreter.operations[operation](lhs, rhs)
        return value

    def __parse_expression(self, next_token):
        """
        Parse an expression.

        Grammar:
            expression: term expression'
        """
        next_token, value = self.__parse_term(next_token)
        next_token, data = self.__parse_expression_prime(next_token)
        value = GenesisIntepreter.__perform_operation(data, value)
        return next_token, value

    def __parse_expression_prime(self, next_token):
        """
        Parse an expression'.

        Grammar:
            expression': ["+|-" term expression']
        """
        token, oper, *_ = next_token
        if token == tokenize.OP and oper in ["+", "-"]:
            next_token, value = self.__parse_term(self.__next_token())
            next_token, data = self.__parse_expression_prime(next_token)
            value = GenesisIntepreter.__perform_operation(data, value)
            return next_token, (oper, value)

        return next_token, None

    def __parse_term(self, next_token):
        """
        Parse a term.

        Grammar:
            term: factor term'
        """
        next_token, value = self.__parse_factor(next_token)
        next_token, data = self.__parse_term_prime(next_token)
        value = GenesisIntepreter.__perform_operation(data, value)
        return next_token, value

    def __parse_term_prime(self, next_token):
        """
        Parse a term'.

        Grammar:
            term': ["*|/|//|%" factor term']
        """
        token, oper, *_ = next_token
        if token == tokenize.OP and oper in ["*", "/", "//", "%"]:
            next_token, value = self.__parse_factor(self.__next_token())
            next_token, data = self.__parse_term_prime(next_token)
            value = GenesisIntepreter.__perform_operation(data, value)
            return next_token, (oper, value)
        return next_token, None

    def __parse_factor(self, next_token):
        """
        Parse a factor.

        Grammar:
            factor: number factor'
        """
        next_token, value = self.__parse_number(next_token)
        next_token, data = self.__parse_factor_prime(next_token)
        value = GenesisIntepreter.__perform_operation(data, value)
        return next_token, value

    def __parse_factor_prime(self, next_token):
        """
        Parse a factor'.

        Grammar:
            factor': ["**" number factor']
        """
        token, oper, *_ = next_token
        if token == tokenize.OP and oper in ["**"]:
            next_token, value = self.__parse_number(None)
            next_token, data = self.__parse_factor_prime(next_token)
            value = GenesisIntepreter.__perform_operation(data, value)
            return next_token, (oper, value)
        return next_token, None

    def __parse_number(self, next_token):
        """
        Parse a number.

        Grammar:
            number: literal_number | "(" expression ")" | identifier
        """
        token, val, *_ = next_token
        if token == tokenize.NUMBER:
            value = GenesisIntepreter.as_number(val)
            next_token = self.__next_token()
        elif token == tokenize.OP:
            if val == "(":
                next_token = self.__next_token()
                next_token, value = self.__parse_expression(next_token)
                token, val, *_ = next_token
                if token != tokenize.OP and val != ")":
                    raise Exception("Expected ')' got '%s'." % val)
                next_token = self.__next_token()
            else:
                raise Exception("Expected '(' got '%s'." % val)
        elif token == tokenize.NAME:
            next_token, value = self.__get_value_from_name(next_token)
        else:
            raise Exception("Invalid element `%s`." % val)
        return next_token, value

    def __get_value_from_name(self, next_token):
        """
        Return the value for a parsed fully qualified identifier.

        If the identifier parsed is a language command, return the result of
        its execution.
        """
        # TODO: Currently only parsing properties, could also parse methods.
        next_token, qualified_id = self.__parse_identifier(next_token)
        if qualified_id in GenesisIntepreter.commands:
            cmdname = GenesisIntepreter.commands[qualified_id]
            cmd = getattr(self, cmdname)
            next_token, value = cmd(next_token, __command__=qualified_id)
        else:
            value = self.__get_object_property(qualified_id)
        return next_token, value

    def __next_token(self):
        """Retrieve the next token."""
        try:
            token = next(self.tokenizer)
            while token[0] == tokenize.NEWLINE:
                token = next(self.tokenizer)
            return token
        except Exception:  # pylint: disable=broad-except
            return None

    def __get_object_property(self, identifier):
        """Retrieve the value of an object property."""
        value = None
        try:
            value = self.__game.get_object_value(identifier)
        except Exception:  # pylint: disable=broad-except
            try:
                object_ref, member_name = self.__get_reference(identifier)
                if self.__scope.get("name") == object_ref:
                    value = self.__scope.get(member_name)
                elif hasattr(object_ref, member_name):
                    value = getattr(object_ref, member_name)(**self.__scope)
                elif hasattr(self.__game, member_name):
                    value = getattr(self.__game, member_name)(**self.__scope)
                else:
                    value = self.__get_value_from_local_scope(identifier)
            except Exception:  # pylint: disable=broad-except
                value = self.__get_value_from_local_scope(identifier)
        return value

    def __get_value_from_local_scope(self, identifier):
        """Retrieve value for a fully qualified name from local scope."""
        data = self.__scope.copy()
        parts = identifier.split(".")
        if self.__scope.get("name") == parts[0]:
            parts = parts[1:]
        for part in parts:
            if part not in data:
                raise Exception("Could not find value for `%s`" % identifier)
            data = data[part]
        return data

    def __parse_list(self, next_token):
        """Parse a list of itens. ("(items...)" or "[items...]")."""
        if next_token[0] == tokenize.OP and next_token[1] in ("(", "["):
            close_list = ")" if next_token[1] == "(" else "]"
            #
            list_of_items = []
            next_token = self.__next_token()
            while next_token[0] == tokenize.NAME:
                list_of_items.append(next_token[1])
                next_token = self.__next_token()
                if next_token[0] == tokenize.OP:
                    if next_token[1] == ",":
                        next_token = self.__next_token()
                    elif next_token[1] == close_list:
                        break
                    else:
                        raise Exception(
                            "Invalid list separator: '%s'." % next_token[1]
                        )

            if next_token[0] != tokenize.OP and next_token[1] != close_list:
                msg = "Expected `%s`, got `%s`." % (close_list, next_token[1])
                raise Exception(msg)
            next_token = self.__next_token()
        else:
            msg = "Expected `list of items`, found `%s`" % next_token[1]
            raise Exception(msg)

        return next_token, list_of_items

    @staticmethod
    def __assert_identifier(token, expected=None):
        """Assert that an identifier parsed has the expected value."""
        token_type, val, *_ = token
        if token_type != tokenize.NAME:
            raise Exception("Expected identifier. Got `%s`." % val)
        if expected and val != expected:
            raise Exception(
                "Expected identifier `%s, got `%s`." % (expected, val)
            )
        return val

    def __parse_object_property_or_list(self, next_token):
        """
        Parse a list of values.

        grammar:
            list_of_values: "(" item [, item]* ")" | identifier
        """
        if next_token[0] == tokenize.NAME:
            next_token, identifier = self.__parse_identifier(next_token)
            items = self.__get_object_property(identifier)
        else:
            next_token, items = self.__parse_list(next_token)
        return next_token, items

    def __parse_list_in_list(self, next_token):
        """
        Parse the `in` part of commands.

        grammar:
            list_in_list: list_of_values "in" list_of_values
        """
        next_token, items = self.__parse_object_property_or_list(next_token)
        GenesisIntepreter.__assert_identifier(next_token, "in")
        next_token = self.__next_token()
        next_token, compare = self.__parse_object_property_or_list(next_token)
        return next_token, (items, compare)

    # ---- language commands

    def _parse_command_all(self, next_token, **_):
        """Parse and evaluate command: `all <list> in <list>`."""
        next_token, (needle, search) = self.__parse_list_in_list(next_token)
        for value in needle:
            if value not in search:
                value = False
                break
        else:
            value = True
        return next_token, value

    def _parse_command_any(self, next_token, **_):
        """Parse and evaluate command: `all <list> in <list>`."""
        next_token, (needle, search) = self.__parse_list_in_list(next_token)
        for value in needle:
            if value in search:
                value = True
                break
        else:
            value = False
        return next_token, value

    def _unexpected_command(self, *_args, **params):
        """Raise an exception due to unexpected command found."""
        # pylint: disable=no-self-use
        raise Exception(
            "Unexpected command: `%s`" % params.get("__command__", "UNKNOWN")
        )
