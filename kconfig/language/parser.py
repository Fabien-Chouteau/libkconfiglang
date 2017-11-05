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
    text    = Field()
    visible = Field()
    child   = Field()

class MainMenu(KConfigNode):
    Title = Field()

class Select(KConfigNode):
    symbol    = Field()
    condition = Field()

class Imply(KConfigNode):
    symbol    = Field()
    condition = Field()

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

class Comment(KConfigNode):
    string = Field()

class Visible(KConfigNode):
    condition = Field()

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
    value     = Field()
    condition = Field()

class DefaultChoice(Property):
    value     = Field()
    condition = Field()

class DefBool(Property):
    value     = Field()
    condition = Field()

class DefTristate(Property):
    value     = Field()
    condition = Field()

class Depends(Property):
    identifier = Field()

class Prompt(Property):
    prompt_str = Field()
    condition  = Field()

class Range(Property):
    low       = Field()
    high      = Field()
    condition = Field()

class Option(Property):
    opt_name = Field()
    value    = Field()

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
    main_rule=Row(Opt(G.mainmenu), G.block) ^ RootNode,

    # Block rule
    block=List(Or(G.config,
                  G.menuconfig,
                  G.source,
                  G.menu,
                  G.comment,
                  G.if_rule,
                  G.choice),
               empty_valid=True),

    # Config
    config=Row('config', G.identifier, G.config_options) ^ Config,

    config_options=List(Or(G.type,
                           G.prompt,
                           G.default,
                           G.depends,
                           G.select,
                           G.imply,
                           G.help,
                           G.range,
                           G.comment,
                           G.def_bool,
                           G.def_tristate,
                           G.option)),

    config_list=List(G.config, empty_valid=True),

    # Menuconfig
    menuconfig=Row('menuconfig', G.identifier, G.menuconfig_options) ^ MenuConfig,

    menuconfig_options=List(Or(G.type,
                               G.prompt,
                               G.default,
                               G.depends,
                               G.select,
                               G.imply,
                               G.help,
                               G.range,
                               G.comment,
                               G.def_bool,
                               G.def_tristate,
                               G.option)),

    # Menu
    menu=Row('menu', G.string_literal, Opt (G.visible), G.block, 'endmenu') ^ Menu,

    # If
    if_rule=Row('if', G.expr, G.block, 'endif') ^ If,

    # Choice
    choice=Row('choice', G.choice_options, G.config_list, 'endchoice') ^ Choice,
    choice_options=List(Or(G.depends,
                           G.prompt,
                           G.default_choice)),

    default_choice=Row('default', G.identifier, G.opt_condition) ^ DefaultChoice,

    # Symbol
    identifier=Tok(Token.Identifier, keep=True) ^ Identifier,

    # Mainmenu
    mainmenu=Row('mainmenu', G.string_literal) ^ MainMenu,

    # Optional condition
    opt_condition=Opt('if', G.expr),

    # Literals
    tristate_literal=Or(Tok(Token.Yes, keep=True),
                        Tok(Token.No, keep=True),
                        Tok(Token.Module, keep=True)) ^ TristateLiteral,

    bool_literal=Or(Tok(Token.Yes, keep=True),
                    Tok(Token.No, keep=True)) ^ BoolLiteral,

    int_literal=Tok(Token.Number, keep=True) ^ IntLiteral,

    hex_literal=Tok(Token.HexNumber, keep=True) ^ HexLiteral,

    string_literal=Tok(Token.String, keep=True) ^ StringLiteral,

    value=Or(G.tristate_literal,
             G.bool_literal,
             G.int_literal,
             G.hex_literal,
             G.string_literal),

    # Options

    # TODO: How to grab the text between help and the empty line
    help=Row('help', Tok(Token.EmptyLine)) ^ Help,

    type=Row(Or(Tok(Token.Tristate,   keep=True),
                Tok(Token.Bool,       keep=True),
                Tok(Token.Int,        keep=True),
                Tok(Token.Hex,        keep=True),
                Tok(Token.StringType, keep=True)
                ),
             Opt (G.string_literal)) ^ Type,

    prompt=Row('prompt', G.string_literal, G.opt_condition) ^ Prompt,

    default=Row('default', G.value, G.opt_condition) ^ Default,

    def_bool=Row('def_bool', G.bool_literal, G.opt_condition) ^ DefBool,

    def_tristate=Row('def_tristate', G.tristate_literal, G.opt_condition) ^ DefTristate,

    select=Row('select', G.identifier, G.opt_condition) ^ Select,

    imply=Row('imply', G.identifier, G.opt_condition) ^ Imply,

    visible=Row('visible', 'if', G.expr) ^ Visible,

    depends=Row('depends', 'on', G.expr) ^ Depends,

    range=Row('range', G.value, G.value, G.opt_condition) ^ Range,

    comment=Row('comment', G.string_literal) ^ Comment,

    # Misc options

    # TODO: Here we could add handling of custom (user defined) options that
    # would provide additional features for GPR files.
    # For instance : option source_dir="src/some_feature"
    option=Row('option', Or(Tok(Token.OptDefConfigList, keep=True),
                            Tok(Token.OptModules,       keep=True),
                            Tok(Token.OptEnv,           keep=True),
                            Tok(Token.OptAllNoConfY,    keep=True)
                            ),
               Opt ('=', G.string_literal)) ^ Option,

    source=Row('source', G.string_literal) ^ Source,

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
