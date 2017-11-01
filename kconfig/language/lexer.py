from langkit.lexer import Lexer, LexerToken, Literal, WithText, \
     WithSymbol, Pattern, Ignore


class Token(LexerToken):

    Example = WithText()

    # Keywords
    Config = WithText()
    Menuconfig = WithText()
    Choice = WithText()
    Endchoice = WithText()
    Comment = WithText()
    Menu = WithText()
    Endmenu = WithText()
    If = WithText()
    Endif = WithText()
    Source = WithText()
    Mainmenu = WithText()


    Depends = WithText()
    On = WithText()
    Help = WithText()
    Prompt = WithText()
    Default = WithText()
    Select = WithText()
    Imply = WithText()
    Range = WithText()
    Visible = WithText()

    # The help text is terminated by an empty line
    EmptyLine = WithText()

    String = WithText()

    # Types
    Tristate = WithText()
    Bool = WithText()
    Int = WithText()
    Hex = WithText()
    StringType = WithText()

    Identifier = WithSymbol()
    Number     = WithSymbol()
    HexNumber  = WithSymbol()
    Yes        = WithSymbol()
    No         = WithSymbol()
    Module     = WithSymbol()

    LPar       = WithText()
    RPar       = WithText()
    Equal      = WithText()
    Different  = WithText()
    Not        = WithText()
    Or         = WithText()
    And        = WithText()

kconfig_lexer = Lexer(Token)
kconfig_lexer.add_rules(
    (Literal("example"),     Token.Example),

    (Pattern(r"[ \t\r\n]+"),  Ignore()),
    (Pattern(r"#.*"),         Ignore()),

    # Keywords
    (Literal("config"),     Token.Config),
    (Literal("menuconfig"), Token.Menuconfig),
    (Literal("choice"),     Token.Choice),
    (Literal("endchoice"),  Token.Endchoice),
    (Literal("comment"),    Token.Comment),
    (Literal("menu"),       Token.Menu),
    (Literal("endmenu"),    Token.Endmenu),
    (Literal("if"),         Token.If),
    (Literal("endif"),      Token.Endif),
    (Literal("source"),     Token.Source),
    (Literal("mainmenu"),   Token.Mainmenu),
    (Literal("depends"),    Token.Depends),
    (Literal("on"),         Token.On),
    (Literal("help"),       Token.Help),
    (Literal("prompt"),     Token.Prompt),
    (Literal("default"),    Token.Default),
    (Literal("select"),     Token.Select),
    (Literal("imply"),      Token.Imply),
    (Literal("range"),      Token.Range),
    (Literal("visible"),    Token.Visible),

    # Types
    (Literal("tristate"), Token.Tristate),
    (Literal("bool"),     Token.Bool),
    (Literal("int"),      Token.Int),
    (Literal("hex"),      Token.Hex),
    (Literal("string"),   Token.StringType),

    (Literal("="),    Token.Equal),
    (Literal("!="),   Token.Different),
    (Literal("("),    Token.LPar),
    (Literal(")"),    Token.RPar),
    (Literal("!"),    Token.Not),
    (Literal("&&"),   Token.And),
    (Literal("||"),   Token.Or),

    (Literal("y"),                     Token.Yes),
    (Literal("n"),                     Token.No),
    (Literal("m"),                     Token.Module),

    (Pattern(r"[a-zA-Z][a-zA-Z0-9]*"),                                  Token.Identifier),
    (Pattern(r"[0-9]+"),                                                Token.Number),
    (Pattern(r"0x[0-9]+"),                                              Token.HexNumber),
    (Pattern(r'\"(\"\"|(\[\"([0-9A-F][0-9A-F]){2,4}\"\])|[^\n\"])*\"'), Token.String),
)
