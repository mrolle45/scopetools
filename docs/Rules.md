# Python Name Resolution Rules

This document specifies the complete set of rules for resolving a name (an identifier) at runtime in a running Python program, and getting, setting, or deleting its current value.

# Table of contents

- [Syntax Tree](#syntax-tree)
  - [Inclusion Relationships](#inclusion-relationships)
- [Scope](#scope)
  - [Scope Kinds](#scope-kinds)
  - [Closed and open scopes](#closed-and-open-scopes)
  - [Scope Owned Items and Item Owner Scopes.](#scope-owned-items-and-item-owner-scopes)
  - [Child Items Not Direct Items of Scope](#child-items-not-direct-items-of-scope)
  - [Scope Tree](#scope-tree)
- [Variables](#variables)
  - [Variable Name](#variable-name)
  - [References](#references)
  - [Context of a Reference](#context-of-a-reference)
  - [Variable Identity](#variable-identity)
- [Scope Name Resolution](#scope-name-resolution)
  - [Binder Scope and Binding Variable](#binder-scope-and-binding-variable)
  - [LOCS Scope and builtin `locals()` function](#locs-scope-and-builtin-locals-function)
  - [CELL Type and Captured Variables](#cell-type-and-captured-variables)
- [Namespace](#namespace)
  - [<span hidden>Namespace </span>Static State](#namespace-static-state)
  - [Namespace Lifecycle](#namespace-lifecycle)
  - [Namespace Tree](#namespace-tree)
  - [Binder Namespace for Variable](#binder-namespace-for-variable)
  - [Dynamic State](#dynamic-state)
  - [Namespace Name Resolution](#namespace-name-resolution)
- [Summary of Rules](#summary-of-rules)# Syntax Tree

When a program is compiled, it is first converted to a **syntax tree**, which is described in the [ast](https://docs.python.org/3.10/library/ast.html) module.  This is an `ast.Module` object.  It is then converted to a binary format which can be executed by the interpreter at the time the module is imported.  The syntax tree can be obtained directly with the `ast.parse()` function.

Other text, besides Python programs, can be parsed or compiled.  `mode='eval'` produces an `ast.Expression` node.  `mode='func_type_'` produces an `ast.FunctionType` node.

A **node**, or **AST node** is an object which is a subclass of `ast.AST`.  In this document, **AST** is shorthand for any `ast.AST` node.  
An AST has some **child** objects[^ast-child], some of which can be other ASTs.  A non-AST child is called a **leaf**, or **AST leaf**.  
The terms **parent**, **root**, **ancestor** and **descendant** follow from the "child" relationship according to standard tree structure terminology.

An **item**, or **AST item**, is either a node or a leaf.

Each item represents a single contiguous section of the parsed text.  Children of a node represent nonoverlapping subsets of that section of text.  Some node classes have attributes [^other-ast-attrs] (which are not child items) showing the location of the text within the root's text.

[^other-ast-attrs]: ### Text span attributes of AST node
Refer to the [`ast` module documentation](https://docs.python.org/library/ast.html#node-classes) for the `lineno`, `end_lineno`, `col_offset` and `end_col_offset` attributes of `ast.expr` and `ast.stmt` subclasses.

## Inclusion Relationships

- **node >> item**, or **item << node** -- `item` is a child of `node`.  
- **node > item**, or **item < node** -- `item` is a descendant of `node`.  
There is a chain `node` [ >> `another node` ]... >> `item`.  
- **node >= item**, or **item <= node** -- `node` >> `item` or `node` is `item`.  

[^ast-child]: ### AST node child items.
The children of an AST node are found by looking at the class attribute `node._fields`, which is a tuple of attribute names.  Some nodes have other attributes that are not fields, and these are ignored.  
    
    The [ast grammar](https://docs.python.org/3.10/library/ast.html#abstract-grammar) shows the names and types of fields of each AST node class, in the form `class(field, ...)`.  

    For each `field` the node has 0 or more child objects, depending on the coding of `field` as shown in this table.  `T` is the type of the child.  `value` is the value of `node.name`.  

    | field | value type | count | children |
    |:-|:-|:-|:-|
    | T name | T | 1 | [value] |
    | T? name | T \| None | 0 or 1 | filter(None, [value]) |
    | T* name | list[T] | 0 or more | value[:] |


# Scope

A few specific node classes define **AST scopes**, or simply, **scopes**.

## Scope Kinds

The **kind** of a scope is denoted by an enumeration, **ScopeKind** in [scope_common.py](../scopetools/scope_common.py#:~:text=class%20ScopeKind).  Each kind represents a certain node class or classes, and corresponding elements of the Python program.

|    kind      | AST class | Python code |
|:-------------|:--|:--
|ROOT| n/a | (container for GLOBs of different modules)
|GLOB| ast.Module | entire module
|CLASS| ast.ClassDef | `class` statement + decorators
|FUNC| ast.FunctionDef |`def` statement + decorators
|    | ast.AsyncFunctionDef |`async def` statement + decorators
|LAMB| ast.Lambda |`lambda` expression
|COMP| ast.ListComp |`[expr for var in iter ...]`
|    | ast.SetComp |`{expr for var in iter ...}`
|    | ast.DictComp |`{key : expr for var in iter ...]`
|    | ast.GeneratorExp |`(expr for var in iter ...)`
|LOCS| n/a | call to locals()
|EXEC| ast.Module | input to exec()
|EVAL| ast.Expression | input to eval()

For brevity, any of these kind names can be used to mean an AST having that kind.

The name **EVEX** means either EVAL or EVEX.  The expression **evex()** refers to calling either of the builtin `eval` or `exec` functions.  The difference between them is that eval() takes an expression and returns the evaluation of that expression, and exec() takes a complete module text and returns None.

### Scope Kind Hierarchy

The scopes.py module defines a `Scope` class and a hierarchy of subclasses.  These subclasses correspond to different Kinds.

| Class | Kind |
|:--|:--|
| Scope | |
| - RootScope | ROOT |
| - OpenScope <sup>[1]</sup> | OPEN |
| - - GlobalScope | GLOB |
| - - ClassScope | CLASS |
| - - LocalsScope | LOCS |
| - - - ExecEvalScope <sup>[1]</sup> | EVEX |
| - - - - ExecScope | EXEC |
| - - - - EvalScope | EVAL |
| - ClosedScope <sup>[1]</sup> | CLOS |
| - - FunctionScope | FUNC |
| - - LambdaScope | LAMB |
| - - ComprehensionScope | COMP |

[1] Abstract class

The property **scope.isKIND** is true if `scope` is an instance of the corresponding class.  This includes subclasses, so for example, for a LambdaScope, `scope.isLAMB` and `scope.isCLOS` are both True.

## Closed and open scopes
In a **closed scope**, or **CLOS**, at runtime, the known variable names cannot be extended dynamically (e.g. by monkey-patching).  They are all determined at compile time.

In an **open scope**, or **OPEN**, at runtime, additional variables can be associated with the scope.

## Scope Owned Items and Item Owner Scopes.

The relationship of **scope owns item**, or **scope -> item**, or **item <- scope**, is defined below in such a way that every item in the entire AST is owned by exactly one scope.  Thus it can be written that **scope is item.owner**.

The relationship **scope ->> item** is also defined below.

### scope ->> direct item

Certain items in a scope AST are classified as **direct items**, and notated as **`scope` ->> `item`**.  They are listed in this table:

| kind | item | location
|:--|:--|:--|
| GLOB | statement | scope.body[:]
| CLASS | statement | scope.body[:]
| FUNC | statement | scope.body[:]
| | argument | scope.args.*various* [^FUNC-and-LAMB-arguments]
| LAMB | expression | scope.body
| | argument | scope.args.*various* [^FUNC-and-LAMB-arguments]
| COMP | everything **except** | 
| | first iterable | scope.generators[0].iter
| LOCS | none | 
| EXEC [^exec-and-eval] | statement | scope.body[:]
| EVAL [^exec-and-eval] | expression | scope.body[:]
| Not COMP | COMP walrus[^scope-comp-walrus] target | walrus.id

[^exec-and-eval]: EXEC and EVAL scopes.  
Calling `exec(code, [globals, [locals, ]])` or `eval(code, [globals, [locals, ]])` results in an EXEC or EVAL scope.

    Its parent is
- The owner scope of the call, if no `globals` is given, or is given the same as the builtin globals().
- A new GLOB scope, otherwise.  The property **GLOB.initial** designates this `globals` dict.  At runtime, the GLOB namespace will be initially populated with the contents of `globals`.  If several scopes are created with the same `globals` argument, then their parents should be the same GLOB.

    The property **scope.locals** designates the `locals` argument, if provided and is not the same as the builtin `globals()`, or None otherwise. 

    At runtime, the call, as with any other call, immediately executes the code in a new namespace.  If GLOB.initial exists, it is used to populate GLOB's initial bindings.  If `scope.locals` exists, this will be the initial local bindings, otherwise a copy of GLOB's bindings will be used.

[^FUNC-and-LAMB-arguments]:
In this table, **scope.args.*various*** means a collection of items, which comprise all the arguments to a function or a lambda.  They include the argument name.  In a function, they also include any annotations or type comments.
The items are, in this order:
- scope.args.posonlyargs[:]
- scope.args.args[:]
- scope.args.vararg
- scope.args.kwonlyargs[:]
- scope.args.kwarg

    This comprises all of scope.args except scope.args.defaults and scope.args.kw__defaults.
[^scope-comp-walrus]:
In this table, **COMP walrus** of `scope` means the target name of an assignment expression in the COMP subtree of `scope.  

    Note that *only* the target name, `wal.id`, is the direct item of `scope`.  The assigned value, `wal.value` *is not*.

### scope -> owned item

**`scope` -> `item`** if:

1. `scope` is a scope AST instance.
2. `scope` ->> `dir` >= `item`, for some direct item `dir`.
3. There is no other scope AST `scope2` and direct item `dir` of `scope2` such that `scope` > `scope2` ->> `dir` -> `item`.

Note, `item` can be another scope AST.  

In other words, a scope contains all direct items, plus all of their descendants, minus any child scope's items.

## Child Items Not Direct Items of Scope

Another way of stating when an item < a scope are owned by it is to specify which items *are not* owned by it.

| Kind | Items | Location | Owned by |
|:--|:--|:--|:--|
| GLOB | (none) | | |
| CLASS | decorator | scope.decorator_list[:] | parent |
| | base class | scope.bases[:] | parent |
| | keyword arg | scope.keywords[:] | parent |
| FUNC | decorator | scope.decorator_list[:] | parent |
| | default value | scope.args[:].defaults[:] | parent |
| | | scope.args[:].kw_defaults[:] | parent <sup>[1]</sup> |
| LAMB | default value | scope.args[:].defaults[:] | parent |
| | | scope.args[:].kw_defaults[:] | parent <sup>[1]</sup> |
| COMP | first iterable | scope.generators[0].iter | parent |
| | target of walrus | walrus.target, where walrus <- scope | COMP owner|
| LOCS | (none) | |
| EVAL | (none) | |
| EXEC | (none) | |

[1] Some elements of `kw_defaults` may be `None`.  These are not owned by any scope.

## Scope Tree

Scopes form a tree structure, using the relationship **`parent` -> `child`**.  
`parent` is the **parent** of `child`, and denoted as **child.parent**.  
Conversely, `child` is a **child** of `parent`.  
The **parent chain** of a scope is the sequence starting with the scope and followed by successive parents, ending with ROOT.  
Conversely, the **subtree** of a scope is the tree starting with the scope and moving down to the subtrees of its child scopes.  
The **ancestor chain** of a scope are the parent chain, without the scope itself.  ROOT has no ancestors.  
Conversely, the **descendants** of a scope are all scopes in the subtree, without the scope itself.  
The **global scope** of a scope, also denoted as **scope.glob** is the GLOB in the parent chain.  ROOT has no global scope.  
The **root scope** of a scope, also denoted as **scope.root**, is the ROOT at the end of the parent chain.  
The **COMP subtree** of a scope is all COMPs in the subtree such that `scope [ -> another COMP ]... ->= COMP`.  That is, the scope itself, if it is a COMP, and moving down to all COMP children, and to their COMP children, *etc*.  Note, a COMP could be in the subtree but not in the COMP subtree if there is a LAMB scope between the scope and the COMP.  
Conversely, the **COMP owner** of a COMP, or **COMP.comp_owner**, is the first non-COMP scope in the parent chain.  The **COMP parent chain** is the parent chain, up to but not including the COMP owner.

The tree looks like this:
- ROOT
  - GLOB
    - other kinds
      - other kinds
        - *etc.*
          
See special cases [^exec-and-eval] for EXEC and EVAL.


# Variables

A **variable** is a name (any Python identifier) which *can have* a **value** at runtime.  This value can be any Python object, and the variable is said to be **bound to** that object.  The variable can also have no value, in which case the variable is said to be **unbound**.

During execution of the program, the state of the variable can change, by binding it to a new or different value or by making it unbound.  This is why it is called a "variable".

A **variable** is almost any occurrence of a Python identifier in a syntax tree.  The grammar determines whether an identifier is a variable or not.

Identifiers that are *not* variables are shown here [^non-variables]:
[^non-variables]: ### Identifiers that are not variables
- Attributes, as in `(expression).attribute`, in an `ast.Attribute` node.
- Some identifiers in an import statement.  It is simpler to specify which identifier **is** a variable which is bound according to [the document for Import statement](https://docs.python.org/3.10/reference/simple_stmts.html#the-import-statement)
         ```py
        import module as variable
        import variable(.name)*     # Note, only the top level identifier is bound
        from module import variable
        from module import name as variable
        ```
- A keyword in a function call, as in `function(keyword=expression)`

This document is concerned only with variables.
        
## Variable Name

The **name** of a variable, as seen by the compiler or at runtime by the compiled code, is the same as the identifier AST item, except for special cases:

- If importing a module with a dotted name, and without an 'as alias' clause, the variable name is that part before the first dot.  
For example, `import ..foo.bar` in package `pkg` treats `foo` as the variable name, which is bound to the module `pkg.foo`.  `bar` is an attribute name of variable `foo`, which is the module `pkg.foo.bar`.
- If this name is a **private name**, the `name.mangled` name is used.

### Private Name Mangling

This is described in [Language doc 6.2.1](https://docs.python.org/3.10/reference/expressions.html#:~:text=private%20name%20mangling), in the section "**Private Name Mangling**".

Every syntax item has, possibly, a **mangler**.  This is the nearest CLASS scope which contains the item's owner scope.  If there is no such CLASS, then there is no mangler.

In a CLASS scope, `cls`, the compiler treats certain [^private-name] name items as **private names**.  This applies to any `name` where `cls` is `name.mangler`, by replacing `name` with a transformed [^private-mangle] version of `var`.  This is also known as the **mangled name**, or **name.mangled**.

The purpose is to allow a name to be used in a class without conflicting with the same name in a subclass or superclass.

Important:
- A name is private *solely* as a function of the name and the name of the mangler.  
- A name can be private even if it is declared global or nonlocal, or is the name of an imported module.
- The name is mangled anywhere in the mangler, including nested scopes, other than in another (nested) CLASS.
- The name is *not mangled* in any other location in the program.  If the program needs to refer to the name (as an instance or class variable, or above the mangler scope), it must compute [^private-mangle] the mangled name and use that instead.  Note the exceptional cases discussed there.

    I have created an [enhancement proposal](https://github.com/python/cpython/issues/95621) for cpython to provide functionality in the language which computes the mangled name as a classmethod of the mangler class, without exceptional cases.  Please feel free to read this and comment on it.

[^private-name]:
A `name` is private to a mangler scope based solely on `name` and `mangler.name`.  The requirements are:
- `name.startswith("__")
- and `name var.endswith("__")`
- and `mangler.name.lstrip("_") != ""` (i.e., anything other than all '_' characters)

[^private-mangle]:
The mangled name `name.mangled` is *usually* computed by
```
f'_{name.mangler.name.lstrip("_")}{name}'
```
For example, the name '\_\_\_x_' in mangler '\_\_C__` is mangled to '\_C_____x_'.

    **Exception with very long names** [^very-long-names].

[^very-long-names]:
The description of name transformation referenced above is *not entirely correct*, as it says:

  >  If the transformed name is extremely long (longer than 255 characters), implementation defined truncation may happen.  

   This is not a problem for program where `len(class_name) + len(name) <= 254`.  For a general code analysis tool, where arbitrary names might appear, because of this implementation-defined behavior, the only reliable way to transform the name is something like this:
``` py
def transform(name: str, class_name: str) -> str:
    d = {}
    exec(f'''class {class_name}:
    loc = set(locals())
    {name} = 0                  # make it a local variable
    loc = set(locals()) - loc
    loc.remove('loc')           # Only transformed name remains.
    transformed = loc.pop()
    ''',  d)
    return d[class_name].transformed
```
This is implemented in the method **scopetools.mangle(cls_name: str, var_name: str) -> str**.  Also by **scopetools.ScopeTree.mangle(var_name: str) -> str**, which can be called on a tree object of any kind and any tree type.

## References

Each occurrence of a variable in the syntax tree is called a **reference**.  The occurrence is a syntax item.
A reference is a **declaration reference**, a **binding reference**, a **value reference**, or a **walrus reference**.

### Declaration reference

This is a statement which tells the compiler that the variable(s) are associated with a different scope.  This alters resolution of the variable name.  There is no runtime behavior.

| Declaration | AST Node | Var Items | Statement |
|:--|:--|:--|:--|
| global | ast.Global | node.names[:] | `global name[, name]...`
| nonlocal | ast.Nonlocal | node.names[:] | `nonlocal name[, name]...`

### Binding reference
This implies that the variable is Local in the scope.  Refer to the [documentation](https://docs.python.org/3.10/reference/executionmodel.html#binding-of-names) for name binding. The possibilities are:
- An `ast.Name` node, where the context attribute is either `ast.Store()` or `ast.Del()`.  Yes, a `del variable` statement is considered binding.  There are some exceptions, as noted below.

  This includes a target name in:
    - an assignment statement.
    - an augmented assignment statement.
    - an annotated assignment statement, *except as noted* [^anno-ref].
[^anno-ref]:  An annotated assignment statement has the form  
`target: anno [= value]`  
- If a value is assigned, the assignment is performed *first*, so this can affect any evaluation of `anno`.  It is treated the same as  
`target = value`.  
- If no value is assigned,
      - If `target` is `expr.attr`, then `expr` is evaluated.
      - If `target` is `expr[subscr]`, then `expr` and then `subscr` are evaluated.
- Target is either `name` or `(name)` or other `expr`.
        - If `target` is `(name)`, there is no further effect.  `(name)` **is not a binding reference**
        - If target is other `expr`, there is no further effect.
        - If `target` is `name`, this is a **binding reference**.  Any subsequent global or nonlocal statement is a syntax error.
  - In a CLOS scope, the `anno` expression *is not evaluated*.
  - In an OPEN scope, the `anno` expression is evaluated.  (When future annotations import is in effect, `anno` is a literal string).  If target is plain `name`, sets `__annotations__[name] = anno`.  

    | Statement | Kind | \_\_annotations__ | Bind name | Assign name |
    |:--|:--|:--|:--|:--|
    | name: anno | OPEN | [name] = anno | No | No |
    | name: anno | CLOS | No change | Yes | No |
    | name: anno = 0 | OPEN | [name] = anno | Yes | Yes |
    | name: anno = 0 | CLOS | No change | Yes | Yes |
    | (name): anno | (any) | No change | No | No |
    | (name): anno = 0 | (any) | No change | Yes | Yes |

    - an assignment expression.  Note that the expresion can be contained within an [owned COMP](#owned-comp-of-a-scope-and-comp-owner-scope-of-a-comp).  This is termed a **walrus reference** if the scope itself is a COMP.
    - a 'for' statement target.
    - a 'for' clause in a COMP.  

- The name in a function or class definition.  The definition creates a new scope, but the owner of the name is its parent.
- A parameter name in a function definition.
- Certain references[^import-reference] in an `import` statement name (module name or module member) or alias in an `as variable` clause.
- After `as` in a with statement or except[*]  clause, or in the as-pattern in structural pattern matching.  
With an except[\*] clause, the name is used *twice*: at the start of the clause, to bind the name, and at the end of clause, to unbind the name.  If the handler unbinds the name, the final unbinding does not raise an exception.
- In a capture pattern in structural pattern matching.

[^import-reference]:
    The bound name varies with the syntax of the import statement:  

    | Statement | Name | AST Item |
    |--|--|--|
    | import module as alias | alias | node.names[:].asname |
    | import name | first dotted component of name | node.names[:].name.split('.')[0] |
    | from rel-module import name | name | node.names[:].name |
    | from rel-module import name as alias | alias | node.names[:].asname |
    | from rel-module import * | none (see below) |  |

    For `import *`, the names are not known at compile time, so there are no binding references.  The names are determined at runtime, after importing the module and examining the module's namespace; these names will be bound in the current module's namespace.  
    A code analysis tool, if given the code for the module, could try to deduce all the public names, but this would have to account for any `import *` in the imported module (recursively) and decide how to deal with circular imports.

### Value reference

All other references.
- The use of the current value of the variable.
    This is node.id for any `ast.Name` node in which node.context is `ast.Load()`.  

### Examples:

```py
foo = bar  # 'foo' is binding and 'bar' is value.
foo.append(1)  # 'foo' is a value reference; 'append' is an attribute
import foo  # 'foo' is a binding reference
import foo.bar  # 'foo' is a binding reference;
                # 'bar' is part of the module name and not used in the scope.
```

## Context of a Reference

The **context** of a variable reference in a scope describes how a variable name is used in the scope, and denoted as **scope.context(name)**.

This is an enumeration [`VarCtx`](../scopetools/variables.py#:~:text=class%20VarCtx) in variables.py.  It consists of several bit flags, which may be combined in certain cases.

For brevity, any of these context names may be used to denote:
- a variable with any bits of that context, *i.e.*, `scope.hasLOCAL(var)` means `bool (scope.context(var) & LOCAL)`.
- an attribute of a scope, *i.e.*, `scope.LOCAL` is LOCAL.

Context bits are divided into two categories, **usage** and **type**.

### Variable Usage

This is a function of all the references, both [binding](#binding-reference) and [value](#value-reference), and [declarations](#declaration) to the variable in that scope.

It is a member of `VarCtx` and is denoted **scope.usage(var)**.  It is one or more of:

- **BINDING**.  The variable appears in a binding reference in the scope, or as a walrus target if the scope is a COMP.
- **NLOC_DECL**.  The scope contains a `nonlocal variable` statement.
- **GLOB_DECL**.  The scope contains a `global variable` statement.
Or in the GLOB scope, if any other scope in the subtree contains a `global variable` statement.
- **WALRUS** [^comp-walrus].  Only used in COMPs.  The variable appears as a walrus target in any scope in its COMP subtree.  
- **USE**.  The variable appears in a value reference.
- **UNUSED**.  The variable does not appear at all.

These flags may appear with BINDING:
- **ANNO**.  Has an annotation, other than annotating a parameter.
- **PARAM**.  Is a function parameter.
- **NESTED**.  Is a nested CLASS or FUNC name.
- **IMPORT**.  Bound by an `import` statement.

For convenience, certain combinations are defined:

- **EXTERN_BIND** = NLOC_DECL | GLOB_DECL
- **USAGE** = GLOB_DECL | NLOC_DECL | BINDING | USE | WALRUS | UNUSED
- **BINDFLAGS** = ANNO | PARAM | NESTED | IMPORT

NLOC_DECL and GLOB_DECL are mutually exclusive.  May be combined with USE and/or BINDING if the declaration occurs first, or if in GLOB.

In a COMP, combinations of BINDING and WALRUS are:
- BINDING.  A binding reference (an iteration variable).
- WALRUS.  A walrus target in the COMP subtree.
- WALRUS | BINDING. A walrus target in this COMP.  Can also be a walrus target in some descendant in the COMP subtree.

[^comp-walrus]: ### Walrus Items in a COMP
Any COMP has a [COMP owner](#scope-tree), or `COMP.comp_owner`.
Example.  
``` py
def f():                # FUNC, COMP owner of x and y
    [x for x in             # COMP, COMP owner is f
        { y for y in            # COMP, COMP owner is also f
            (lambda n:              # LAMB, COMP owner is NOT f
                [ z for z in [1] ]      # COMP, COMP owner is NOT f
            )(2)
        }
    ]
```
When an assignment expression (or walrus) appears in a COMP scope, the walrus.target.id item is owned by `COMP.comp_owner`.
Even though the walrus target is owned by COMP.comp_owner,
-  the target.id is defined as a **walrus reference** in this COMP and every scope in the COMP parent chain.  
-  the target.id is defined as a **binding reference** in this COMP.  
A walrus is a SyntaxError in certain situations (see [PEP 572](https://peps.python.org/pep-0572/#scope-of-the-target)):
-  the walrus scope is a CLASS.
-  the walrus < an iterable expression in a 'for' clause of *any* ancestor COMP.  This is true for a walrus within a non-COMP scope (i.e. a LAMB expression).
-  the target name is also a binding reference (an iteration variable) in this COMP or any COMP between it and the walrus scope.
Examples.  
``` py
class C():
    ## [x := y for y in [0]]   # SyntaxError.
    pass
def f():            # FUNC, walrus scope
    [
     x := y             # Sets x in f.
                        # walrus reference here
                        # binding reference here
     for y in
        ## [x := y for y in [0]]   # SyntaxError.
        [0]
    ]
    [y for y in []      # COMP
                        # x is walrus reference here
     if x in [
        [                   # COMP
         x := y             # Sets x in f.
                            # walrus reference here
                            # binding reference here
         for y in [0]
        ]
    [x for x in []      # COMP
                        # x is binding reference here
     if x in [
        [                   # COMP
         ## x := y              # SyntaxError
        ]
    ]
```

### Variable Type

There are three **types** of variables in a scope, distinguished by where the variable is resolved, denoted by [**scope.binder(var)**](#binder-scope), which is discussed later.  
The type is denoted **scope.type(name)**.

These types are members of `VarCtx`.  They are determined by the usage of `name` in `scope`, as well as in all ancestors of `scope`.

**scope.type(name)** is one or more of these bits.  It is based on `scope.binder(name)`:
- **LOCAL**.  binder is scope.
- **GLOBAL**.  binder is scope.glob.
- **FREE**.  binder is some other closed ancestor.
- **CELL**.  FREE and `name` is [captured](#CELL-Type-and-Captured-Variables).  Only in CLOS scopes.
- **UNRES**.  binder not found (applies to a nonlocal name with no matching closed scope).

These bits are mutually exclusive, except:
- in a GLOB, every `name` is both LOCAL and GLOBAL.
- in a CLOS, CELL can be combined with FREE.

For convenience, certain combinations are defined:

- **TYPES** = LOCAL | GLOBAL | FREE | CELL | UNRES
- **INLOCALS** = LOCAL | CELL.  Used in evaluating a locals() call.

## Variable Identity

A variable is uniquely identified, for a given reference by:
- Its name, or **var.name**.
- Its scope, or **var.scope**.  This scope is determined by the method [(reference.scope).binder(name)](#binder-scope), which is discussed in detail later on.

It can be written as **Variable(name, scope)**.  This produces the same Variable every time with the same arguments.

`scope.usage(var.name)` is always BINDING, and so `name` is always LOCAL in `scope`.  This means that scope is its own binder, i.e., scope.binder(name) is scope.

A fundamental concept is that any references which have the same name and binder **are the same variable**.  At runtime, any operations for a reference are immediately visible to all other references to the variable.

# Scope Name Resolution

At compile time, any reference `ref` is resolved by finding the scope **binder** = [ref.scope.binder(ref.name)](#binder-scope).  So the resolution of `ref` is Variable(name, binder).

At runtime, the operation for `ref` is performed on the Variable.  Binding references are always performed in the binder (actually, the namespace corresponding to binder).  Value references begin in the binder, but may actually get the value for name in some other namespace.

The method scope.binder(name) is discussed below, as is a helper method [scope.closure(name)](#closure-scope).  

## Binder Scope and Binding Variable

The **binder scope** of a name `name` in a scope `scope`, or denoted as **scope.binder(name)** [^binder-algo], is a scope, `binder`, where the name `name` would be resolved.  This may be None if, for example, `name` is declared nonlocal and there is no matching closed scope.

Plain **binder(ref)** means `ref.scope.binder(ref.name)`.

The **binding** for a name in a scope, or **scope.binding(name)** is a Variable, namely, `Variable(name, scope.binder(name))`.

Plain **binding(ref)** means `ref.scope.binding(ref.name)`.

Finding the binder is an iterative process which moves up the parent chain.  At each point, `binder()` operates with two variable mode flags, which are preserved during the iteration unless specifically changed:
- **skipclass**.  Initially false.  If true, then all CLASS scopes are bypassed. `scope.binder()` is delegated directly to `scope.parent`.
- **closure**.  Initially false.  This occurs when the name is declared nonlocal in some earlier scope (but not a CLASS which is bypassed).  The result must be a CLOS or None.

The binder depends on the scope kind and the usage of `name` in each scope.
- If scope.isGLOB, binder is this scope, or None if closure is true.
- If scope.isLOCS, see details [below](#LOCS-Scope-and-builtin-locals-function).
- If scope.isCLASS and skipclass is True, move to `scope.parent`.
- If usage is GLOB_DECL, move to the GLOB scope.
- In all other cases, set skipclass mode.
- If usage is NLOC_DECL, move to `scope.parent` setting closure mode.
- If usage is BINDING, binder is this scope.
- Otherwise, move to `scope.parent`.

[^binder-algo]: Algorithm for scope.binder(name, skipclass=False, closure=False).  
```py
    class Scope:
        def binder(self, name: str, skipclass=True, closure=False) -> Scope | None:
            return self._binder(name, skipclass=False)

        def _binder(self, name: str, skipclass=True, closure=False) -> Scope | None:
            if self.hasGLOB_DECL(name):
                return self.glob._binder(name, closure=closure)
            elif self.hasNLOC_DECL(name):
                return self.glob._binder(name, closure=True)
            elif self.hasBINDING(name):
                return self
            else:
                return self.parent._binder(name, closure=closure)
    class ClassScope(Scope):
        def _binder(self, name: str, skipclass=True, closure=False) -> Scope | None:
            if skipclass: return self.parent._binder(name, closure=closure)
            else: return super()._binder(name, init=True, skipclass=False, closure=closure)
    class GlobalScope(Scope):
        def _binder(self, name: str, skipclass=True, closure=False) -> Scope | None:
            if closure: return None
            else: return self
    class LocalsScope(Scope):
        def _binder(self, name: str, skipclass=True, closure=False) -> Scope | None:
            if self.parent.hasINLOCALS(name):
                return self.parent._binding(name, skipclass=False)
            else: return None
    class ExecEvalScope(Scope):
        def _binder(self, name: str, skipclass=True, closure=False) -> Scope | None:
            # Try LOCS base class first.
            result = super()._binder(name, skipclass=False)
            if not result:
                result = self.glob._binding(name)
            return result
```

## LOCS Scope and builtin `locals()` function

A call to [locals()](https://docs.python.org/library/functions.html#locals) in a scope creates a nested LOCS scope.  This scope has no actual AST source.

At runtime, `locals()` provides a dict which maps *some* names in the caller (the parent of the LOCS).  These names are those where: 
- `caller.binder(name)` exists, and
- `caller.hasINLOCALS(name)` is True.  INLOCALS is either LOCAL or [CELL](#CELL-Type-and-Captured-Variables).

`LOCS.binder(name)` gives the binder for any of these names, or None otherwise.  At runtime, the dict returned by `locals()` will map `name` to its current value if it currently has a value; otherwise `name` is not in the dict.  

LOCS uses its parent scope (the one in which `locals()` is called) to get the binder.  It returns `parent.binder(name)` if this binder exists, and if `name` is either LOCAL or CELL (see below) in the parent.

EVEX scopes are subclasses of LOCS, and their `binder()` method first checks the LOCS base class method, and if this is None, it will go to the GLOB scope.  
The algorithm is detailed here[^binder-algo]  
A possibly confusing runtime behavior is that if `name` is a INLOCALS in the parent, but it currently has no value in the binder scope, then evex() will use the global variable instead.  For example,
``` py
x = 0
def f():
    print(eval('x'))    # 0 because local x is unbound
    class C:
        print(eval('x'))    # 0 because f.x is unbound
    x = 1
    print(eval('x'))    # 1 because local x is bound
    class C:
        print(eval('x'))    # 1 because f.x is bound

```

## CELL Type and Captured Variables

The CELL type marks the name as a cell variable.  A list of cell variable names can be found in the `co_cellvars` member of the code object for the calling scope.  
There are no CELL variables in an OPEN scope.  
In a CLOS `scope`, `name` is CELL if
- it is FREE, and
- it is **captured** by the scope or any descendant scope.

    A scope, `scope2` captures `name` from `scope` if
    - `scope` >= `scope2`, and
    - `name` is FREE and USE in `scope2`,
    - `scope2.binder(name)` is identical to `scope.binder(name)`

    This is denoted by **scope.is_captured(name)**.  The method returns False if `scope` is OPEN.

    The algorithm is here[^is-captured-algo].

[^is-captured-algo]: Algorithm for scope.is_captured(name).
    ```py
    class Scope:
        def is_captured(self, name) -> bool:
            return self.captures(name, scope.binder(name))

        def captures(self, name, binder):
            if self is CLOS:
                if name is not FREE: return False
                if name is USE: return self.binder(name) is binder
            return any(child.captures(name, binder)
                for child in self.nested)
    ```

**scope.in_locals(name)** is part of the runtime behavior of the builtin [locals()](https://docs.python.org/library/functions.html#locals) function.  

This is important because `locals()` may be used by `evex()` as the mapping for local variables in the executed code.  

`in_locals(name)` is true if name is LOCAL.  
`in_locals(name)` is also true if name is FREE and
  - scope is CLOS,
  - and name in scope is captured by any descendant <= `scope`.  


### \_\_class__ and super Special Cases

The name '\_\_class__' is handled as a special case.  In a CLOS scope `s`, if its closure scope method reaches a CLASS scope `C`, then the closure scope is `C`, instead of `C.parent.closure(name)`.  This makes '\_\_class__' a FREE variable, whose value is the class `C`.

`s.in_locals(name)` operates in the usual way.  

Also, the name 'super' is handled as a special case.  In a CLOS scope `s`, if `super` appears in a value reference, 
then this is *implicitly also a value reference of '\_\_class__'* in `s`.

### Compiler Symbol Table

Most of the flags in the scope context are modeled closely, but not exactly, after the internal symbol table used by the compiler.

The library [**symtable**](https://docs.python.org/library/symtable.html) module is an implementation-independent view of the compiler symbol table hierarchy for a module, starting from the python text of the module.  This hierarchy consists of `SymbolTable` objects, and is parallel to the `Scope` hierarchy starting with a GLOB scope.  
`SymbolTable.get_children()` is a list of child `SymbolTable` objects in the hierarchy.  It is possible for several of these to have the same name.
`SymbolTable.get_symbols()` is a list of `Symbol` objects for identifiers appearing in the scope, including free variables which are used by free variables in any descendant scopes.  
The `Symbol` class corresponds to the context of its name in the scope.  It has a set of flag bits, which correspond (approximately) to flags in the context.  The correspondence is shown in the table below.  
`Symbol.get_namespaces()` is a sequence of internal symbol table objects.  They correspond to children of the parent `SymbolTable` which have the same name as the `Symbol`.  These internal objects are implemkentation-dependent.  Thus the only portable use of this method is to see how many of these there are.  One can get the child `SymbolTable` by filtering the parent's `get_children()' for a matching name.

| Context | Internal | Method | Notes |
|:--|:--|:--|:--|
| Uses... |
| USE | USE | is_referenced |
| GLOB_DECL | GLOBAL_EXPLICIT | is_declared_global |
| NLOC_DECL | DEF_NONLOCAL | is_nonlocal |
| BINDING | DEF_LOCAL | is_assigned |
| | DEF_BOUND | is_global | GLOB [1]
| | | is_local | GLOB [1]
| ANNO | DEF_ANNOT | is_annotated |
| PARAM | DEF_PARAM | is_parameter |
| | DEF_BOUND | is_global | GLOB [1]
| | | is_local | GLOB [1]
| IMPORT | DEF_IMPORT | is_imported |
| | DEF_BOUND | is_global | GLOB [1]
| | | is_local | GLOB [1]
| NESTED |  | get_namespaces | [2]
| Types... |
| LOCAL | LOCAL | is_local | [1]
| CELL | CELL | is_local | [1]
| FREE | FREE | is_free |   
| GLOBAL | GLOBAL_EXPLICIT | is_global | [1]
| | GLOBAL_IMPLICIT | is_global | [1]

Note, this is for the reference implementation, Cpython.  A different implementation, with its own compiler and `symtable` module, should have the same methods for `SymbolTable` and `Symbol classes`, but the methods could return different values, and the flag bits could be defined differently.

[1] 
At the module level, is_local() and is_global() are *also* True if any DEF_BOUND bit is present.  DEF_BOUND is defined as the union DEF_LOCAL | DEF_PARAM | DEF_IMPORT.  The other mentions of is_local() and is_global() apply to scopes at any level.

[2] `Symbol.get_namespaces(self, name)` returns a *list* of all internal namespace objects with that name.  More than one object is possible if there are multiple function and/or class definitions for the name in the enclosing scope.  The context NESTED bit is the same as `len(self.get_namespaces(name)) > 0`.

# Namespace

A **namespace** is a runtime concept, as opposed to a scope, which is a compile-time concept.  At all times, there is a **current namespace**.  Every namespace has both static and dynamic properties.

## <span id="namespace-static-state">Static State </span>

The static properties of a namespace are those which are unchanged at runtime, once the namespace is [created](#creation).  These include:
- [scope](#namespace-scope)
- [frame](#frame)
- [caller](#calling-namespace)
- [ancestors](#namespace-tree)

### <span hidden>Namespace </span>Scope

A namespace is associated with an AST scope.  There is a corresponding `Scope` object, designated as **namespace.scope**.  At runtime, the scope can be executed.  To enable the execution, the scope is compiled into a **code object**, designated as **namespace.code**, at some earlier time.

Several namespaces can have the same Scope and exist at the same time.

Various terms which apply to scopes also apply to a namespace via the namespace.scope.  For example, `namespace.hasBINDING("x")` means `namespace.scope.hasBINDING("x")`.

### Frame

The interpreter creates an internal [frame object](https://docs.python.org/3/reference/datamodel.html#frame-objects) when it creates the namespace.  This is denoted as **namespace.frame**.  
The code in the namespace may or may not have access to the frame.  It is implementation-dependent.  See [inspect module](https://docs.python.org/3/library/inspect.html#inspect.currentframe).  However, the following *might* work on all implementations:
```py
    try: raise Exception()
    except: frame = sys.exc_info()[2].tb_frame    # get from Traceback
```

### Calling Namespace

This is the current namespace in the interpreter at the time the given namespace is [created](#creation).  It is denoted **namespace.caller**.

The namespace and caller's frames are related by the `frame.f_back` attribute.  `namespace.frame.f_back` is `namespace.caller.frame`.  

A debugger will generally show the current namespace and its chain of callers in its call stack display.

Variables in the caller **are not visible** in the namespace, unless the caller is also its parent.

The ROOT namespace has no caller.

### Namespace Tree

Every namespace has a parent (except a special ROOT namespace which is the parent of all GLOB namespaces).

**namespace.parent** is the namespace which was current at the time the *namespace.code* was compiled.

**Important**: namespace.parent is *not necessarily* namespace.caller.  The latter relationship is shown in a debugger as next item in the call stack.  `(new namespace).frame.f_back` is `(caller namespace).frame`.

- With FUNC and LAMB namespaces, the function object is compiled from the scope at some earlier time.  The function can be stored somewhere and later called in a completely unrelated place.  Example [^namespace-parent].  When the function object is called, the new namespace.parent is the current namespace at compile time, and namespace.caller is current namespace at time of the call.

- With all other namespace kinds, the namespace.parent is identical to the current namespace.  This is because the namespace code is executed immediately after the code is compiled.

Multiple namespaces may exist, at the same time and/or at different times, for the same scope.  This can happen:
- When a function object is called multiple times.
- When two namespaces are created in the same namespace from the same scope (such as in a loop).
- When two namespaces are created in two namespaces which themselves have the same scope.

  If two namespaces have have a parent, or some other ancestor, in common, then it is possible for a variable to be **aliased** in the two namespaces.  It occurs if the variable's binding currently refers to the binding in the common ancestor (that is, the variable has no binding elsewhere in the parent chain which would hide it).  Here's an example [^binding-alias-example].

[^binding-alias-example]: Here the value of variable `x` is 1 when one would expect it to be 0, because `x` refers to the variable in the common parent `foo` which changes value.
```py
    def foo():
        ff = []
        for x in (0, 1):
                def f(): print(x)
                ff.append(f)
        ff[0]()                # prints 1, not 0.

    foo()
```

[^namespace-parent]: `a.func.parent` = `a.f`, even though `a.func()` was called during `b.g()`.
a.func() has access to captured variable `y` in `a.f()`, and global variable `z` in `a`.
```py
a.py:

# namespace a (GLOB)
# a.parent = ROOT
def f():
    # namespace f (FUNC)
    # f.parent = a
    global func
    y = 5
    def func(x):
        # namespace func (FUNC)
        # func.parent = f
        # call stack:   a.func
        #               b.g
        #               __main__
        print(x, y, z)
z = 6

b.py:

# namespace b (GLOB)
from a import func
def g():
    # namespace g (FUNC)
    # g.parent = b
    func(4)

main module:

# namespace __main__ (GLOB)
from b import g
g()             # prints "4 5 6"
```  

    The entire namespace tree during the execution of func(4) is:  
    - ROOT  
      - a  
        - f  
          - func  
      - b  
        - g  

Multiple namespaces may exist for the same scope at the same time.

### namespace.find_scope(scope)

The parent chain of a namespace corresponds to the (scope) parent chain of `namespace.scope`.  `namespace.parent.scope` is always identical to `namespace.scope.parent`.  And so on, up the parent chain.

For any scope `scope` that is in the parent chain of `namespace.scope`, **namespace.find_scope(scope)** means the corresponding namespace in the namespace parent chain.  `namespace.find_scope(scope).scope` is always identical to `scope`.

## Dynamic State

The dynamic state of a namespace is a mapping from variable names to possible values.

## Namespace Lifecycle

### Creation

The Python interpreter maintains a **current namespace**.  The interpreter executes the code for the current namespace.  This can be temporarily interrupted by changing the current namespace.

The interpreter creates a namespace from time to time, associated with a Scope.  
Whenever the interpreter creates a namespace, that becomes the current namespace, and it begins executing its code.  In some cases, some argument values may be provided.  
The namespace is related to an execution frame (see [Standard Type Hierarchy](https://docs.python.org/3/reference/datamodel.html#:~:text=frame%20objects)), which is the internal object created by the interpreter.  **namespace.frame** refers to this frame.

A namespace is created in the following ways:

- At the top level, by running the interpreter.  It takes python code in various ways, and creates a GLOB namespace.  This namespace is always called '\_\_main__'.  It creates a module, which is stored in `sys.modules[__main__]`  
- A GLOB is created for a named module by executing some form of an `import` statement.  Modules are cached in `sys.modules`, and so the GLOB is created and its code executed only the first time it is imported.
- A CLASS is created by executing a class definition.
- A FUNC is created when a user-defined function object is called, using the argument values in the call expression.  The arguments are evaluated at the time of the call.  
The function object itself was created earlier by executing a function definition (a `def` statement).  It has references to:
  - The current namespace when it was created.
  - The scope of the `def`.  This becomes namespace.scope for any namespace which is subsequently created.
  - The code object compiled.

  Multiple function objects can be created from the same `def` statement.  They each have separate creation namespaces and code objects, but they all have the same scope.
  
- Similarly, a LAMB is like a FUNC, except that it comes from a `lambda` expression instead of a `def` statement.
- A COMP is created immediately when a comprehension expression is executed.  A single unnamed argument is provided by evaluating the first iterable expression[^comp-first-iterable].
- An EXEC or EVAL is created immediately when a call is executed to the `exec()`, or `eval()` builtin.   
    Arguments to the this function are *not* execution arguments.  The first argument is compiled and is what is executed by the interpreter.  Any remaining arguments are incorporated into the namespace object to affect the evaluation of variable references.

[^comp-first-iterable]:  First iterable in a COMP.  

    When the interpreter executes a [comprehension expression](#scope-kinds), it evaluates its first iterable expression, as `iter` in `... for var in iter [... for var2 in iter2] ...`.  This value is used as a single unnamed argument for executing the comprehension.  
    In the Cpython interpreter, this argument called ".0".  This name cannot be used within the comprehension (it is not a valid identifier), but it can be retrieved as `locals()[".0"]`.  A debugger will also show ".0" as a variable.

## Binder Namespace for Variable

The **binder namespace** for a variable is the namespace which corresponds to its binder scope in the namespace's scope.

For any variable `var`, **namespace.binder(var)** = `namespace.find_scope(namespace.scope.binder(var))`.  That is, `namespace.binder(var).scope` is `namespace.scope.binder(var)`.

The variable `var` is always LOCAL in `namespace.binder(var)`.

All binding operations, and most (but not all) value operations, involving `var` are performed in namespace.binder(var).  The exceptions are noted where they occur.

### locals() Binder Namespace

**namespace.locals_binder(var)**[^locals-binder-algo] is part of the runtime behavior of the builtin [locals()](https://docs.python.org/library/functions.html#locals) function.  
This is important because `locals()` may be used by `exec()` or `eval()` as the mapping for local variables in the executed code.  
In an EVEX namespace, `namespace.parent.locals_binder(var)` is used in resolving `var`, when `locals()` is actually the local variable mapping.

The result is the same as `namespace.binder(var)` if `namespace.context(var)` has the CELL bit set, and None otherwise.

**namespace.locals_bindings** is a Bindings object for all vars which have the CELL bit set.

### Binding and Bindings

The state for a variable is represented by the class **Binding** in [namespaces.py](../scopetools/namespaces.py#:~:text=class%20Binding).  It is analogous to the internal python [cell object in User-defined functions](https://docs.python.org/reference/datamodel.html#the-standard-type-hierarchy).

A Binding is either
  - **bound**.  It has a value (any python object, including None).
  - **unbound**.  It has no value.

**Binding(value)** designates a `Binding` which is bound to this value.  
**Binding()** designates an unbound `Binding`.

**binding.value** is the stored value if it is bound, or raises ValueError if it is unbound.

**bool(binding)** is True if it is bound, False if it is unbound.

**namespace.bindings** is represented by the class **Bindings** in [namespaces.py](../scopetools/namespaces.py).  It maps var names to `Binding` objects

`Bindings` has these operations:
- **bindings[var]** -> `Binding`.  This is a `Binding` carrying the currently assigned value, or it is an unbound `Binding`.  It is valid for any `var`.
- **bindings.global_binding(var)** -> `Binding`.  This is similar to `bindings[var]`, except that it will also check for `var` being a builtin name [^global-binding-algo].  Only valid in a namespace.global_bindings object.
- **bindings[var] = value**.  Sets a value.  bindings[var] will now carry this value.
- **del bindings[var]**.  Removes the binding if there is one.  `bindings[var]` will now be `Binding.unbound`.  At runtime, deleting an unbound variable raises a NameError.

**namespace.binding(var)**, or **namespace[var]** is a `Binding` for `var` at the present time, equivalent to `namespace.bindings[var]`.  As the namespace code is being executed, this may change.  
The `Binding` can be bound if
- `var` is BINDING in namespace.scope and currently has a value, or
- for OPEN namespaces, if added to `namespace.bindings` without using a binding reference [^extra-bindings].

[^global-binding-algo]:
`bindings.load_global(var)` will try builtin names as a last resort.  `bindings` will always have the key '\_\_builtins__', possibly added by a call to `evex()`.  
`bindings['__builtins__']` is a dict object.  It is the dict of the `builtins` module, except possibly if `bindings` comes from an `evex()` call.
```py
def load_global(bindings, var: VarName) -> Binding:
    binding = bindings[var]
    if binding: return binding
    builtins = bindings['__builtins__']
    assert builtins
    if var in builtins:
        binding = Binding(builtins[var])
    return binding
```

### Befpre Executing the Namespace

When the namespace begins execution, it is given an initial state.  This is done *before* the namespace code runs.

1. For a CLASS, if its metaclass has a \_\_prepare__ method, this method supplies bindings, which can be whatever that method implements.

2. For some namespaces, a few special variables, such as `__name__` and `__module__` are bound.

3. If the scope is executed with arguments, the parameter names are bound to the corresponding values.
   - The iterable argument for a COMP is bound to a hidden name.  This means that the iterable is evaluated in the caller's namespace, but the iteration of its values occurs in the COMP code.

### After Executing the Namespace

GLOB and CLASS namespaces persist after the module or class code has run.  They are in the form of __dict__ attributes of the module or class object being created.  The binding for a variable becomes its attribute of the same name.  

### Local Variables and Bindings

A var is a **local variable** if it is LOCAL in namespace.scope.  Thus it is a static property.

The **local binding** of a var is a dynamic property, and is the current namespace.binding(var) value.

Normally, a var can have a local binding only if it is a local variable, because binding operations on a non-local variable take place in namespace.binder(var), which is a different namespace.

However, there are obscure ways [^extra-bindings] that a local binding can be changed other than by a binding reference in the namespace code.  This could result in a non-local variable having a local binding, or a local variable's local binding changing.  

For this reason, name resolution involves looking in namespace.bindings, even for a var that is not LOCAL.

[^extra-bindings]: Obscure ways that local bindings can be changed:
- A CLASS metaclass \_\_prepare__ method provides some initial bindings.
- A call to `exec()` with an assignment statement and default namespace arguments.  Only in *closed* namespaces.
- A dict of the current local bindings is obtained, and is at some later time modified.  It is obtained by
      - Calling the builtin locals() function, or
      - Getting the current frame object, via `sys._getframe()` or `inspect.stack()`, and using the frame.f_locals.  

  The result is implementation dependent behavior, but is expected to be standardized in future Python versions.  [PEP 558](https://peps.python.org/pep-0558) and [PEP 667](https://peps.python.org/pep-0667) are converging and expected to be adopted.  
          With this convergence, the behavior will (presumably) be:
      - locals() in a closed namespace will be a **copy** of the local bindings at the time of call.  Changes to locals() **will not** affect namespace.bindings, and *vice versa*.
      - locals() in an open namespace is identical to the namespace.bindings, and all updates to either are reflected immediately in the other.
      - frame.f_locals *may not be available* because it is dependent on the Python runtime implementation whether or not frames are available.
      - frame.f_locals, *when available*, is tied to the namespace.bindings for both closed and open namespaces, and all updates to either are reflected immediately in the other.

    Note: If you have a code analysis application, which tracks the changes to a namespace as its code is executed, then in any of the above situations, the corresponding update to the namespace must be performed

    Example:
```py
def f():
    x = 1
    class C:
        nonlocal x
        print(x)                        # 1
        x = 2; print(x)                 # 2 (f.x)
        locals()['x'] = 3; print(x)     # 3 (C.x)
        x = 4; print(x)                 # 3 sets (f.x), use (C.x) 
        del locals()['x']; print(x)     # 4 No (C.x), use (f.x)
        locals()['x'] = 5; print(x)     # 5 (C.x)
    print(x)                            # 4 (f.x)
    return C

C = f()
print(C.x)                              # 5

```

### locals() and globals() Bindings

**namespace.locals_binding(var)** is a `Binding` that reflects the dict returned by the builtin `locals()` at the time it is called.  

In an OPEN namespace, this is identical to `namespace.binding(var)

In a CLOS namespace, this is:
- `namespace.binding(var)` if `var` is LOCAL,
- `namespace.binder(var).binding(var)` if `var` is both FREE and CELL,
- or an unbound `Binding` otherwise.


**namespace.locals_bindings()** is a Bindings that reflects the dict returned by the builtin `locals()` at the time it is called.  It maps `var` to `namespace.local_binding(var)` for every `var` where this is bound.

The builtin `globals()` corresponds to `namespace.glob.locals_bindings()`.  

The semantics of `locals()` depends on the kind of caller namespace involved, and this affects the resulting Bindings object.

- OPEN.  `locals()` produces the *identical* dict to that which is used for local variables in the caller.  Therefore, any stores or deletes performed in the Bindings will be immediately visible in the namespace, and *vice versa*.  
While initializing a module, the module object is available in `sys.modules` and its attributes reflect the current Bindings.  This remains true after the module's body has finished initialization.  
After executing a CLASS def body, the final state of its local variables is *copied* to a new mapping, which serves as the class attributes dict.  At this point, the class attributes and the Bindings object are no longer linked to each other.

    `namespace.locals_bindings()` is identical to `namespace.bindings`.

    Examples [^open-locals-examples].
[^open-locals-examples]:
`locals()` in CLASS is same dict as the local variables (but no free variables),
and at the end of the CLASS code, this is copied into the class dict.

    ```py
    x = 0
    def f():
        x = 1
        class C:
            loc = locals()
            assert 'x' not in loc   # Not yet bound
            assert x == 1           # Not yet bound, use free x 
            assert eval('x') == 0   # Not yet bound, use global x
            loc['x'] = 42
            assert x == 42          # Now bound, use local x 
            assert eval('x') == 42  # Now bound, use local x
        return C

    C = f()
    assert C.x == 42
    assert C.loc['x'] == 42
    C.loc['x'] = 43
    assert C.x == 42        # C.x unchanged
    ```

    In a module suite, locals() is same dict as local variables of the namespace, and is the same as the module's attributes (even while running the suite).  After the suite is complete, the dict is still the same as the module's attributes.
    ```py
    # m.py:

    loc = locals()
    assert globals() is locals()
    assert 'x' not in loc
    import m as m2          # m2 is same as the m being initialized.
    loc['x'] = 42
    assert x == 42          # Now local
    assert eval('x') == 42  # Now local
    assert m2.x == 42       # Now module attribute
    ```

    ```py
    import m
    assert m.x == 42       # Now module attribute
    m.loc['x'] = 43
    assert m.x == 43       # Module attribute changed
    ```

- CLOS.  The behavior is implementation-dependent with respect to modifications to the dict returned by `locals()`.
    - Changes to locals() may or may not be visible in the namespace.
    - Changes in the namespace may or may not be visible in locals().
    - locals() may or may not be the identical dict as another locals() in the same namespace.

    See discussion of current CPython behavior and possible future standardization of the behavior [^closed-locals-implementation].

    To be safe from implementation dependencies, a Python program should make a copy of any `locals()` dict, and should not try to modify variables using `evex(code)` with no other arguments.  

    Examples [^closed-locals-examples].

[^closed-locals-implementation]:

    CPython behavior in a CLOS namespace:
  - `locals()` always returns the same dict object, `d`, in the same namespace.  Therefore, `d` will always be the same as that returned by the most recent `locals()` call.
  - `d` is updated by each `locals()` call to reflect the bindings of all CELL vars in the namespace.  It maps `var` to `(b := namespace.binding[var]).value` if `b` is bound. The key `var` is absent if `b` is unbound.  Thus a `var` can be added, or its value changed, or deleted.
  - Any changes to `d` made by the caller (regarding CELL vars) are lost as a result of a subsequent `locals()`.
  - Any other keys added to `d` by the caller will remain there after a subsequent `locals()`.
  - Changes to `d` are not visible in the namespace.

  The behavior is expected to be standardized in future Python versions.  [PEP 558](https://peps.python.org/pep-0558) and [PEP 667](https://peps.python.org/pep-0667) are converging and expected to be adopted.  
  With this convergence, the behavior will (presumably) be that
  - locals() produces a *copy*, `d` of `namespace.locals_bindings()` at the time of the `locals()` call.  This is the sme as current CPython behavior,  except that the contents of `d` are not affected by later `locals()` in the namespace.
  - Any changes to `d` made by the caller not visible in the namespace, nor in any other dict returned by `locals()`.
  - Any changes in the namespace are not visible in `d`.

[^closed-locals-examples]:
locals() in a FUNC has all LOCAL and FREE variables that are currently bound.  Changes to it are not copied back to the namespace.
    ```py
    x = 0
    y = 0
    def f():
        x = 1
        y = 1
        def g():
            loc = locals()
            assert 'x' in loc
            assert x == 1           # Not bound, use x in f()
            assert eval('x') == 1   # Not bound, use x in f()
            loc['x'] = 42
            assert x == 1           # Unchanged
            assert eval('x') == 1   # Unchanged
            assert eval('y') == 0   # Not in locals(), use global
            return loc
        g()

    f()
    ```

## Namespace Name Resolution

The term **name resolution** means performing certain **variable operations** with a namespace and a var name.  All operations involve a [reference](#references-and-declarations) to a `var` name.

The variable operations are:

- **namespace.load(var)** -> Binding.  Results from any [value reference](#value-reference) to `var`.  *Not always the same* as namespace.binder(var)[var].  
    This is `(b := namespace.load_binding(var)).value` if `b` is bound, otherwise it raises an [exception](#namespace-resolution-exceptions).
- **namespace.store(var, value)**.
    This always operates on the binding namespace.  Executes `namespace.binder(var).bindings[var] = value`.

    The store is a result of any [binding reference](#binding-reference) to var, except when delete() is called (see following).

- **namespace.delete(var)**.
    This always operates on the binding namespace.  Executes `del namespace.binder(var).bindings[var]`.  
    Note, if var is *already unbound*, then it raises an [exception](#namespace-resolution-exceptions).

    The delete may occur in two places:
    - a target name in a `del` statement.
    - at the *end* of an `except ... as var:` clause, *if* the handler is executed.  
        Note that `var` is bound to the exception object at the start of the handler, so the delete will succeed (unless if it was deleted in the handler code explicitly).

Helper properties and methods:

- **namespace.load_binding(var)** -> Binding.  The Binding holding the current value, or Binding.unbound.  It varies with the type of the namespace and the context of the var.
The algorithm is here[^binding-algo].

[^binding-algo]: Algorithm for namespace.load_binding(var):
- if a CLOS namespace:
      - return namespace.binder(var)[var].
- If a CLASS or EVEX namespace, this depends on which context the variable is.
      - if usage is GLOB_DECL, return namespace.global_binding(var).  Note, type can be GLOB without usage being GLOB_DECL.
      - check namespace[var].  If this is bound, return it.  
        Note that if var is not LOCAL, it is still possible for var to be bound, in special circumstances [^extra-bindings].
      - if type is LOCAL or GLOBAL,
        - return namespace.global_binding(var).
      - if type is FREE,
        - return namespace.free_binding(var).
- If the GLOB namespace:
      - return namespace.global_binding(var).

- **namespace.global_bindings** -> Bindings.  Used for lookup of  `var` as a global variable.  Same as `namespace.glob.bindings` except in an EVEX.
- **namespace.global_binding(var)** -> Binding.  Lookup of `var` as a global variable.  Same as `namespace.global_bindings.global_binding(var)`.

- **namespace.free_binding(var)** -> Binding.  Lookup of `var` as a free variable.  Same as `namespace.binder(var)[var]` except in an EVEX, it is `namespace.free_bindings[var].

### Resolution for eval() and exec()

Any call to [eval](https://docs.python.org/library/functions.html#exec) or [exec](https://docs.python.org/library/functions.html#eval) creates an EVAL or EXEC Namespace, *resp.*, which is immediately executed.  The term **EVEX** refers to this Namespace.  
There are special rules for `EVEX.load_binding()`.

The term **caller**, or **caller namespace** is the namespace which is currently being executed when the call to `evex` occurs.  This is same as EVEX.parent.

`evex` is called with these arguments:
- **code**.  What is being evaluated or executed.  Either an internal `code` object, or a string (or bytes) which is compiled to provide a `code` object.
- **globs**.  A dict to be used to resolve global variables.  May be [modified](#builtins-for-evex).
- **locs**.  A dict (or any other mapping object) to be used to resolve local variables.  All binding operations in `code` are made here.
- **closure = None**.  Keyword-only argument, which provides bindings for FREE variables in the `code`.  It is required if `code` has any free variables.

These arguments have defaults, as follows:
- `evex(code)` is `evex(code, globals(), locals())`.
- `evex(code, globs)` is `evex(code, globs, globs)`.  `globs` is evaluated only once.
 
Either `globs` or `locs` may come from a `locals()` or `globals()` call.  The call may have been made in the caller namespace at the time of the `evex()` call, or it may have been made at some earlier time (possibly in a different caller namespace) and stored somewhere.  

A call to `globals()` in any namespace is equivalent to a call to `locals()` in `namespace.glob`.

**EVEX.global_bindings**, **EVEX.bindings** and **EVEX.free_bindings** are `Bindings` objects representing the actual `globs`, `locs`, and `closure` arguments to `evex()`.  `EVEX.global_bindings` and `EVEX.free_bindings` are used by `EVEX.load_binding()`.

#### Builtins for evex()

Whenever `evex()` is called, the `globs` argument is checked.  If it doesn't have a key '\_\_builtins__', then this key is inserted into `globs` with the value being the `__dict__` of the `builtins` module.  This key is visible in the EVEX.globs bindings.  
The reason for this is to allow the caller to `evex()` to supply an alternative builtins mapping, while using the `builtins` module by default.  
Note: *the key '\_\_builtins__' remains inserted in the dict* given as the `globs` argument during and after the `evex()` call.

### Namespace Resolution Exceptions

An exception raised by `namespace.load(var)` or `namespace.delete(var)` is
- `UnboundLocalError`, if `var` is LOCAL in `namespace`.
- `NameError`, otherwise.

These occur when var is currently unbound.

# Summary of Rules

Here's how to determine the meaning of an identifier, **`var`**, in the AST tree.

First, be sure it's really a variable, rather than something else[^non-variables].

If `var` is a [**private name**](#private-name-mangling), replace `var` with its mangled name.

Identify the [**owner**](#scope-owned-items-and-item-owner-scopes) AST scope, usually the nearest scope containing the identifier, but sometimes something else further up the parent chain.  This requires analysis of the entire AST of the scope and all of its parent chain.

Identify the [**binder**](#binder-scope) AST scope.

The static (compile time) meaning of `var` is the name `var` in scope `binder`.

The dynamic (runtime) behavior is described [here](#namespace-name-resolution).  
