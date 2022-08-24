# Typing Information for Scopes

This document describes ways in which typing information can be provided in a Python module, and methods for conveying that information to `TreeT` trees maintained by this `scopetools` package.

`Scope` trees do not use any typing information, with one exception:
- A *bare* annotated assignment without a value, as in `name: anno`, defines `"name"` as a local variable.  This is conveyed by the method call  
 `tree.bind("name", anno=True)`.  
Note, if the name is parenthesized, this is treated as an expression, and so `(name): anno` *does not* bind `"name"`.  Refer to the [table](#annotated-assignment)

## Static and Dynamic Types

Every python object at runtime has a **dynamic type**.  This is simply the class of the object.  It is a "dynamic" type because the same variable, or expression, can have different classes at different times.

A **static type** is a constraint upon the dynamic type of a runtime object (actually, any `ast.Expr` node in the syntax tree).  It is an assertion that the dynamic type is one which is allowed by the static type.  It may also constrain the actual value of an object, as well as its class.

In this document, the term **type** means a static type, unless otherwise qualified.

Every class is a type.  That is, class `C` asserts that `isinstance(obj, C)` is true.

All other types are objects defined in the [`typing`](https://docs.python.org/3.10/library/typing.html) module.  Most of the classes defined there are usable as types.  A few, such as `TypeVar`, are not.

A static type checker verifies that the dynamic type of an object conforms to its static type.  To do this, it needs to know the static type.  There are the following methods to obtain this:
- **Type hints**.  These are found in the module code.  A type hint specifies a type for a target.  The target may be:
    - A variable name.
    - An named attribute of an object, such as `expr.x`.
    - A subscript of an object, such as `expr1[expr2]`

    There are three forms of type hint information found in a module:
    - Annotations.
    - Type comments.
    - Type ignores.
- **Type expression or alias**.  Any static type object may appear as an expression in the code.  This expression can be used as a type hint, or part of a type hint.  Furthermore, it can be assigned to a global or class variable, and that variable can also be used the same as type expression.  This is called a type alias.  
[PEP 613](https://peps.python.org/pep-0613/) provides a way of making the type alias clear to the type checker, by annotating the alias variable as `alias: TypeAlias = typ`.
- **Type inference**.  When a target is assigned a value in the code, the type checker can infer that the target has the type of the value,
or more generally, that the target type includes the value type.  
There may be several such assignments for the same target; in this case, the type checker might use the first one it sees and require that all further assignments conform to this type, or it might expand the type to include all the different assigned types.

- **Type narrowing**.  At some points in a code block, the type of a particular target can be inferred to be a restricted subset of the target's type.  For example, `assert x is not None` tells the type checker that the type of `x` does not include the type `NoneType` during subsequent statements in that code block.  A discussion of this in mypy is found [here](https://mypy.readthedocs.io/en/stable/type_narrowing.html).  
- **Unreachable code**.  Some code in the module will never be executed,  and should be ignored by the type checker.  These are typically enclosed in `if` statements which test some expression of known boolean value.  It could be an object which is known to have fixed value, or a comparison with `sys.version_info` or `sys.platform`, or after a `return` or `raise`.
  
## Annotations

Type annotations are the newer way of providing typing information for variables and other targets with attributes or indexing.

An **annotation** is a Python expression, which represents a static type.  It is used at runtime by the statement in which it appears, in one of three ways:
1. The expression is actually evaluated and the result is used as the annotation.
2. The text of the expression, as a string, is written as the annotation and termed a **forward reference**.  It is not evaluated at runtime, and only used by the type checker.
3. If the module uses **future annotations**, by having a `from __future__ import annotations` statement in the module, then all annotation text is compiled as a string.  This may someday (3.11 or later) become the standard behavior.  
Historically, annotations have been used by code analysis tools for purposes other than type checking.  This is why forward references are not already standard behavior.  

In this `scopetools` package, all annotations will be forward references, even without any future annotations in the module.  Any application that needs to evaluate the string can use `typing.get_type_hints()`.  The AST traverser in `treebuild.py` will convert annotation expressions to forward references.  Conversely, an application which has an annotation in the form of an `ast.Expr` node needs to call `node.unparse()`, and it should check that the expression can be evaluated without error.

Annotations appear in the python code, or the AST, in the following:
#### Function argument
`AST: ast.arg`.  
  The target is `AST.arg`; this is a simple `ast.Name` identifier.  The annotation is `AST.annotation`.  This is reported as `tree.anno(target, annotation)`
#### Function return type
In `AST: ast.FunctionDef`  
The annotation is `AST.returns`.  This is reported as `tree.anno_return(annotation)`
#### Annotated assignment
`AST: ast.AnnAssign`  
  This has two parts, an annotation definition, and an optional assignment to a value.  
The optional assignment is treated the same as an ordinary assignment statement, as `{AST.target} = {AST.value}`.  At runtime, the assignment is performed *before* the annotation is performed.  
The annotation is treated according to the class of `AST.target`, and the value of `AST.simple`:

| target class | simple | scope effect | runtime effect
|:-|:-|:-|:-|
| `ast.Name` | 1 | Make `AST.id` a local variable in FUNC tree only. | Set `__annotations[{AST.id}]` = annotation in CLASS or GLOB tree only.
| `ast.Name` | 0 | None. | None.
| `ast.Attribute` | 0 |  None. | Evaluate `AST.value`, *but not* `{AST.value}.{AST.attr}`.
| `ast.Subscript` | 0 |  None. | Evaluate `AST.value` and  `AST.slice`, *but not* `{AST.value}.[{AST.slice}]`.

## Type Comments

A **type comment** is a comment of the form  
`# type: {typ}`.  See [PEP 484](https://peps.python.org/pep-0484/#type-comments).  
It provides information to a type checker about the type of an associated target.
It may appear only in a few specific places in the program.  The AST for the target will have an `AST.type_comment` item containing the text of `typ`.

`typ` specifies one or more types.  It must be a syntactically valid expression.  It is not evaluated at runtime.  It may be evaluated by a type checker, just like any Python expression, except that the result must be a valid type.

A type comment is analogous to an assignment statement, `target = [target = ...] value`, but with `typ` being the `value`.  As with an assignment, if `target` is an unpacking (i.e. `[targ1, targ2]`) then `typ` is similarly unpacked.

These are the places it may appear and the corresponding target(s):
- A **function argument**, on the same line.  The target is just the argument name.
- A **function definition**, immediately after the colon.  The `typ` is of the form `([arg typ, ]... or a literal '...') -> ret typ`.
The `typ` can be parsed with `ast.parse(typ, mode='func_type')`.  This produces an `ast.FunctionType` with items `node.argtypes[:]` and `node.returns`, which are all `ast.Expr` nodes.  These items are the `typ`s for the function's arguments (in the same order) and return type.
- An **assignment statement**, on the last line.  There may be multiple targets.  The type is treated as though it were the right hand side of the same assignment.  That is, when a target is an unpacking, the type must be an iterable of corresponding types; this is applied recursively.
- A **`for`** `target in iter: # type: typ` statement.  The target is just `target`.
- A **`with`** `... : # type: typ`.  It contains a number of `context [as item]` clauses.  The overall target is a tuple of the `item`s in each `as item` that appears.  

The type comment is conveyed to the tree by  
**`tree.type_comment(target: Target, info: str)`**.

## Type Ignores

A comment of the form `# type: ignore` may appear anywhere in a Python module.  This is a hint for a type checker to perform no type checking for the statement which includes that line.

The AST node for a statement in a module provides the line number range for that statement.  The node does not convey which line(s) have type ignores.

The AST node for the entire module has an item `ast.Module.type_ignores`.  This is a list of the line numbers in the entire module which contain type ignores.

The method **`tree.type_ignores(linenos: list[int])`** conveys the line numbers to the GLOB tree for the module.

(Future enhancement) The AST traverser in `treebuild.py` will provide an indicator that a particular statement has a type ignore.  The traverser can be set to require that the type ignore appear on the last line of the statement.

Note, like type comments, the supposed intention of the type: ignore feature is that the type ignore appear at the end of the statement in question.

###  Type Ignore Module

Quote from [PEP 484](https://peps.python.org/pep-0484/#type-comments):

> A # type: ignore comment on a line by itself at the top of a file, before any docstrings, imports, or other executable code, silences all errors in the file. Blank lines and other comments, such as shebang lines and coding cookies, may precede the # type: ignore comment.

The GLOB tree will need to examine the AST for the module to determine if the first type ignore line satisfies the above requirement.  
(Future enhancement) The AST traverser in `treebuild.py` will provide this indication, via `tree.type_ignores(linenos, all=True)`.
