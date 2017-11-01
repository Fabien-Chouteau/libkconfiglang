from langkit.compiled_types import ASTNode, abstract, root_grammar_class, \
     Field, EnumType
from langkit.parsers import Grammar, Row, List, Or, Tok, Opt, Enum
from lexer import Token

@abstract
@root_grammar_class()
class KConfigNode(ASTNode):
    """
    Root node class for KConfig AST nodes.
    """
    pass

class RootNode(KConfigNode):
    main = Field()
    lst  = Field()

class Config(KConfigNode):
    symbol = Field()
    options = Field()

class MenuConfig(KConfigNode):
    symbol = Field()
    options = Field()

class Choice(KConfigNode):
    options = Field()
    configs = Field()

class Menu(KConfigNode):
    text = Field()
    child = Field()

class MainMenu(KConfigNode):
    Title = Field()

class Select(KConfigNode):
    symbol = Field()

class If(KConfigNode):
    expr  = Field()
    child = Field()

class Source(KConfigNode):
    filename = Field()

class TristateLiteral(KConfigNode):
    value = Field()

class BoolLiteral(KConfigNode):
    value = Field()

class IntLiteral(KConfigNode):
    value = Field()

class HexLiteral(KConfigNode):
    value = Field()

class StringLiteral(KConfigNode):
    value = Field()

class Identifier(KConfigNode):
    ident = Field()

@abstract
class Property(KConfigNode):
    pass

class Type(Property):
    type_id = Field()
    prompt_str = Field()

class Help(Property):
    # text = Field()
    pass

class Default(Property):
    value = Field()

class Depends(Property):
    identifier = Field()

class Prompt(Property):
    prompt_str = Field()

@abstract
class Expression(KConfigNode):
    pass

class NotExpr(Expression):
    A = Field()

class Operator(EnumType):
    alternatives = ['equal_op', 'diff_op', 'and_op', 'or_op']

class BinaryExpr(Expression):
    lhs = Field()
    op = Field()
    rhs = Field()

kconfig_grammar = Grammar('main_rule')

G = kconfig_grammar

kconfig_grammar.add_rules(

    # Main rule
    main_rule=Row(Opt(G.mainmenu_rule), G.root_rule) ^ RootNode,

    # Root rule
    root_rule=List(Or(G.config_rule,
                      G.menuconfig_rule,
                      G.source_rule,
                      G.menu_rule,
                      G.if_rule,
                      G.choice_rule),
                   empty_valid=True),

    # Config
    config_rule=Row('config', G.identifier, G.config_options) ^ Config,

    config_options=List(Or(G.type_exp,
                           G.prompt_exp,
                           G.default_exp,
                           G.depends_exp,
                           G.select_exp,
                           G.help_exp)),

    config_list=List(G.config_rule),

    # Menuconfig
    menuconfig_rule=Row('menuconfig', G.identifier, G.menuconfig_options) ^ MenuConfig,

    menuconfig_options=List(Or(G.type_exp,
                               G.prompt_exp,
                               G.default_exp,
                               G.depends_exp,
                               G.select_exp,
                               G.help_exp)),

    # Menu
    menu_rule=Row('menu', G.string_literal, G.root_rule, 'endmenu') ^ Menu,

    # If
    if_rule=Row('if', G.expr, G.root_rule, 'endif') ^ If,

    # Choice
    choice_rule=Row('choice', G.choice_options, G.config_list, 'endchoice') ^ Choice,
    choice_options=List(Or(G.depends_exp)),

    # Symbol
    identifier=Tok(Token.Identifier, keep=True) ^ Identifier,

    # Mainmenu
    mainmenu_rule=Row('mainmenu', G.string_literal) ^ MainMenu,

    # Literals
    tristate_literal=Or(Tok(Token.Yes, keep=True),
                        Tok(Token.No, keep=True),
                        Tok(Token.Module, keep=True)) ^ TristateLiteral,

    bool_literal=Or(Tok(Token.Yes, keep=True),
                   Tok(Token.No, keep=True)) ^ BoolLiteral,

    int_literal=Tok(Token.Number, keep=True) ^ IntLiteral,

    hex_literal=Tok(Token.HexNumber, keep=True) ^ HexLiteral,

    string_literal=Tok(Token.String, keep=True) ^ StringLiteral,

    value_exp=Or(G.tristate_literal,
                 G.bool_literal,
                 G.int_literal,
                 G.hex_literal,
                 G.string_literal),

    # Options

    # TODO: How to grap the text between help and the empty line
    help_exp=Row('help', Tok(Token.EmptyLine)) ^ Help,

    type_exp=Row(Or(Tok(Token.Tristate,   keep=True),
                    Tok(Token.Bool,       keep=True),
                    Tok(Token.Int,        keep=True),
                    Tok(Token.Hex,        keep=True),
                    Tok(Token.StringType, keep=True)
                    ),
                 Opt (G.string_literal)) ^ Type,

    prompt_exp=Row('prompt', G.string_literal) ^ Prompt,

    default_exp=Row('default', G.value_exp) ^ Default,

    select_exp=Row('select', G.identifier) ^ Select,

    depends_exp=Row('depends', 'on', G.expr) ^ Depends,

    source_rule=Row('source', G.string_literal) ^ Source,

    # Expressions

    expr=Or(Row('(', G.expr, ')')[1],
            Row(G.expr,
                Or(Enum('=', Operator('equal_op')),
                   Enum('!=', Operator('diff_op')),
                   Enum('&&', Operator('and_op')),
                   Enum('||', Operator('or_op'))),
                G.expr
                ) ^ BinaryExpr,
            G.identifier,
            G.bool_literal,
            G.tristate_literal,
            Row('!', G.expr) ^ NotExpr,
            ),
)
