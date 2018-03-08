import os, strutils

proc main() =
  if paramCount() != 2:
    echo("usage: sub [a] [b]")
  else:
    echo(parseint(paramStr(1)) - parseint(paramStr(2)))

main()
