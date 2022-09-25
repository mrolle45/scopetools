# Python Name Resolution Rules

This document specifies the complete set of rules for resolving a name (an identifier) at runtime in a running Python program, and getting, setting, or deleting its current value.

# Table of contents

- [Syntax Tree](#syntax-tree)
- [Variable](#variable)
  - [Private Variable Name Mangling](#private-variable-name-mangling)
- [Scope](#scope)
  - [Closed and open scopes](#closed-and-open-scopes)
  - [Scope Kinds](#scope-kinds)
  - [Scope Owned Items and Item Owner Scopes.](#scope-owned-items-and-item-owner-scopes)
  - [Items Not Owned by Scope](#items-not-owned-by-scope)
  - [Item CLASS Owner Scope and CLASS Class Items](#item-class-owner-scope-and-class-class-items)
  - [Scope Tree](#scope-tree)
  - [Owned COMP of a Scope and COMP Owner Scope of a COMP](#owned-comp-of-a-scope-and-comp-owner-scope-of-a-comp)
  - [References and Declarations](#references-and-declarations)
  - [Context of a Variable](#context-of-a-variable)
  - [Scope Name Resolution](#scope-name-resolution)
- [Namespace](#namespace)
  - [Namespace Scope](#namespace-scope)
  - [Namespace Tree](#namespace-tree)
  - [Ancestor for a Scope](#ancestor-for-a-scope)
  - [Binder Namespace for Variable](#binder-namespace-for-variable)
  - [Dynamic State and Operations](#dynamic-state-and-operations)
  - [Namespace Name Resolution](#namespace-name-resolution)
- [Summary of Rules](#summary-of-rules)

# Syntax Tree

When a program is compiled, it is first converted to a **syntax tree**, which is described in the [ast](https://docs.python.org/3.10/library/ast.html) module.  This is an `ast.Module` object.  It is then converted to a binary format which can be executed by the interpreter at the time the module is imported.  The syntax tree can be obtained directly with the `ast.parse()` function.

A **node**, or **AST node** is an object which is a subclass of `ast.AST`.  In this document, **AST** is shorthand for any `ast.AST` node.  
An AST has some **child** objects[^ast-child], some of which can be other ASTs.  A non-AST child is called a **leaf**, or **AST leaf**

An **item**, or **AST item**, is either a node or a leaf.

Each item represents a single contiguous section of the text.  Children of a node represent subsets of that section of text.  Some node classes have attributes (which are not child items) showing the range of the text.

As a shorhand notation, for any `node` and `item`, **`node` > `item`**, or **`item` < `node`**, when `item` is a descendant of `node`.  Likewise, **`node` >= `item`**, or **`item` <= `node`**, which means that (`node > item or node is item`).

[^ast-child]: The children of an AST node are found by looking at the class attribute `node._fields`, which is a tuple of attribute names.  Some nodes have other attributes that are not fields, and these are ignored.  
    
    The [ast grammar](https://docs.python.org/3.10/library/ast.html#abstract-grammar) shows the names and types of fields of each AST node class, in the form `class(field, ...)`.  

    For each `field` the node has 0 or more child objects, depending on the coding of `field` as shown in this table.  `T` is the type of the child.  `value` is the value of `node.name`.  

    | field | value type | count | children |
    |:-|:-|:-|:-|
    | T name | T | 1 | [value] |
    | T? name | T \| None | 0 or 1 | filter(None, [value]) |
    | T* name | list[T] | 0 or more | value[:] |

# Variable

A **variable** is almost any occurrence of a Python identifier in a syntax tree.  The grammar determines whether an identifier is a variable or not.

Identifiers that are not variables are [^non-variables]:
[^non-variables]: Identifiers that are not variables:
- Attributes, as in `(expression).attribute`, in an `ast.Attribute` node.
- Some identifiers in an import statement.  It is simpler to specify which identifier **is** a variable which is bound according to [the document for Import statement](https://docs.python.org/3.10/reference/simple_stmts.html#the-import-statement)
        ```py
        import module as variable
        import variable(.name)*     # Note, only the top level name is bound
        from module import identifier
        from module import name as variable```

- A keyword in a function call, as in `function(keyword=expression)`

This document is concerned only with variables.
        
## Private Variable Name Mangling

This is described in [Language doc 6.2.1](https://docs.python.org/3.10/reference/expressions.html#atom-identifiers), in the section "**Private Name Mangling**".

In a CLASS scope, `cls`, the compiler treats certain [^private-name] variable names as **private names**.  This applies to any `var` where `cls` is the CLASS owner scope of `var`, by replacing `var` with a transformed [^private-mangle] version of `var`.  This is also known as the **mangled name**, or **`var.mangled`**.

The purpose is to allow a name to be used in a class to be used without conflicting with the same name in a subclass or superclass.

`var.mangled` is the identifier which actually is in the ast item.  It has the same effect on the running program as though `var.mangled` itself appeared in the source text instead of `var`.  

Important:
- A name is private *solely* as a function of the name and the name of the class.  
- A name can be private even if it is declared global or nonlocal.
- The name is private to the CLASS in any descendant scope that is not another CLASS.
- The name is *not mangled* in any other location in the program.  If the program needs to refer to the name (as an instance or class variable, or in the cls.binder scope), it must compute [^private-mangle] the mangled name and use that instead.  Note the exceptional cases discussed there.

[^private-name]:
A `var` is private to a CLASS owner scope `cls` based solely on `var` and `cls.name`.  The requirements are:
- `var.startswith("__")
- and `not var.endswith("__")`
- and `cls.name.lstrip("_") != ""`

[^private-mangle]:
The mangled name `var.mangled` is *usually* computed by
```
f'_{cls.name.lstrip("_")}{var}'
```
**Exception**:
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

I have created an [enhancement proposal](https://github.com/python/cpython/issues/95621) for cpython to provide this functionality in the language.  Please feel free to read this and comment on it.

# Scope

A few specific node classes define **AST scopes**, or simply, **scopes**.

## Closed and open scopes
In a **closed scope**, at runtime, the known variable names cannot be extended dynamically (e.g. by monkey-patching).  They are all determined at compile time.

In an **open scope**, at runtime, additional variables can be associated with the scope.

**scope.is_open** and **scope.is_closed** are True for open and closed scopes, *resp.*, and False otherwise.

## Scope Kinds

The **kind** of a scope is denoted by an enumeration, `Scope.Kind` in [scopes.py](../scopetools/scopes.py).  Each kind represents a certain node class or classes, and corresponding elements of the Python program.

|    kind      | closed? | AST class | Python code |
|:-------------|:-----------|:--|:--
|ROOT| n/a | n/a | (container for GLOBs of different modules)
|GLOB|     | ast.Module | entire module
|CLASS|    | ast.ClassDef | `class` statement + decorators
|FUNC| Yes | ast.FunctionDef |`def` statement + decorators
|LAMB| Yes | ast.Lambda |`lambda` expression
|COMP| Yes | ast.ListComp |`[expr for var in iter ...]`
|COMP| Yes | ast.SetComp |`{expr for var in iter ...}`
|COMP| Yes | ast.DictComp |`{key : expr for var in iter ...]`
|COMP| Yes | ast.GeneratorExp |`(expr for var in iter ...)`

For brevity, any of these kind names can be used to mean an AST having that kind, or some other object in `scopetools` associated with such a scope AST

The names **OPEN** and **CLOS** refer to any open scope or closed scope, *resp.*.

## Scope Owned Items and Item Owner Scopes.

The relationship of **scope owns item**, or **scope -> item**, is defined below in such a way that every item in the entire AST is owned by exactly one scope.  Thus it can be written that **scope is the owner of item**.

### Direct Items

Certain items in a scope AST are classified as **direct items**, and notated as **`scope` ->> `item`**.  They are listed in this table:

| kind | item | location
|:--|:--|:--|
| GLOB | statement | scope.body[:]
| CLASS | statement | scope.body[:]
| FUNC | statement | scope.body[:]
| | argument | scope args [^FUNC-and-LAMB-arguments]
| LAMB | expression | scope.body
| | argument | scope args [^FUNC-and-LAMB-arguments]
| COMP | everything **except** | 
|  | first iterable | scope.generators[0].iter
| Not COMP | COMP walrus[^scope-comp-walrus] target | (scope COMP walrus)[^scope-comp-walrus].id

[^FUNC-and-LAMB-arguments]:
In this table, **`scope args`** means a collection of items, which comprise all the arguments to a function or a lambda.  They include the argument name.  In a function, they also include any annotations or type comments.
The items are, in this order:
- scope.args.posonlyargs[:]
- scope.args.args[:]
- scope.args.vararg
- scope.args.kwonlyargs[:]
- scope.args.kwarg

[^scope-comp-walrus]:
In this table, **COMP walrus** of `scope` means the target name of an assignment expression in an owned COMP of `scope.  

    That is, `wal.id` for some COMP `comp` and assignment expression `wal` where
- `scope` is not a COMP
- `scope` is the [COMP owner](#owned-comp-of-a-scope-and-comp-owner-scope-of-a-comp) of `comp`
- `comp` -> `wal`

    Note that *only* the target name, `wal.id`, is the direct item of `scope`.  The assigned value, `wal.value` *is not*.

    The following conditions are syntax errors:

  - The same `wal.id` is a target in the 'for' clause of a COMP `comp2` where `comp` is an [owned COMP](#owned-comp-of-a-scope-and-comp-owner-scope-of-a-comp) of `comp2`.
  - `wal` occurs in an iterable clause in any COMP
  (even if as part of a lambda or another COMP).
  - `scope` is a CLASS.

    (For the walrus-related rules, see
[PEP 572](https://www.python.org/dev/peps/pep-0572/#scope-of-the-target).)

### All Items

**`scope` -> `item`** if:

1. `scope` is a scope AST instance.
2. `scope` [->>](#direct-items) `dir` >= `item`, for some direct item `dir`.
3. There is no other scope AST `scope2` such that `scope` > `scope2` ->> `item` (defined recursively).  Note, `item` can be another scope AST.  

In other words, a scope contains all direct items, plus all of their descendants, minus any child scope's items.

## Items Not Owned by Scope

Another way of stating which items within the scope are owned by it is to specify which items *are not* owned by it.

| Kind | Items | Owned by |
|:--|:--|:--|
| GLOB | (none) | |
| CLASS | decorator | parent |
| | base class | parent |
| | keyword arg | parent |
| FUNC | decorator | parent |
| | default value | parent |
| LAMB | default value | parent |
| COMP | first iterable | parent |
| | target of walrus | [comp owner](#owned-comp-of-a-scope-and-comp-owner-scope-of-a-comp) |

## Item CLASS Owner Scope and CLASS Class Items

The **CLASS owner scope** of an item, if any, is the nearest CLASS in the parent chain of the owner scope.  
More precisely, `scope` is the CLASS owner scope of `item` if both
- `scope` ->> `item`, and
- there is no other CLASS scope `c` such that `scope` ->> `c` ->> `item`.

An item will have no CLASS owner scope if there is no CLASS in the parent chain of its owner scope.

Conversely, the **class items** of a CLASS scope `c` consist of all items in the `c` AST whose CLASS owner scope is `c`.

This concept is applicable for [private names](#private-variable-name-mangling).

## Scope Tree
Scopes form a tree structure, using the relationship **`parent` -> `child`**.  
`parent` is the **parent** of `child`, and denoted as **child.parent**..  If `child` is a GLOB, then `child.parent` is the ROOT.  
Conversely, `child` is a **child** of `parent`.
The **parent chain** of a scope is the sequence starting with scope and followed by successive parents, ending with ROOT.
The **ancestors** of a scope are scope.parent and the ancestors (recursively) of scope.parent.  ROOT has no ancestors.
Conversely, the **descendants** of a scope are all its children and all of their descendants (recursively).  
The **global scope** of a scope, also denoted as **scope.glob** is the scope itself or an ancestor, whichever one is a GLOB.  ROOT has no global scope.  
The **root scope** of a scope, also denoted as **scope.root**, is the ROOT.

## Owned COMP of a Scope and COMP Owner Scope of a COMP

For two scopes `owner` and a COMP `comp`, `comp` is an **owned COMP** of `owner` if there is a chain of 0 or more **->** relationships ending in `comp` and all intermediate scopes are also COMPs.

That is, one of these possibilities:

- `owner` is `comp`
- `owner` -> `comp2` for some COMP `comp2` and `comp` is an owned COMP of `comp2` (recursive definition).

In addition, if `owner` is not a COMP, then `owner` **is the COMP owner of** `comp`, or `owner` **COMP>>** `comp`.  Any COMP has exactly one COMP owner. 
Note that any COMP is an owned COMP of itself, but not the COMP owner of itself.  
Example [^owned-comp-ex].  
[^owned-comp-ex]:
``` py
def f():                        # FUNC, owner
    [x for x in                    # COMP, owned by owner
        { y for y in                   # COMP, also owned by owner
            (lambda n:                      # LAMB, NOT owned
                [ z for z in [1, 2, 3] ]       # COMP, NOT owned
            )(2)
        }
    ]
```


## References and Declarations

Each occurrence of a variable in the syntax tree is called a **reference** or a **declaration**.  The occurrence is a syntax item.

### Declaration

| Declaration | AST Node | Var name | Statement |
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
- An imported name (module name or module member) or alias in an `as variable` clause.
- After `as` in a with statement or except clause, or in the as-pattern in structural pattern matching.
With an except clause, the name is used *twice*: at the start of the clause, to bind the name, and at the end of clause, to unbind the name.
- In a capture pattern in structural pattern matching.

### Non-binding reference
All other occurrences of the variable.
- The use of the current value of the variable.
    This is node.id for any `ast.Name` node in which node.context is `ast.Load()`.  

#### Walrus reference

This is a special case of a non-binding reference.  The scope is a COMP, and the reference is a walrus target in any [owned COMP](#owned-comp-of-a-scope-and-comp-owner-scope-of-a-comp).  The sole purpose of this is to catch a syntax error where the same variable is an ordinary non-binding reference elsewhere in the same scope.  The walrus target is also a binding reference in the owner scope.

### Examples:

```py
foo = bar  # 'foo' is binding and 'bar' is non-binding.
foo.append(1)  # 'foo' is a non-binding reference; 'append' is an attribute
import foo  # 'foo' is a binding reference
import foo.bar  # 'foo' is a binding reference;
                # 'bar' is part of the module name and not used in the scope.
```

## Context of a Variable

The **context** of a variable in a scope describes how a variable is used in the scope, and denoted as **scope.context(var)**.

This is an enumeration `VarCtx` in [scopes.py](../scopetools/scopes.py).  It consists of several bit flags which may be combined in certain cases.

For brevity, any of these context names may be used to denote a variable with that context, *i.e.*, "var is LOCAL in scope" means scope.context(var) is LOCAL.  And the context names can be written as attributes with the same name of a Scope, *i.e.*, `scope.LOCAL`.

### Variable Usage

This is a function of all the references, both [binding](#binding-reference) and [non-binding](#non-binding-reference) and [declarations](#declaration) to the variable in that scope.

It is a member of `VarCtx` and is denoted **scope.usage(var)**.  It is one of:

- **BINDING**.  The variable appears in a binding reference in the scope.
- **NLOCDECL**.  The scope contains a `nonlocal variable` statement.
- **GLOBDECL**.  The scope contains a `global variable` statement.
This does not apply in the global scope itself, in which the statement is redundant and ignored.
- **WALRUS** [^walrus-ref].  Only used in COMPs.  The variable appears as a walrus target in any [owned COMP](#owned-comp-of-a-scope-and-comp-owner-scope-of-a-comp).
- **USED**.  The variable appears in the scope, but none of the above.  That is, a non-binding reference.
- **UNUSED**.  The variable does not appear at all.

[^walrus-ref]:
Note, if a walrus reference occurs in a COMP scope, `scope`, the variable will be Local in `owner` = the [COMP owner](#owned-comp-of-a-scope-and-comp-owner-scope-of-a-comp) scope, as well as Walrus in `scope` itself and any other COMPs between `scope` and `owner`.  If some other reference would make the variable Local in any of these COMPs, this is a syntax error.

In the context, BINDING may be combined with one or more of these bits:
- **ANNO**.  Has an annotation.
- **PARAM**.  Is a function parameter.
- **NESTED**.  Is a nested CLASS or FUNC name.
- **IMPORT**.  Bound by an `import` statement.

### Variable Type

There are three **types** of variables in a scope, distinguished by where the variable is resolved.  It is denoted **scope.type(var)**.

These are members of `VarCtx`.  They are a function of the usage of `var` in `scope`, as well as in all ancestors of `scope`.  Every variable context has one of these bits.

| Type | scope.binder |
|:---|:---|
| **LOCAL** | scope |
| **GLOBAL** | scope.glob if is not scope |
| **FREE** | some other closed ancestor |

## Scope Name Resolution

At compile time, any item `var` is resolved by finding the scope **binder** = [scope.binder(var)](#binder-scope).  So the semantics of `var` is the pair (`binder`, `var`).

The method scope.binder(var) is discussed below, as is a helper method [scope.closure(var)](#closure-scope).  

A fundamental concept is that `var` appearing in one place in the AST, and `var` appearing in another place, with the same binder for both, are the **same variable**.

At runtime, the behavior of any mutating operation with `var` is solely a function of the scope `binder(var)`.  Lookups of `var` use this binder scope, as well as the original scope and the global scope.

### Closure Scope

The **closure scope** of a variable `var` in a scope `scope`, or denoted as **scope.closure(var)** [^closure-algo], is a closed scope, `clos`, where the name `var` would be resolved if `var` were to be declared nonlocal in `scope`.  This may be None if the nonlocal declaration would be a syntax error.

Plain **closure(item)** means owner(item).closure(item).  

[^closure-algo]:
```py
    def closure(self: Scope, var: str) -> Scope | None:
        if self is ROOT: return None
        if self.is_open: return self.parent.closure(var)
        if self.usage(var) is self.BINDING: return self
        if self.usage(var) is self.GLOBDECL: return None
        return self.parent.closure(var)
```

### Binder Scope

The **binder scope** of a variable `var` in a scope `scope`, or denoted as **scope.binder(var)** [^binder-algo], is a scope, `binder`, where the name `var` would be resolved.  This may be None if `var` would be a syntax error at that location in the AST tree.

Plain **binder(item)** means owner(item).binder(item).

[^binder-algo]:
```py
    def binder(self: Scope, var: str) -> Scope | None:
        if self.usage(var) is self.GLOBDECL: return self.glob
        if self.usage(var) is self.BINDING: return self
        if closure := self.closure(var): return closure
        if self.usage(var) is self.NLOCDECL: return None
        return self.glob
```

# Namespace

A **namespace** is a runtime concept, as opposed to a scope, which is a compile-time concept.  At all times, there is a **current namespace**.  This is related to an execution frame[^execution-frame].
[^execution-frame]:
Search for "Frame objects" in [Standard Type Hierarchy](https://docs.python.org/3.10/reference/datamodel.html?highlight=frame#the-standard-type-hierarchy).

## Namespace Scope

A namespace is associated with an AST scope.  At runtime, the scope can be executed.  To enable the execution, the scope is compiled into a **code object** at some earlier time [^scope-code].  The scope and code refer to each other with the notation **code.scope** or **scope.code**.
[^scope-code]: Compiling a scope AST.
- This occurs for a GLOB when the module's .py file is compiled into a .pyc file.  The code object is embedded in the .pyc file.  Alternatively, the Python source, as a string, can be compiled with compile(), or as part of exec().
- For other scopes in the module, this occurs as the parent scope is being compiled.

At some point(s) in time, the code object is executed [^code-execute].  Executing the code has the option of providing arguments, as for a function call.
[^code-execute]: Executing a code object.
- A GLOB code is executed the *first time* the module is loaded, usually as the result of some `import` statement.  
Or if the GLOB.code was created by compiling python source, it is executed by a call to `exec(code)` or `exec(source)`.
- A CLASS code is executed immediately (with no arguments) when executing the `class` statement.  The code is not otherwise used.
- A FUNC or LAMB code is executed with arguments, *each time* the function is called with those arguments.  The function object is created by a `def` statement or a `lambda` expression, but the code is not executed at that time.
- A COMP code is executed when the COMP expression is executed.  This evaluates the first iterable expression of the COMP (in the current namespace), then executes the code with the iterable as a single argument.

Whenever a scope's code object is executed, a new namespace is created.  This is not an actual python object, but rather a conceptual object.  **namespace.scope** means this scope.

Various terms which apply to scopes also apply to a namespace via the namespace.scope.  For example, "variable "x" is BINDING in namespace" means that "x" is Local in namespace.scope.

## Namespace Tree

Every namespace has a parent (except a special ROOT namespace which is the parent of all GLOB namespaces).

**Important**: the parent is *not* the current namespace at the time the new namespace is created.  The latter relationship is shown in a debugger as next item in the call stack.

**namespace.parent** is the namespace which was current at the time the namespace.scope.code was created.  With GLOB, CLASS, and COMP namespaces, these two are the same namespace, since the code is executed immediately.  

With FUNC and LAMB namespaces, the function objects can be stored somewhere and later called in a completely unrelated place.  Example [^namespace-parent].  The function object contains relevant information from the namespace in which it was created (such as the module's globals and any referenced nonlocal variables).

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

## Ancestor for a Scope

For any scope `scope` that is >= `namespace.scope`, **namespace.ancestor(scope)** means the namespace `ns` which is an ancestor of `namespace` where `ns.scope` is `scope`.
Thus, the chain of parents of `namespace` corresponds to the chain of parents of `namespace.scope`.

## Binder Namespace for Variable

For any variable `var`, **namespace.binder(var)** = namespace.ancestor(namespace.scope.binder(var)).  That is, namespace.binder(var).scope is namespace.scope.binder(var).

The variable `var` is always LOCAL in namespace.binder(var).

Most, but not all, operations involving `var` are performed in namespace.binder(var).  The exceptions are noted where they occur.

## Dynamic State and Operations

The dynamic state of a namespace is a mapping from variable names to possible values.

The state for a variable is represented by the class **Binding** in [namespaces.py](../scopetools/namespaces.py).  It is analogous to the internal python cell object.

- A Binding is either
  - **bound**.  It has a value (any python object, including None).  It tests True.
  - **unbound**.  It has no value, and tests False.  This is a singleton object, denoted as **Binding.unbound**.

- **binding.value** is either the stored value, or the name "\<unbound>".

- **bool(binding)** is True if it is bound, False if it is unbound.

The variable can be bound if
- it is BINDING in namespace.scope and currently has a value, or
- for open scopes, if added to the locals() dict without using a binding reference [^extra-bindings].

### Bindings

**namespace.bindings** is a conceptual object, represented by the class **Bindings** in [namespaces.py](../scopetools/namespaces.py).  It maps var names to Binding objects

Bindings has these operations:
- **bindings[var]** -> Binding.  This is a bound Binding carrying the currently assigned value, or it is Binding.unbound.
- **bindings[var] = value**.  Sets a value.  bindings[var] will now carry this value.
- **del bindings[var]**.  Removes the binding if there is one.  bindings[var] will now be Binding.unbound.  

**namespace.binding(var)** is a Binding for `var` at the present time, equivalent to `namespace.bindings[var]`.  As the namespace code is being executed, this may change.

### Initial State

When the namespace begins execution, is given an initial state.

1. For a CLASS, if its metaclass has a \_\_prepare__ method, this method supplies bindings, which can be whatever that method implements.

2. For some namespaces, a few special variables, such as `__name__` and `__module__` are bound.

3. If the scope is executed with arguments, the parameter names are bound to the corresponding values.
   - The iterable argument for a COMP is bound to a hidden name.  This means that the iterable is evaluated in the caller's namespace, but the iteration of its values occurs in the COMP code.

### Local Variables and Bindings

A var is a **local variable** if it is LOCAL in namespace.scope.  Thus it is a static property.

The **local binding** of a var is a dynamic property, and is the current namespace.binding(var) value.  The var is **locally bound** at a given time if its local binding is bound.

Normally, a var can be locally bound only if it is a local variable, because binding operations on a non-local variable take place in namespace.binder(var), which is a different namespace.

However, there are obscure ways [^extra-bindings] that a local binding can be changed other than by a binding reference in the namespace code.  This could result in a non-local variable having a local binding, or a local variable's local binding changing.  

For this reason, name resolution involves looking in namespace.bindings.

[^extra-bindings]: Obscure ways that local bindings can be changed:
  - A CLASS metaclass \_\_prepare__ method provides some initial bindings.
  - A call to `exec()` with an assignment statement and default namespace arguments.  Only in *closed* namespaces.
  - A dict of the current local bindings is obtained, and is at some later time modified.  It is obtained by
      - Calling the builtin locals() function, or
      - Getting the current frame object, via `sys._getframe()` or `inspect.stack()`, and using the frame.f_locals.

    The result is implementation dependent behavior, but is expected to be specified in future Python versions.  [PEP 558](https://peps.python.org/pep-0558) and [PEP 667](https://peps.python.org/pep-0667) are converging and expected to be adopted.  
    With this convergence, the behavior will (presumably) be:
    - locals() in a closed namespace will be a **copy** of the local bindings at the time of call.  Changes to locals() **will not** affect namespace.bindings, and *vice versa*.
    - locals() in an open namespace is identical to the namespace.bindings, and all updates to either are reflected immediately in the other.
    - frame.f_locals *may not be available* because it is dependent on the Python runtime implementation whether or not frames are available.
    - frame.f_locals, *when available*, is tied to the namespace.bindings for both closed and open namespaces, and all updates to either are reflected immediately in the other.

    Note: If you have a code analysis application, which tracks the changes to a namespace as its code is executed, then in any of the above situations, the corresponding update to the namespace must be performed

## Namespace Name Resolution

All operations performed while executing the namespace code involve a [reference](#references-and-declarations) to a `var` name.

The operations are:

- **namespace.load(var)** -> Binding.  Results from any [non-binding reference](#non-binding-reference) to `var`.  *Not always the same* as namespace.binder(var).binding(var).  
The algorithm is here[^load-algo].
[^load-algo]: Algorithm for namespace.load(var):
- if a CLOS namespace:
      - check namespace.binder(var).binding(var).  If this is bound, return it.
      - else raise an [exception](#namespace-resolution-exceptions).
- If a CLASS namespace, this depends on which type and context the variable is.
      - if usage is GLOBDECL, return namespace.glob.binding(var).  Note, type can be GLOB without usge being GLOBDECL.
      - check namespace.binding(var).  If this is bound, return it.  
        Note that if var is not LOCAL, it is still possible for var to be bound, in special circumstances [^extra-bindings].
      - if type is LOCAL or GLOBAL,
        - return namespace.glob.binding(var).
      - if type is FREE,
        - check binder.binding(var).  If this is bound, return it.
        - else raise an [exception](#namespace-resolution-exceptions).
- If the GLOB namespace:
      - check namespace.binding(var).  If this is bound, return it.
      - else return namespace.root.binding(var).
- If the ROOT namespace:
      - check the builtins module for builtins.var.  If this exists, return a Binding with this value.
      - else raise an [exception](#namespace-resolution-exceptions).

[^class-deref]:
This a very unusual situation, and it requires some sneaky code to alter the class dictionary as the class is being constructed.  In the class body, the dict is the value of `locals()`.  It is also accessible in frame.f_locals for the current frame object (accessible through the inspect module).  A local variable is not visible in any nested scope, and so normally it can only be assigned or deleted by name within the class body.
In addition, the check of local variables only happens when the var is declared nonlocal.
However, since this is possible, the behavior has to be documented as part of the resolution of `var` in the class body.
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

- **namespace.store(var, value)**.
    This always operates on the binding namespace.  Executes `namespace.binder(var).bindings[var] = value`.

    The store is a result of any [binding reference](#binding-reference) to var, except when delete() is called (see below).

- **namespace.delete(var)**.
    This always operates on the binding namespace.  Executes `del namespace.binder(var).bindings[var]`.  
    Note, if var is *already unbound*, then it raises an [exception](#namespace-resolution-exceptions)

    The delete may occur in two places:
    - a target name in a `del` statement.
    - at the *end* of an `except ... as var:` clause, *if* the handler is executed.  
        Note that `var` is bound to the exception object at the start of the handler, so the delete will succeed (unless it was deleted in the handler code explicitly).

### Namespace Resolution Exceptions

An exception raised by `namespace.load(var)` or `namespace.delete(var)` is
- `UnboundLocalError`, if `var` is LOCAL in `namespace`.
- `NameError`, otherwise.

These occur when var is currently unbound.

# Summary of Rules

Here's how to determine the meaning of an identifier, **`var`**, in the AST tree.

First, be sure it's really a variable, rather than something else[^non-variables].

If `var` is a [**private name**](#private-variable-name-mangling), replace `var` with its mangled name.

Identify the [**owner**](#scope-owned-items-and-item-owner-scopes) AST scope, usually the nearest scope containing the identifier, but sometimes something else farther up the parent chain.

Identify the [**binder**](#binder-scope) AST scope.

The static (compile time) meaning of `var` is the name `var` in scope `binder`.

The dynamic (runtime) behavior is described [here](#namespace-name-resolution).  
