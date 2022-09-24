# Scopes in Python Code

This document describes how a Python module is composed of various **scopes**, some of which may be **nested** in larger scopes.

It also describes classes which represent scopes and how they form a tree structure.

# Syntax Tree

A **syntax tree** is a representation of the program text of a module or expression, which is produced by the `ast.parse()` method.  Refer to [ast documentation](https://docs.python.org/3.10/library/ast.html#module-ast) for complete details.

A **node** is an object which is a subclass of `ast.AST`.  In this document, **AST** is shorthand for any `ast.AST` node.  
An AST has some [**child**](#ast-child-objects) objects, some of which can be other ASTs.  A non-AST child is called a **leaf**, or **AST leaf**

An **item**, or **AST item**, is either a node or a leaf.

Each item represents a single contiguous section of the text.  Children of a node represent subsets of that section of text.  Some node classes have attributes (which are not child items) showing the range of the text.

A Python module is considered to be the same as an `ast.Module` tree.  In this document, the program will be described in terms of ASTs in the syntax tree.

The code in this `scopetools` package does not require that there be an actual AST tree, or a module file which would be parsed into one.  An application is only required to build a Scope tree as though there is an actual AST.  There are examples of programs which build a scope tree without an actual syntax tree.

## Inclusion

As a shorhand notation, for any `node` and `item`, **`node` > `item`**, or **`item` < `node`**, when `item` is a descendant of `node`.  Likewise, **`node` >= `item`**, or **`item` <= `node`**, which means that (`node > item or node is item`).

## Scope AST and Program Structure

Refer to sections [4.1](https://docs.python.org/3.10/reference/executionmodel.html#structure-of-a-program), [4.2](https://docs.python.org/3.10/reference/executionmodel.html#naming-and-binding), and [6.2.1](https://docs.python.org/3.10/reference/expressions.html#atom-identifiers) of the language specification for an introduction to the basic concepts.  A scope is a code block.  For any given name, the scope may extended to include certain nested code blocks, in which the name refers to that name in the outer scope block.

I think it is simpler to treat the scope as a set of names and their 
meanings.  A name is either a local variable (resulting from some name binding operation in that block) or an alias for that name in an enclosing scope.

What the documentation does not mention is that:
- Lambda and comprehension expressions are also blocks, as they are "executed as a unit."
- Any code in a class or function definition statement *other than* the statements in the body and the formal parameters to functions, is part of the outer scope where the definition statement appears.
- The leftmost iterable expression in a comprehension is *not* evaluated in the comprehension.  It is part of the outer scope where the comprehension appears.
- An assignment expression can bind the target name in the scope if it appears nested in a series of comprehensions.  Examples:  
    `[x for x in range(3) if x in [name := y for y in range(3)]]` evaluates to [0, 1, 2] and sets `name` = 2 in the current scope.  
     `[x for x in range(0) if x in [name := y for y in range(3)]]` evaluates to [] and does not modify `name` in the current scope.  However, this is still a binding operation for `name`.  
    `[x for x in [y for y in range(3)] if (lambda: (name := x))()]` evaluates to [1, 2] but does not set `name` at all in the current scope, and is *not* a binding operation.  The `name := y` sets a local variable `name` in the lambda expression.

- private names in a class are transformed *only* within the class body.  To use the name in any other context, such as `C.name` or `getattr(C, name)` the program must [provide or compute the transformed name](#transforming-private-names) and use that instead of `name`.

A **scope AST** is an instance of one of a few specific AST subclasses.

A **scope kind** is an [enum](#kind-enum) which corresponds (except for ROOT) to one of these scope AST classes.

|    kind      |  AST class | Python code |
|:-------------|:-----------|:--
|ROOT | | container for GLOBs or other ASTs
|GLOB|   ast.Module | entire module
|CLASS|   ast.ClassDef | `class` statement with decorators
|FUNC|   ast.FunctionDef |`def` statement with decorators
|LAMB|   ast.Lambda |`lambda` expression
|COMP|   ast.ListComp |`[expr for var in iter ...]`
|...|   ast.SetComp |`{expr for var in iter ...}`
|...|   ast.DictComp |`{key : expr for var in iter ...]`
|...|   ast.GeneratorExp |`(expr for var in iter ...)`

For brevity, any of these kind names can be used to mean an `AST` having that kind.

## Scope Nesting

Only certain kinds of scopes can be children or parents of other kinds of scopes.  These are the possible combinations:

| Kind | Parent | Child | Items |
|:---|:---|:---|
| ROOT | (none) | GLOB | module
| GLOB | ROOT | CLASS, FUNC, LAMB, COMP | statement, expression
| CLASS, FUNC | GLOB, CLASS, FUNC | CLASS, FUNC, LAMB, COMP | statement, expression
| LAMB, COMP | GLOB, CLASS, FUNC | LAMB, COMP | expression

Just as `ast.parse()` can also parse a single python expression or statement, a tree can be constructed in this package starting from one of these.  However, to maintain uniformity of structure, GLOB or ROOT tree objects will be inserted into the hierarchy, so that the tree object can have global variables and names that are only in the `builtins` module.

## Scope AST Items
The Python compiler considers each syntax item to belong to a particular scope AST.  This can be written as **scope -> item**, or the scope **owns** the item.

The item is always part of the tree starting with the scope AST.

However, not all such items are owned by it.

### Direct Items

Certain items in a scope AST are classified as **direct items**, and notated as **`scope` ->> `item`**.  They are listed in this table:

| kind | item | location
|:--|:--|:--|
| GLOB | statement | scope.body[:]
| CLASS | statement | scope.body[:]
| FUNC | statement | scope.body[:]
| | argument | [scope.args.*](#FUNC-and-LAMB-arguments)
| LAMB | expression | scope.body
| | argument | [scope.args.*](#FUNC-and-LAMB-arguments)
| COMP | everything **except** | 
|  | first iterable | scope.generators[0].iter
| Not COMP | walrus target | [see below](#owned-comp)

### All Items

**`scope` -> `item`** if:

1. `scope` is a scope AST instance.
2. `scope` ->> `dir` >= `item`, for some direct item `dir`, or `scope` is `item`.
3. There is no other scope AST instance `scope2` such that `scope` > `scope2` ->> `item` (defined recursively).  Note, `item` can be another scope AST.  

In other words, a scope contains all direct items, plus all of their descendants, minus any other scope's items.

In this way, every AST item in the program is owned by exactly one scope.

## Class Scope of an Item

The **class scope** of an item, if any, is the nearest CLASS in the chain of owner scopes.  
More precisely, `scope` is the class scope of `item` if either
- `scope` is a CLASS and `scope` -> `item`,
- or `scope` is the class scope of the owner of `item`.

An item will have no class scope if its owner is the GLOB, or if its owner has no class scope.

This concept is applicable for [private names](#private-name-mangling).

# `ScopeTree[TreeT, SrcT]` Class

This is defined in [scope_common.py](../scopetools/scope_common.py).  It is a base class for `Scope` in `scopes.py`, `Namespace` in `namespaces.py`, and any custom classes an application may define to follow the syntax tree structure.

The term **tree** means any `ScopeTree` instance.

`ScopeTree` is a Generic class, with these type variables:
- **`TreeT`**, base class for the particular object, a subclass of `ScopeTree`.  That is, `Scope` or `Namespace` or whatever.  This is also known as a **tree type**.  **`tree.tree_type`** is a class variable == `TreeT`.  (Note, the `ScopeTree` class itself is never instantiated.)
- **`SrcT`**, which denotes the class of a ["source"](#tree-source) object.

## Tree Source

Every tree has a **source**, stored in `tree.src`, which is sufficient to specify the contents of the tree (that is, attributes of the tree and any nested subtrees).

A source has its own tree structure.  It has some method (which varies by `SrcT`) of iterating over **child sources**.  The notation **`source` -> `child`** means that `child` is one of the child sources.

When `SrcT` is `ast.AST`, then the source is the actual ast scope object.  Otherwise, it is something which is equivalent to an AST, as interpreted by an application (for example, [scopestest.py](../scopetools/scopestest.py).  All source objects must be distinct objects, although they may compare equal.

## Tree Structure

Every `tree` corresponds to an AST scope, **`tree.ast`**.  The attribute `tree.ast` doesn't actually exist.  It is just for purposes of documentation.  When `SrcT` is `ast.AST`, `tree.ast` is the same as `tree.src`.

Every tree has a **parent** tree (except for a ROOT tree).  Parents of trees correspond to parents of the ast nodes.  That is, `tree.parent.ast` is the same as `tree.ast.parent`.

A tree has (potentially) a set of **child** subtrees.  For any child source `child_src`, where `tree.src` -> `child_src`, `tree` has 0 or more child trees, `child_tree`, where `child_tree.src` is `child_src`.  
When a child tree is created, the parent tree *may* keep a record of the child.  The recorded children are found in the list `parent.nested[child source]`.

A **Scope tree** (where `TreeT` is `Scope`) has exactly one recorded child for each child source.  These are recorded in the same order as the `child.ast`s appear in `parent.ast`.  Thus it exactly parallels the scope AST tree structure of the module AST.

## `TreeT` Subclass of `ScopeTree`

The type variable `TreeT` is a direct subclass of `ScopeTree`.  All objects in the tree structure are instances of `TreeT`.
The class variable `TreeT.tree_type` == `TreeT`  

### Kind-specific Subclass of `TreeT`

A subclass `K` of `TreeT` may be defined for all trees with Kind `kind`.  It will have a class variable `K.kind` == `kind`.
If a custom `TreeT` is defined by an application, it must be defined using  
`class K(TreeT or subclass of TreeT, kind=kind): ...`.

## Tree Scope
Every tree is associated with a `Scope` object, which specifies the actual or hypothetical scope AST.  It is stored in `tree.scope`.
When `TreeT` is `Scope`, then `tree.scope` is `tree` itself.
Otherwise, it is determined by the constructor from other parameters.

## Tree Constructor

All trees are created by  
`T(src: SrcT, parent: TreeT = None, kind: Kind = None, *args, **kwds)`
- `T` is some subclass of `TreeT`
- `src` is the source object.  For any given `parent`, all `src` objects must be distinct objects.
- `parent` is the parent tree, except for a ROOT.  
- `kind` is the kind of the result, or `T.kind` if this is defined.
For a Scope tree (`TreeT` is `Scope`):

+ additional arguments are:
    + `name` is optional name, but required for CLASS and FUNC.

  `tree.scope` = tree  
  `tree.nested` = an empty mapping.  It becomes populated later as subtrees are created.

For other tree types:

+ Find `scope` which is a child of `parent.scope` that matches `src`.    
+ `tree.scope, tree.name, tree.src = scope, scope.name, scope.src`.
+ `tree.nested` = a mapping `{id(src): `[`NestInfo`](#nestinfo-class)(src)` for src in scope.nested}.  That is, there is a slot for each possible source for a subtree.


The tree might be an instance of some subclass of `TreeT` ...

- If there is a subclass `K` corresponding to `tree.kind` as mentioned above, the tree is an instance of `K`, with class attribute `K.kind` == `kind`.  
- Otherwise the tree is an instance of `TreeT`, with instance attribute `tree.kind`.

In all cases, `tree.kind` is `kind`

## Tree Scope

Every tree has a corresponding `Scope` object, stored as `tree.scope`.  When `TreeT` is `Scope`, then `tree.scope` is `tree` itself.  For other `TreeT` types, tree.scope is a separate `Scope` object; the constructor finds the scope object from the `parent` and `src` parameters.

The scope provides a source for the tree.  `tree.src` is an alias for `tree.scope.src`.

The parent chains of `tree` and `tree.scope` are exactly parallel.  `tree.parent.scope is tree.scope.parent`.

## `ScopeTree` Variables
- `kind`: `Kind`.  An instance attribute, or a class attribute for the actual object class if it has one.
- `name`: `str | None`.  Required for CLASS and FUNC, otherwise optional.
- `parent`: `ScopeTree | None`.  Required except for ROOT.
- `scope`: `Scope`.  A scope object associated with this object.  In the `Scope` `TreeT`, it is a reference to itself.
- `src`: `SrcT`, used to populate the tree.
- `nested: Mapping[int, `[`NestInfo`](#nestinfo-class)]`]`, nested sub-trees, corresponding (in order) to children of `src`.  Indexed by the id() of the child source.

## Tree State Methods

There are many methods defined by `ScopeTree`.  **Setters** alter some aspect of the state of a tree, corresponding to something in the `tree.ast`, and **getters** make inquiries about the current state.

  Some of these methods are implemented only by some tree types; in other tree types, they are ignored and return None.

The **tree state** is composed of a number of items, arranged in a number of categories...
- **Static state**.  Setters only apply to Scope trees.  Static properties are aspects of a Scope which are determined at compile time, such as how to interpret a variable name.  Refer to [scopes.md](scopes.md) for details.  Non-Scope trees will delegate the getters to the `tree.scope` object.  
- **Dynamic state**.  These apply mainly to Namespace trees and are ignored by Scope trees.  Dynamic properties are aspects of the object which change at runtime, such as the value of a variable, or child trees.  Refer to [namespaces.md](namespaces.md) for details.
- **Typing state**.  These only mainly to Typing trees and ignored by Scope trees.  This records static typing information associated with names.  A type checker might make several passes over a module, or a set of modules, and accumulate information.  Refer to [typing.md](typing.md) for details.

### Note for Scope trees
All setters for nesting and static state must be called while "building" the Scope object, in the same order in which the corresponding ASTs are found in the `tree.ast` tree.  After this, all Scope trees are immutable.

### Private Name Mangling
In a class, the compiler considers certain variable names as "private" to that class, by transforming them to a different name which is (usually) different from the same name in a different class.  For details see [below](#transforming-private-names).

Note, these names include those found in other non-CLASS enclosed scopes.

This is specified by a method  
 **`scope.mangle(var: str) -> str`**.

- If `scope.kind` is CLASS and `var` is a private name, it returns the transformed name, using the name of the CLASS.
- If `scope` is the GLOB scope, it returns `var` unchanged.
- Otherwise, it returns `scope.parent.mangle(var)`.

All of the nesting and state info (both setter and getter) methods call `tree.scope.mangle`() on all variable names and for all tree types.  If the name is already mangled, there is no change because mangled names are not subject to mangling.  Mangling can be suppressed with a `nomangle=True` argument to the tree method.

- Usually, this takes care of everything.  However, if an application needs to access a private class or instance variable *outside the class definition*, that is, when the class scope is not the class scope of the variable, then it must provide the mangled name for the variable, possibly by calling `tree.mangle(var)` on a CLASS tree for the scope in question.

# Creating and Building a Tree

See [treebuild.md](treebuild.md) for this information.


# Notes
These sections provide details for some things mentioned above, so as to keep this document easier to read.

## AST Child Objects

The children of an AST node are found by looking at the class attribute `node._fields`, which is a tuple of attribute names.  Some nodes have other attributes that are not fields, and these are ignored.  
The [ast grammar](https://docs.python.org/3.10/library/ast.html#abstract-grammar) shows the names and types of fields of each AST node class, in the form `class(field, ...)`.  For each `field` the node has 0 or more child objects, depending on the coding of `field` as shown in this table.  `T` is the type of the child.  `value` is the value of `node.name`.

| field | value type | children |
|:-|:-|:-|:-
| T name | T | [value]
| T? name | T \| None | filter(None, [value])
| T* name | list[T] | value[:]

## `Kind` enum
`ScopeTree.Kind` is an `enum` class which distinguishes different instances from each other, as well as `ROOT`, which represents a container for other objects.  The correspondence is shown in the table [above](#Scope-AST-and-Program-Structure)
The elements of this enum are also defined as attributes of `ScopeTree`.  For example, `tree.GLOB` is `tree.Kind.GLOB`.
All trees have a `kind` attribute.  Depending on the type TreeT, it may be provided to a TreeT() constructor, or it may be a class attribute of a subclass of TreeT.

The value of each member of `Kind` is a string which can be used to create the name of a corresponding class or attribute.  The method `kind.make_name(template)` can be useful for this.  For example, `Kind.GLOB.make_name('%sScope')` gives 'GlobalScope'.
## `NestInfo` class
`ScopeTree.NestInfo` describes subtrees of a tree having a common source.  They are elements of `tree.nested`, in the same order as the children of `tree.src`.  It has attributes:
- `src`: `SrcT`, a child of `tree.src`.
- `nested`: `Iterable[TreeT]`, the children of `tree`, if any, having this `src`.

## FUNC and LAMB arguments

In the [above table](#direct-items), **`scope.args.*`** is a collection of items, which comprise all the arguments to a function or a lambda.  They include the argument name.  In a function, they also include any annotations or type comments.
The items are:
- scope.args.posonlyargs[:]
- scope.args.args[:]
- scope.args.vararg
- scope.args.kwonlyargs[:]
- scope.args.kwarg

## Owned COMP

For the purpose of explaining the behavior of assignment expressions in a COMP...  
For two scopes `owner` and `comp`, `comp` is an **owned comprehension** of `owner` if:
- `owner` >= `comp`
- `comp` is a COMP
- for any `other` scope, where `owner` > `other` > `comp`, `other` is also a COMP.

Note that a COMP is an owned COMP of itself.

In addition, if `owner` is not a COMP, then `owner` is **the owner of** `comp`, or `owner` ->> `comp`.  Any COMP has exactly one owner.  `comp` is the direct item of `owner` mentioned in the [table above](#direct-items) as a "walrus target".  
Example:
``` py
def f():                        # FUNC owner
    [x for x in                    # COMP owned by owner
        { y for y in                   # COMP also owned by owner
            (lambda n:                      # LAMB NOT owned
                [ z for z in [1, 2, 3] ]       # COMP NOT owned
            )(2)
        }
    ]
```

## Transforming Private Names
This is described in [Language doc 6.2.1](https://docs.python.org/3.10/reference/expressions.html#atom-identifiers), in the section "**Private Name Mangling**".

Note some **exceptional cases** below.

Everywhere within the body of the `class` statement, the compiler generates the code using the transformed name.  If the transformed name appears in place of the private name, the compiled result is the same.  Please note that the transforming also applies to a name declared global or nonlocal.  
More precisely, this occurs when the [class scope](#class-scope-of-an-item) for the name item is that `class` statement.  So it includes any descendant non-CLASS scopes, and excludes the body of any descendant CLASS scope.
*Anywhere else*, if a program wants to access an attribute of a class or instance with a private name, it must use the transformed name, as described.

As an example,
```py
class C:
    __loc = 3
    global __glob
    __glob = 13
    print(__loc)       # 3    
class D(C):
    __loc = 4
    global __glob
    __glob = 14
    print(__loc)       # 4
print(C._C__loc)       # 3
print(D._D__loc)       # 4
print(D()._C__loc)     # 3
print(D()._D__loc)     # 4
print(_C__glob)        # 13
print(_D__glob)        # 14
```

### Very Long Names

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
This is implemented in the method **`scope_common.ScopeTree.mangle(name: str) -> str**, and can be called on a tree object of any kind and any tree type.

I have created an [enhancement proposal](https://github.com/python/cpython/issues/95621) for cpython to provide this functionality in the language.  Please feel free to read this and comment on it.

### Walrus in a COMP with a global variable
There is a bug in the cpython compiler, in a case such as this:
```py
class C:
    (possibly some more nested functions ...)
    def f():
        global __x
        [__x := 1 for ...]
```
The compiler ignores the global `__x` and tries to resolve the *unmangled* name `__x`, resulting in a SyntaxError.
The workaround is to figure out the mangled name and use this in the walrus, as:
```py
        [_C__x := 1 for ...]
```
The `scopetools` module does this in the Python code that it generates.

See [bug report](https://github.com/python/cpython/issues/96497).
