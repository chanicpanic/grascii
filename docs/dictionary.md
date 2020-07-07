
# Grascii Dictionary

Grascii comes with the Grascii forms of all words in the 1916 Gregg 
Shorthand Dictionary.

These mappings of Grascii strings to their corresponding words are
contained in a series of text files in the `dsrc` directory.

These dictionary source files can then be compiled into the dictionary
format that Grascii Search expects using `grascii.py`'s `build` subcommand.

## Dictionary Source File Layout

### Basic Entry

Each entry in a dictionary source file is contained on its own line in
the following scheme:

`[Grascii String] [Translation]`

There can be any amount of whitespace surrounding the Grascii String and 
its Translation.

Both Grascii String and Translation are case-insensitive.

### Blank Lines

Blank Lines are ignored

### Comments

Lines whose first non-whitespace character is a `#` are ignored.

`# This is a comment`

### Uncertainties

An entry preceded by a `?` will produce a warning during the build phase.

```
# I am not sure if that is an A or an E
? ken keen
```