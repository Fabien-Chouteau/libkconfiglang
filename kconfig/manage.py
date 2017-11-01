#! /usr/bin/env python

import os

from langkit.libmanage import ManageScript


class Manage(ManageScript):
    def create_context(self, args):
        from langkit.compile_context import CompileCtx

        from language.lexer import kconfig_lexer
        from language.parser import kconfig_grammar

        return CompileCtx(lang_name='KConfig',
                          lexer=kconfig_lexer,
                          grammar=kconfig_grammar)

if __name__ == '__main__':
    Manage().run()
