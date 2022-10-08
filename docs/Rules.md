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

The **kind** of a scope is denoted by an enumeration, `ScopeKind` in [scope_common.py](../scopetools/scope_common.py).  Each kind represents a certain node class or classes, and corresponding elements of the Python program.

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
|EXEC|     | ast.Module | input to exec()
|EVAL|     | ast.Expression | input to eval()

For brevity, any of these kind names can be used to mean an AST having that kind, or some other object in `scopetools` associated with such a scope AST

The names **OPEN** and **CLOS** refer to any open scope or closed scope, *resp.*.

The name **EVEX** refers to any EVAL or EVEX scope.  The name **evex()** refers to calling either of the builtin `eval` or `exec` functions.

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
| | first iterable | scope.generators[0].iter
| EXEC [^exec-and-eval] | expression | scope.body[:]
| EVAL [^exec-and-eval] | statement | scope.body[:]
| Not COMP | COMP walrus[^scope-comp-walrus] target | (scope COMP walrus)[^scope-comp-walrus].id

[^exec-and-eval]: EXEC and EVAL scopes.  
Calling `exec(code, [globals, [locals, ]])` or `eval(code, [globals, [locals, ]])` results in an EXEC or EVAL scope.

    Its parent is
- The owner scope of the call, if no `globals` is given, or is given the same as the builtin globals().
- A new GLOB scope, otherwise.  The property **GLOB.initial** designates this `globals` dict.  At runtime, the GLOB namespace will be initially populated with the contents of `globals`.  If several scopes are created with the same `globals` argument, then their parents should be the same GLOB.

    The property **scope.locals** designates the `locals` argument, if provided and is not the same as the builtin `globals()`, or None otherwise. 

    At runtime, the call, as with any other call, immediately executes the code in a new namespace.  If GLOB.initial exists, it is used to populate GLOB's initial bindings.  If `scope.locals` exists, this will be the initial local bindings, otherwise a copy of GLOB's bindings will be used.

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
| EVAL | (none) | |
| EXEC | (none) | |

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
`parent` is the **parent** of `child`, and denoted as **child.parent**.  
Conversely, `child` is a **child** of `parent`.  
The **parent chain** of a scope is the sequence starting with the scope and followed by successive parents, ending with ROOT.  
Conversely, the **subtree** of a scope is the tree starting with the scope and moving down to the subtrees of its child scopes.  
The **ancestor chain** of a scope are the parent chain, without the scope itself.  ROOT has no ancestors.  
Conversely, the **descendants** of a scope are all scopes in the subtree, without the scope itself.  
The **global scope** of a scope, also denoted as **scope.glob** is the GLOB in the parent chain.  ROOT has no global scope.  
The **root scope** of a scope, also denoted as **scope.root**, is the ROOT at the end of the parent chain.

The tree looks like this:
- ROOT
  - GLOB
    - other kinds
      - other kinds
        - *etc.*
          
