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
        "all": "parse_command_all",
        "any": "parse_command_any",
        "in": "unexpected_command",
    }

    def __init__(self, game):
        """Initialize interpreter."""
        self.__game = game
        self.tokenizer = None
        self.__extra_parameters = None

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

    def __get_reference(self, identifier, **params):
        objname, *member = identifier.split(".")
        if objname == "self":
            objname = member[0]
            member = member[1:]

        obj = params.get("caller") or self.__game.get_object(objname)
        if not member:
            if objname != obj.name:
                return (obj, objname)
            return (obj, None)
        raise NotImplementedError("Member reference not implemented.")

    def execute(self, statement, **params):
        """Execute an action statement."""
        self.__extra_parameters = params.copy()

        with StringIO(statement) as stream:
            self.tokenizer = tokenize.generate_tokens(stream.readline)
            # identifier
            next_token = self.__next_token()
            token, identifier = self.parse_identifier(next_token)
            # assign expression
            token, assignment = self.__parse_assignment(token)
            if token[0] != tokenize.ENDMARKER:
                raise Exception("Invalid statement: `%s`" % statement)
            member_acs = self.__get_reference(identifier, **params)
            # if member_acs is None:
            #     raise Exception("Invalid reference: %s" % identifier)
            object_ref, member_name = member_acs
            if assignment:
                oper, value = assignment
                original = getattr(object_ref, member_name)
                setattr(
                    object_ref,
                    member_name,
                    GenesisIntepreter.assignment_ops[oper](original, value),
                )
            else:
                value = getattr(object_ref, member_name)(**params)
            self.tokenizer = None
            return value

    def __parse_assignment(self, next_token):
        """Parse an assignment operation."""
        token, oper, *_ = next_token
        result = None
        if token == tokenize.OP and oper in GenesisIntepreter.assignment_ops:
            next_token, value = self.__parse_expression(self.__next_token())
            result = (oper, value)
        return next_token, result

    def evaluate_expression(self, expression, **extra_parameters):
        """Evaluate an expression."""
        self.__extra_parameters = extra_parameters.copy()
        with StringIO(expression) as stream:
            self.tokenizer = tokenize.generate_tokens(stream.readline)
            token, value = self.__parse_expression(self.__next_token())
            if token[0] != tokenize.ENDMARKER:
                raise Exception("Invalid expression: `%s`" % expression)
            self.tokenizer = None
            return value

    def parse_identifier(self, next_token):
        """Retrieve a fully qualified identifier from the token stream."""
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

    def __perform_operation(self, data, value):  # pylint: disable=no-self-use
        if data is not None:
            operation, rhs = data
            value = GenesisIntepreter.operations[operation](value, rhs)
        return value

    def __parse_expression(self, next_token):
        next_token, value = self.__parse_term(next_token)
        next_token, data = self.__parse_expression_prime(next_token)
        value = self.__perform_operation(data, value)
        return next_token, value

    def __parse_expression_prime(self, next_token):
        token, oper, *_ = next_token
        if token == tokenize.OP and oper in ["+", "-"]:
            next_token, value = self.__parse_term(self.__next_token())
            next_token, data = self.__parse_expression_prime(next_token)
            value = self.__perform_operation(data, value)
            return next_token, (oper, value)

        return next_token, None

    def __parse_term(self, next_token):
        next_token, value = self.__parse_factor(next_token)
        next_token, data = self.__parse_term_prime(next_token)
        value = self.__perform_operation(data, value)
        return next_token, value

    def __parse_term_prime(self, next_token):
        token, oper, *_ = next_token
        if token == tokenize.OP and oper in ["*", "/", "//", "%", "^"]:
            next_token, value = self.__parse_factor(self.__next_token())
            next_token, data = self.__parse_term_prime(next_token)
            value = self.__perform_operation(data, value)
            return next_token, (oper, value)
        return next_token, None

    def __parse_factor(self, next_token):
        next_token, value = self.__parse_number(next_token)
        next_token, data = self.__parse_factor_prime(next_token)
        value = self.__perform_operation(data, value)
        return next_token, value

    def __parse_factor_prime(self, next_token):
        token, oper, *_ = next_token
        if token == tokenize.OP and oper in ["**"]:
            next_token, value = self.__parse_number(None)
            next_token, data = self.__parse_factor_prime(next_token)
            value = self.__perform_operation(data, value)
            return next_token, (oper, value)
        return next_token, None

    def __parse_number(self, next_token):
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
            next_token, value = self.__parse_number_from_name(next_token)
        else:
            raise Exception("Invalid element `%s`." % val)
        return next_token, value

    def __parse_number_from_name(self, next_token):
        # TODO: Currently only parsing properties, could also parse methods.
        next_token, qualified_id = self.parse_identifier(next_token)
        if qualified_id in GenesisIntepreter.commands:
            cmdname = GenesisIntepreter.commands[qualified_id]
            cmd = getattr(self, cmdname)
            next_token, value = cmd(next_token, __command__=qualified_id)
        else:
            obj, *parts = qualified_id.split(".")
            if obj not in self.__extra_parameters:
                value = self.__game.get_object_value(qualified_id)
            else:
                obj = self.__extra_parameters[obj]
                for part in parts:
                    if part not in obj:
                        msg = "Undefined identifier %s" % qualified_id
                        raise Exception(msg)
                    obj = obj[part]
                value = obj
        return next_token, value

    def __next_token(self):
        try:
            token = next(self.tokenizer)
            while token[0] == tokenize.NEWLINE:
                token = next(self.tokenizer)
            return token
        except Exception:  # pylint: disable=broad-except
            return None

    def __parse_object_property(self, next_token):
        """Parse an object property."""
        if next_token[0] == tokenize.NAME:
            next_token, identifier = self.parse_identifier(next_token)
            try:
                list_of_items = self.__game.get_object_value(identifier)
            except Exception:  # pylint: disable=broad-except
                data = self.__extra_parameters
                for part in identifier.split("."):
                    if part not in data:
                        raise Exception(
                            "Could not find value for `%s`" % identifier
                        )
                    data = data[part]
                list_of_items = data
        return next_token, list_of_items

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
        token_type, val, *_ = token
        if token_type != tokenize.NAME:
            raise Exception("Expected identifier. Got `%s`." % val)
        if expected and val != expected:
            raise Exception(
                "Expected identifier `%s, got `%s`." % (expected, val)
            )
        return val

    def unexpected_command(self, *_args, **params):
        # pylint: disable=no-self-use
        """Raise an exception due to unexpected command found."""
        raise Exception(
            "Unexpected command: `%s`" % params.get("__command__", "UNKNOWN")
        )

    def __parse_object_property_or_list(self, next_token):
        if next_token[0] == tokenize.NAME:
            next_token, items = self.__parse_object_property(next_token)
        else:
            next_token, items = self.__parse_list(next_token)
        return next_token, items

    def __parse_list_in_list(self, next_token):
        next_token, items = self.__parse_object_property_or_list(next_token)
        GenesisIntepreter.__assert_identifier(next_token, "in")
        next_token = self.__next_token()
        next_token, compare = self.__parse_object_property_or_list(next_token)
        return next_token, (items, compare)

    # ---- language commands

    def parse_command_all(self, next_token, **_):
        """Parse and evaluate command: `all <list> in <list>`."""
        next_token, (needle, search) = self.__parse_list_in_list(next_token)
        for value in needle:
            if value not in search:
                value = False
                break
        else:
            value = True
        return next_token, value

    def parse_command_any(self, next_token, **_):
        """Parse and evaluate command: `all <list> in <list>`."""
        next_token, (needle, search) = self.__parse_list_in_list(next_token)
        for value in needle:
            if value in search:
                value = True
                break
        else:
            value = False
        return next_token, value
