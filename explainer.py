#!/usr/bin/env python3

from antlr4 import *
from PlSqlLexer import PlSqlLexer
from PlSqlParser import PlSqlParser
from PlSqlParserListener import PlSqlParserListener
import sys

class CaseChangingStream():
    def __init__(self, stream, upper=True):
        self._stream = stream
        self._upper = upper

    def __getattr__(self, name):
        return self._stream.__getattribute__(name)

    def LA(self, offset):
        c = self._stream.LA(offset)
        if c <= 0:
            return c
        return ord(chr(c).upper() if self._upper else chr(c).lower())

class Listener(PlSqlParserListener):
    def __init__(self, script):
        self._script = script
        self._explainable = list()

    def explained_script(self):
        prev = 0
        last = -1
        parts = list()
        for point, end in sorted(self._explainable):
            if point > last:
                parts.append(self._script[prev:point])
                prev = point
                last = end
        parts.append(self._script[prev:])
        return ' EXPLAIN ( ANALYZE, COSTS, FROMAT JSON ) '.join(parts)
        

    def enterExplainable(self, ctx):
        start=ctx.start.start
        stop=ctx.stop.stop
        self._explainable.append((start, stop+1))

    def enterSelect_statement(self, ctx):
        self.enterExplainable(ctx)
    def enterUpdate_statement(self, ctx):
        self.enterExplainable(ctx)
    def enterDelete_statement(self, ctx):
        self.enterExplainable(ctx)
    def enterInsert_statement(self, ctx):
        self.enterExplainable(ctx)

def explain(script):
    lexer = PlSqlLexer(CaseChangingStream(InputStream(script)))
    stream = CommonTokenStream(lexer)
    parser = PlSqlParser(stream)
    tree = parser.sql_script()
    listener = Listener(script)
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    return listener.explained_script()

def main():
    import glob
    for p in glob.glob('examples/*.sl'):
        with open(p) as pf:
            script=pf.read()
            print(script)
            print(explain(script))
    script = ' BEGIN SELECT * FROM A; END; update B SET c=d;'
    print(explain(script))

if __name__ == '__main__':
    main()
