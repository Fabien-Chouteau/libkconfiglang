from langkit.dsl import ASTNode, EnumNode, Field, abstract
from langkit.parsers import Grammar, List, Opt, Or, Pick

from lexer import Token

@abstract
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
    title = Field()

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
    token_node = True

class BoolLiteral(KConfigNode):
    token_node = True

class IntLiteral(KConfigNode):
    token_node = True

class HexLiteral(KConfigNode):
    token_node = True

class StringLiteral(KConfigNode):
    token_node = True

class Identifier(KConfigNode):
    token_node = True

class Comment(KConfigNode):
    string = Field()

class Visible(KConfigNode):
    condition = Field()

@abstract
class Property(KConfigNode):
    pass

class BuiltinType(KConfigNode):
    token_node = True

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

class OptionName(KConfigNode):
    token_node = True

class Option(Property):
    opt_name = Field()
    value    = Field()

@abstract
class Expression(KConfigNode):
    pass

class NotExpr(Expression):
    a = Field()

class Operator(EnumNode):
    alternatives = ['equal_op', 'diff_op', 'and_op', 'or_op']

class BinaryExpr(Expression):
    lhs = Field()
    op = Field()
    rhs = Field()

kconfig_grammar = Grammar('main_rule')

G = kconfig_grammar

kconfig_grammar.add_rules(

    # Main rule
    main_rule=RootNode(Opt(G.mainmenu), G.block),

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
    config=Config('config', G.identifier, G.config_options),

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
    menuconfig=MenuConfig('menuconfig', G.identifier, G.menuconfig_options),

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
    menu=Menu('menu', G.string_literal, Opt (G.visible), G.block, 'endmenu'),

    # If
    if_rule=If('if', G.expr, G.block, 'endif'),

    # Choice
    choice=Choice('choice', G.choice_options, G.config_list, 'endchoice'),
    choice_options=List(Or(G.depends,
                           G.prompt,
                           G.default_choice)),

    default_choice=DefaultChoice('default', G.identifier, G.opt_condition),

    # Symbol
    identifier=Identifier(Token.Identifier),

    # Mainmenu
    mainmenu=MainMenu('mainmenu', G.string_literal),

    # Optional condition
    opt_condition=Opt('if', G.expr),

    # Literals
    tristate_literal=TristateLiteral(Or(Token.Yes, Token.No, Token.Module)),

    bool_literal=BoolLiteral(Or(Token.Yes, Token.No)),

    int_literal=IntLiteral(Token.Number),

    hex_literal=HexLiteral(Token.HexNumber),

    string_literal=StringLiteral(Token.String),

    value=Or(G.tristate_literal,
             G.bool_literal,
             G.int_literal,
             G.hex_literal,
             G.string_literal),

    # Options

    # TODO: How to grab the text between help and the empty line
    help=Help('help', Token.EmptyLine),

    type=Type(BuiltinType(Or(Token.Tristate,
                             Token.Bool,
                             Token.Int,
                             Token.Hex,
                             Token.StringType)),
              Opt(G.string_literal)),

    prompt=Prompt('prompt', G.string_literal, G.opt_condition),

    default=Default('default', G.value, G.opt_condition),

    def_bool=DefBool('def_bool', G.bool_literal, G.opt_condition),

    def_tristate=DefTristate('def_tristate', G.tristate_literal, G.opt_condition),

    select=Select('select', G.identifier, G.opt_condition),

    imply=Imply('imply', G.identifier, G.opt_condition),

    visible=Visible('visible', 'if', G.expr),

    depends=Depends('depends', 'on', G.expr),

    range=Range('range', G.value, G.value, G.opt_condition),

    comment=Comment('comment', G.string_literal),

    # Misc options

    # TODO: Here we could add handling of custom (user defined) options that
    # would provide additional features for GPR files.
    # For instance : option source_dir="src/some_feature"
    option=Option('option', OptionName(Or(Token.OptDefConfigList,
                                          Token.OptModules,
                                          Token.OptEnv,
                                          Token.OptAllNoConfY)),
                  Opt('=', G.string_literal)),

    source=Source('source', G.string_literal),

    # Expressions

    expr=Or(Pick('(', G.expr, ')'),
            BinaryExpr(G.expr,
                       Or(Operator.alt_equal_op('='),
                          Operator.alt_diff_op('!='),
                          Operator.alt_and_op('&&'),
                          Operator.alt_or_op('||')),
                       G.expr),
            G.identifier,
            G.bool_literal,
            G.tristate_literal,
            NotExpr('!', G.expr),
            ),
)