See special cases [^exec-and-eval] for EXEC and EVAL.

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
- **NLOC_DECL**.  The scope contains a `nonlocal variable` statement.
- **GLOB_DECL**.  The scope contains a `global variable` statement.
This does not apply in the global scope itself, in which the statement is redundant and ignored.
- **WALRUS** [^walrus-ref].  Only used in COMPs.  The variable appears as a walrus target in any [owned COMP](#owned-comp-of-a-scope-and-comp-owner-scope-of-a-comp).  
This appears only while the scope is being built, in order to prevent var from being also BINDING.  After the scope is built, the context changes to UNUSED.
- **USED**.  The variable appears in the scope, but none of the above.  That is, a non-binding reference.
- **UNUSED**.  The variable does not appear at all.

[^walrus-ref]:
Note, if a walrus reference occurs in a COMP scope, `scope`, the variable will be Local in `owner` = the [COMP owner](#owned-comp-of-a-scope-and-comp-owner-scope-of-a-comp) scope, as well as Walrus in `scope` itself and any other COMPs between `scope` and `owner`.  If some other reference would make the variable Local in any of these COMPs, this is a syntax error.

**scope.bind_flags(var)** is zero or more of these bits, which may be combined with BINDING:
- **ANNO**.  Has an annotation.
- **PARAM**.  Is a function parameter.
- **NESTED**.  Is a nested CLASS or FUNC name.
- **IMPORT**.  Bound by an `import` statement.

### Variable Type

There are three **types** of variables in a scope, distinguished by where the variable is resolved.  It is denoted **scope.type(var)**.

These are members of `VarCtx`.  They are a function of the usage of `var` in `scope`, as well as in all ancestors of `scope`.  Every variable context has one of these bits.

**scope.type(var)** is exactly one of these bits, and is based on [scope.binder(var)](#binder-scope):
- **LOCAL**.  binder is scope.
- **GLOBAL**.  binder is scope.glob if scope is not GLOB.
- **FREE**.  binder is some other closed ancestor.

`scope.context(var)` may also have the bit:
- **IN_LOCALS**.  It is set if the method [scope.in_locals(var)](#in-locals) is true.  
At runtime, `locals()` includes `var` if
  - this bit is set,
  - and `var` has a bound value at the time in the calling namespace.  

## Scope Name Resolution

At compile time, any item `var` is resolved by finding the scope **binder** = [scope.binder(var)](#binder-scope).  So the semantics of `var` is the pair (`binder`, `var`).

The method scope.binder(var) is discussed below, as is a helper method [scope.closure(var)](#closure-scope).  

A fundamental concept is that `var` appearing in one place in the AST, and `var` appearing in another place, with the same binder for both, are the **same variable**.

At runtime, the behavior of any mutating operation with `var` is solely a function of the scope `binder(var)`.  Lookups of `var` use this binder scope, as well as the original scope and the global scope.

### Closure Scope

The **closure scope** of a variable `var` in a scope `scope`, or denoted as **scope.closure(var)** [^closure-algo], is a closed scope, `clos`, where the name `var` would be resolved if `var` were to be declared nonlocal in `scope`.  This may be None if the nonlocal declaration would be a syntax error.

Plain **closure(item)** means owner(item).closure(item).  

EVAL_EXEC has special behavior.  Instead of looking at the parent.closure(var), it looks in [parent.locals_closure(var)](#locals-closure-scope).

[^closure-algo]:
```py
    def closure(self: Scope, var: str) -> Scope | None:
        if self is ROOT: return None
        if self is EVAL_EXEC: return self.parent.locals_closure(var)
        if self is OPEN: return self.parent.closure(var)
        if self.usage(var) is self.BINDING: return self
        if self.usage(var) is self.GLOB_DECL: return None
        return self.parent.closure(var)
```

### Binder Scope

The **binder scope** of a variable `var` in a scope `scope`, or denoted as **scope.binder(var)** [^binder-algo], is a scope, `binder`, where the name `var` would be resolved.  This may be None if `var` would be a syntax error at that location in the AST tree.

Plain **binder(item)** means owner(item).binder(item).

[^binder-algo]:
```py
    def binder(self: Scope, var: str) -> Scope | None:
        if self.usage(var) is self.GLOB_DECL: return self.glob
        if self.usage(var) is self.BINDING: return self
        if closure := self.closure(var): return closure
        if self.usage(var) is self.NLOC_DECL: return None
        return self.glob
```

### Captured Variable

A var in scope `s` **is captured by scope s2** if var in `s2` is the same variable as var in `s`.  That is, `s.binder(var)` is `s2.binder(var)`

### locals() Variables

**scope.in_locals(var)** is part of the runtime behavior of the builtin [locals()](https://docs.python.org/library/functions.html#locals) function.  
This is important because `locals()` may be used by `evex()` as the mapping for local variables in the executed code.  

`in_locals(var)` is true if var is LOCAL.  
`in_locals(var)` is also true if var is FREE and
- scope is CLOS,
- and var in scope is captured by any descendant.  

Here is the algorithm [^in-locals-algo].
[^in-locals-algo]:
    ```
    def in_locals(scope, var) -> bool:
        if scope.type(var) is LOCAL, return True
        if scope.kind is CLOS and scope.type(var) is FREE:
            return scope.captures(var, scope.binder(var))

    def scope.captures(binder, var):
        if scope is CLOS:
            if var is not FREE: return False
            if var is not UNUSED: return scope.binder(var) is binder
        return any(child.captures(binder, var)
            for child in scope's child scopes)
    ```

### \_\_class__ and super Special Cases

The var '\_\_class__' is handled as a special case.  In a CLOS scope `s`, if its closure scope method reaches a CLASS scope `C`, then the closure scope is `C`, instead of `C.parent.closure(var)`.  This makes `var` a FREE variable.

`s.in_locals(var)` operates in the usual way.  

Also, the var 'super' is handled as a special case.  In a CLOS scope `s`, if `var` appears in a non-binding reference, 
then this is *implicitly a non-binding reference of '\_\_class__'* in `s`.

# Namespace

A **namespace** is a runtime concept, as opposed to a scope, which is a compile-time concept.  At all times, there is a **current namespace**.

## Namespace Scope

A namespace is associated with an AST scope.  There is a corresponding `Scope` object, designated as **namespace.scope**.  At runtime, the scope can be executed.  To enable the execution, the scope is compiled into a **code object**, designated as **namespace.code**, at some earlier time [^scope-code].
[^scope-code]: Compiling a scope AST.
- This occurs for a GLOB when the module's .py file is compiled into a .pyc file.  The code object is embedded in the .pyc file.  
- For an EVAL or EXEC, when eval() or exec() is called with a string.
- For other scopes in the module, this occurs as the parent scope is being compiled.
- Python source, as a string, can be compiled with compile(), or as the first argument of exec() or eval().

Various terms which apply to scopes also apply to a namespace via the namespace.scope.  For example, "variable "x" is BINDING in namespace" means that "x" is Local in namespace.scope.

## Namespace Creation
At some point(s) in time, the code object is executed [^code-execute].  Executing the code has the option of providing arguments, as for a function call.
[^code-execute]: Executing a code object.
- A GLOB code is executed the *first time* the module is loaded, usually as the result of some `import` statement.  
Or if the GLOB.code was created by compiling python source, it is executed by a call to `exec(code)` or `exec(source)`.
- A CLASS code is executed immediately (with no arguments) when executing the `class` statement.  The code is not otherwise used.
- A FUNC or LAMB code is executed with arguments, *each time* the function is called, using the arguments in that call.  The function object is created by a `def` statement or a `lambda` expression, but the code is not executed at that time.
- A COMP code is executed when the COMP expression is executed.  This evaluates the first iterable expression of the COMP (in the current namespace), then executes the code with the iterable as a single argument.

Whenever a scope's code object is executed, a new namespace is created.  **namespace.scope** means this scope.  
 This is related to an execution frame[^execution-frame], which is the internal object created by the interpreter.  **namespace.frame** refers to this frame.

[^execution-frame]:
Search for "Frame objects" in [Standard Type Hierarchy](https://docs.python.org/3.10/reference/datamodel.html?highlight=frame#the-standard-type-hierarchy).

## Namespace Tree

Every namespace has a parent (except a special ROOT namespace which is the parent of all GLOB namespaces).

**namespace.parent** is the namespace which was current at the time the *namespace.code* was created.  With GLOB, CLASS, and COMP namespaces, these two are the same namespace, since the code is executed immediately.  

**Important**: the parent is *not necessarily* the caller namespace at the time the new namespace is created.  The latter relationship is shown in a debugger as next item in the call stack.  `(new namespace).frame.f_back` is `(caller namespace).frame`.

With FUNC and LAMB namespaces, the function objects can be stored somewhere and later called in a completely unrelated place.  Example [^namespace-parent].  The function object contains relevant information from the namespace in which it was created (such as the module's globals and any referenced free variables).

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

## Finding the Namespace for a Scope

The parent chain of a namespace corresponds to the (scope) parent chain of `namespace.scope`.  `namespace.parent.scope` is always identical to `namespace.scope.parent`.  And so on, up the parent chain.

For any scope `scope` that is in the parent chain of `namespace.scope`, **namespace.find_scope(scope)** means the corresponding namespace in the namespace parent chain.  `namespace.find_scope(scope).scope` is always identical to `scope`.

## Binder Namespace for Variable

The **binder namespace** for a variable is the namespace which corresponds to its binder scope in the namespace's scope.

For any variable `var`, **namespace.binder(var)** = `namespace.find_scope(namespace.scope.binder(var))`.  That is, `namespace.binder(var).scope` is `namespace.scope.binder(var)`.

The variable `var` is always LOCAL in `namespace.binder(var)`.

All binding operations, and most (but not all) non-binding operations, involving `var` are performed in namespace.binder(var).  The exceptions are noted where they occur.

### locals() Binder Namespace

**namespace.locals_binder(var)**[^locals-binder-algo] is part of the runtime behavior of the builtin [locals()](https://docs.python.org/library/functions.html#locals) function.  
This is important because `locals()` may be used by `exec()` or `eval()` as the mapping for local variables in the executed code.  
In an EVAL_EXEC namespace, `namespace.parent.locals_binder(var)` is used in resolving `var`, when `locals()` is actually the local variable mapping.

The result is the same as `namespace.binder(var)` if `namespace.context(var)` has the IN_LOCALS bit set, and None otherwise.

**namespace.locals_bindings** is a Bindings object for all vars which have the IN_LOCALS bit set.

## Dynamic State

The dynamic state of a namespace is a mapping from variable names to possible values.

### Binding and Bindings

The state for a variable is represented by the class **Binding** in [namespaces.py](../scopetools/namespaces.py).  It is analogous to the internal python [cell object in User-defined functions](https://docs.python.org/reference/datamodel.html#the-standard-type-hierarchy).

A Binding is either
  - **bound**.  It has a value (any python object, including None).
  - **unbound**.  It has no value.  This is a singleton object, denoted as **Binding.unbound**.

**Binding(value)** designates a Binding which is bound to this value.  
**Binding()** designates an unbound Binding, same as `Binding.unbound`.

**binding.value** is the stored value if it is bound, or raises ValueError if it is unbound.

**bool(binding)** is True if it is bound, False if it is unbound.

**namespace.bindings** is represented by the class **Bindings** in [namespaces.py](../scopetools/namespaces.py).  It maps var names to Binding objects

Bindings has these operations:
- **bindings[var]** -> Binding.  This is a bound Binding carrying the currently assigned value, or it is Binding.unbound.  It is valid for any `var`.
- **bindings.global_binding(var)** -> Binding.  This is similar to `bindings[var]`, except that it will also check for `var` being a builtin name [^global-binding-algo].  Only valid in a namespace.global_bindings object.
- **bindings[var] = value**.  Sets a value.  bindings[var] will now carry this value.
- **del bindings[var]**.  Removes the binding if there is one.  `bindings[var]` will now be `Binding.unbound`.  

**namespace.binding(var)**, or **namespace[var]** is a Binding for `var` at the present time, equivalent to `namespace.bindings[var]`.  As the namespace code is being executed, this may change.  
The Binding can be bound if
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

### Initial State

When the namespace begins execution, it is given an initial state.

1. For a CLASS, if its metaclass has a \_\_prepare__ method, this method supplies bindings, which can be whatever that method implements.

2. For some namespaces, a few special variables, such as `__name__` and `__module__` are bound.

3. If the scope is executed with arguments, the parameter names are bound to the corresponding values.
   - The iterable argument for a COMP is bound to a hidden name.  This means that the iterable is evaluated in the caller's namespace, but the iteration of its values occurs in the COMP code.

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

**namespace.locals_binding(var)** is a Binding that reflects the dict returned by the builtin `locals()` at the time it is called.  

In an OPEN namespace, this is identical to `namespace.binding(var)

In a CLOS namespace, this is:
- `namespace.binding(var)` if `var` is LOCAL,
- `namespace.binder(var).binding(var)` if `var` is both FREE and IN_LOCALS,
- or `Binder.unbound` otherwise.

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

[^closed-locals-implementation]:

    CPython behavior in a CLOS namespace:
- `locals()` always returns the same dict object, `d`, in the same namespace.  Therefore, `d` will always be the same as that returned by the most recent `locals()` call.
- `d` is updated by each `locals()` call to reflect the bindings of all IN_LOCALS vars in the namespace.  It maps `var` to `(b := namespace.binding[var]).value` if `b` is bound. The key `var` is absent if `b` is unbound.  Thus a `var` can be added, or its value changed, or deleted.
- Any changes to `d` made by the caller (regarding IN_LOCALS vars) are lost as a result of a subsequent `locals()`.
- Any other keys added to `d` by the caller will remain there after a subsequent `locals()`.
- Changes to `d` are not visible in the namespace.

  The behavior is expected to be standardized in future Python versions.  [PEP 558](https://peps.python.org/pep-0558) and [PEP 667](https://peps.python.org/pep-0667) are converging and expected to be adopted.  
  With this convergence, the behavior will (presumably) be that
- locals() produces a *copy*, `d` of `namespace.locals_bindings()` at the time of the `locals()` call.  This is the sme as current CPython behavior,  except that the contents of `d` are not affected by later `locals()` in the namespace.
- Any changes to `d` made by the caller not visible in the namespace, nor in any other dict returned by `locals()`.
- Any changes in the namespace are not visible in `d`.

  
To be safe from implementation dependencies, a Python program should make a copy of any `locals()` dict, and should not try to modify variables using `evex(code)` with no other arguments.  

Examples [^closed-locals-examples].

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

- **namespace.load(var)** -> Binding.  Results from any [non-binding reference](#non-binding-reference) to `var`.  *Not always the same* as namespace.binder(var)[var].  
    This is `(b := namespace.load_binding(var)).value` if `b` is bound, otherwise it raises an [exception](#namespace-resolution-exceptions).
- **namespace.store(var, value)**.
    This always operates on the binding namespace.  Executes `namespace.binder(var).bindings[var] = value`.

    The store is a result of any [binding reference](#binding-reference) to var, except when delete() is called (see below).

- **namespace.delete(var)**.
    This always operates on the binding namespace.  Executes `del namespace.binder(var).bindings[var]`.  
    Note, if var is *already unbound*, then it raises an [exception](#namespace-resolution-exceptions).

    The delete may occur in two places:
    - a target name in a `del` statement.
    - at the *end* of an `except ... as var:` clause, *if* the handler is executed.  
        Note that `var` is bound to the exception object at the start of the handler, so the delete will succeed (unless it was deleted in the handler code explicitly).

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
 
**EVEX.global_bindings**, **EVEX.bindings** and **EVEX.free_bindings** are `Bindings` objects representing the actual `globs`, `locs`, and `closure` arguments to `evex()`.  These are used by `EVEX.load_binding()`.

#### Builtins for evex()

Whenever `evex()` is called, the `globs` argument is checked.  If it doesn't have a key '\_\_builtins__', then this key is inserted into `globs` with the value being the `__dict__` of the `builtins` module.  This key is visible in the EVEX.globs bindings.  
The reason for this is to allow the caller to `evex()` to supply an alternative builtins mapping, while using the `builtins` module by default.  
Note: *the key '\_\_builtins__' remains inserted in the dict* given as the `globs` argument during and after the `evex()` call.

#### Using locals() and globals()

Either of the mappings may come from a `locals()` or `globals()` call.  The call may have been made in the caller namespace at the time of the `evex()` call, or it may have been made at some earlier time (possibly in a different caller namespace) and stored somewhere.  

A call to `globals()` in `caller` is equivalent to a call to `locals()` in `caller.glob`.

### Namespace Resolution Exceptions

An exception raised by `namespace.load(var)` or `namespace.delete(var)` is
- `UnboundLocalError`, if `var` is LOCAL in `namespace`.
- `NameError`, otherwise.

These occur when var is currently unbound.

# Summary of Rules

Here's how to determine the meaning of an identifier, **`var`**, in the AST tree.

First, be sure it's really a variable, rather than something else[^non-variables].

If `var` is a [**private name**](#private-variable-name-mangling), replace `var` with its mangled name.

Identify the [**owner**](#scope-owned-items-and-item-owner-scopes) AST scope, usually the nearest scope containing the identifier, but sometimes something else further up the parent chain.  This requires analysis of the entire AST of the scope and all of its parent chain.

Identify the [**binder**](#binder-scope) AST scope.

The static (compile time) meaning of `var` is the name `var` in scope `binder`.

The dynamic (runtime) behavior is described [here](#namespace-name-resolution).  
