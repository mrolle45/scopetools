# Python Name Resolution Rules

This document specifies the complete set of rules for resolving a name (an identifier) at runtime in a running Python program, and getting, setting, or deleting its current value.

Contents:
- [Syntax tree for the Python program](#syntax-tree)
- [Scope -- static state](#scope)
  - [Name resolution rules](#scope-name-resolution)
- [Namespace -- dynamic state](#namespace)
  - [Operations](#dynamic-operations)
  - [Name resolution rules](#namespace-name-resolution)

# Syntax Tree

When a program is compiled, it is first converted to a **syntax tree**, which is described in the [ast](https://docs.python.org/3.10/library/ast.html) module.  This is an `ast.Module` object.  It is then converted to a binary format which can be executed by the interpreter at the time the module is imported.  The syntax tree can be obtained directly with the `ast.parse()` function.

A **node**, or **AST node** is an object which is a subclass of `ast.AST`.  In this document, **AST** is shorthand for any `ast.AST` node.  
An AST has some **child** objects[^ASTChild], some of which can be other ASTs.  A non-AST child is called a **leaf**, or **AST leaf**

An **item**, or **AST item**, is either a node or a leaf.

Each item represents a single contiguous section of the text.  Children of a node represent subsets of that section of text.  Some node classes have attributes (which are not child items) showing the range of the text.

foo [^Foo]


# Scope

## Scope Name Resolution

# Namespace

## Dynamic Operations

## Namespace Name Resolution


# Running Tests

This mostly[^othertests] describes the module [scopestest.py](scopestest.py).  This is a standalone module, to be run separately as a script.

[^othertests]: Some other modules in the package, when run as standalone scripts, contain a few simple tests to verify that their functionality works.  You can run them as part of a test suite.  
    - [namespaces.py](namespaces.py)
    - [scopes.py](scopes.py)
    - [treebuild.py](treebuild.py)

[^ASTChild]: The children of an AST node are found by looking at the class attribute `node._fields`, which is a tuple of attribute names.  Some nodes have other attributes that are not fields, and these are ignored.  
    
    The [ast grammar](https://docs.python.org/3.10/library/ast.html#abstract-grammar) shows the names and types of fields of each AST node class, in the form `class(field, ...)`.  

    For each `field` the node has 0 or more child objects, depending on the coding of `field` as shown in this table.  `T` is the type of the child.  `value` is the value of `node.name`.  

    | field | value type | count | children |
    |:-|:-|:-|:-|
    | T name | T | 1 | [value] |
    | T? name | T \| None | 0 or 1 | filter(None, [value]) |
    | T* name | list[T] | 0 or more | value[:] |

[^Foo]: Bar

