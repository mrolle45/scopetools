# All About Scopes

Michael Rolle, 2022

# Definitions

## Syntax Tree

A **syntax tree** is a representation of the program text of a module, which is produced by the `ast.parse()` method.  Refer to [ast documentation](https://docs.python.org/3.10/library/ast.html#module-ast) for complete details.

A **node** is an object which is a subclass of `ast.AST`.  It contains **items**, which can be:
- an element of a list which is a field of the node.
- an optional field of the node with a value other than None.
- a required single-valued field of the node.

A **syntax item** is an object which appears in the syntax tree.  This can be:
- A node.
- An item of a node which is not another node.  For example, `ast.FunctionDef.name`, which is a str.  

Each item represents a single contiguous section of the text.  Items of a node represent subsets of that section of text.

A Python module is considered to be the same as an `ast.Module` tree.  In this document, the program will be described in terms of nodes in the syntax tree.

The code in this `scopetools` package does not require that there be an actual syntax tree, or a module file which would be parsed into one.  An application is only required to build a Scope tree as though there is an actual syntax tree.  There are examples of programs which build a scope tree without an actual syntax tree.

## Scope

A **scope** is a syntax item of one of a few specific node classes.  They are represented in the `scopetools.scopes` module by corresponding subclasses of `Scope`

A **scope kind** is an enumeration in the `Basic` class (a base class of `Scope`).  The members are also class attributes of `Scope`.

| class   |      kind      |  node | Python |
|:----------|:-------------|:------|:--
| RootScope |ROOT | (see below) |
| GlobalScope|GLOB|   ast.Module | entire module
| ClassScope|CLASS|   ast.ClassDef | `class` statement with decorators
| FunctionScope|FUNC|   ast.FunctionDef |`def` statement with decorators
| LambdaScope|LAMB|   ast.Lambda |`lambda` expression
| ComprehensionScope|COMP|   ast.ListComp |`[expr for var in iter ...]`
| ...|...|   ast.SetComp |`{expr for var in iter ...}`
| ...|...|   ast.DictComp |`{key : expr for var in iter ...]`
| ...|...|   ast.GeneratorExp |`(expr for var in iter ...)`


The class **RootScope** represents the entire environment of a running program.  That is, it is a collection of modules, represented by GlobalScope objects.  It is the top of a Scope tree.  
 
## Variable

A **variable** is almost any occurrence of a Python identifier in a program text.  The grammar determines whether an identifier is a variable or not.

The exceptions are:
- Attributes, as in `(expression).attribute`, or an `ast.Attribute` node.
- Some identifiers in an import statement.  It is simpler to specify which identifier **is** a variable which is bound according to [the document for Import statement](https://docs.python.org/3.10/reference/simple_stmts.html#the-import-statement)
    ```py
    import module as variable
    import variable(.name)*     # Note, only the top level name is bound
    from module import identifier
    from module import name as variable```
- A keyword in a function call, as in `function(keyword=expression)`

This document is concerned only with variables.

### References

Each occurrence of a variable in the syntax tree is called a **reference**.  The reference is a syntax item.

#### binding reference
This implies that the variable is Local in the home scope.  Refer to the [documentation](https://docs.python.org/3.10/reference/executionmodel.html#binding-of-names) for name binding. The possibilities are:
- An `ast.Name` node, where the context attribute is either `ast.Store()` or `ast.Del()`.  Yes, a `del variable` statement is considered binding.

  This includes a target name in:
    - an assignment statement.
    - an augmented assignment statement.
    - an annotated assignment statement (even if there is no value).
    - an assignment expression.  In a comprehension, the home scope is the owner scope.
    - a 'for' statement target.
    - a 'for' clause in a comprehension.
- The name in a function or class definition.  The home scope is the parent.
- A parameter name in a function definition.
- An imported name (module name or module member) or alias in an `as variable` clause.
- After `as` in a with statement or except clause, or in the as-pattern in structural pattern matching.
- In a capture pattern in structural pattern matching.

#### non-binding reference
 is simply the use of the current value of the variable, and does not affect the variable's context (defined below) in the home scope (other than changing from Free to Seen).
    This is any `ast.Name` node in which the context attribute is `ast.Load()`.

Examples:

```py
foo = bar  # 'foo' is binding and 'bar' is non-binding.
foo.append(1)  # 'foo' is a non-binding reference; 'append' is an attribute
import foo  # 'foo' is a binding reference
import foo.bar  # 'foo' is a binding reference;
                # 'bar' is part of the module name and not used in the scope.
```

## Enclosing or Enclosed Scope

For any two scopes, either they are unrelated (that is, they cover disjoint segments of the program code), or else one covers a subset of the other.

In the latter case, the larger scope **encloses**, or it is an **enclosing scope** of, the smaller scope.  Likewise, the smaller scope **is enclosed by**. or it is an **enclosed scope** of, the larger scope.

In this document, it may also be expressed succinctly as **outer > inner** (or **inner < outer**).
## Parent or Child Scope

An outer scope is the **parent** of an inner scope, or the inner scope is a **child** of the outer scope, when
- parent > child, and
- There is no other scope such that parent > scope > child.

In a scope tree, every scope other than the RootScope has a parent, and every scope can be reached from the root by a series of children.

### Owned Comprehension Scope

For the purpose of explaining the behavior of assignment expressions in a comprehension...  
For two scopes `owner` and `owned`, `owned` is an **owned comprehension** of `owner` if:
- `owner` >= `owned`
- `owned` is a comprehension
- for any `other` scope, where `owner` > `other` > `owned`, `other` is also a comprehension.

Note that a comprehension is an owned comprehension of itself.

That is to say, every scope in the parent chain, starting from `owned` up to, but not including, `owner`, is a comprehension. 

In addition, if `owner` is not a comprehension, then `owner` is **the owner of** `owned`.  Any comprehension has exactly one owner.
Example:
``` py
def f():                        # owner
    [x for x in                    # owned by owner
        { y for y in                   # also owned by owner
            (lambda n:                      # NOT owned
                [ z for z in [1, 2, 3] ]       # NOT owned
            )(2)
        }
    ]
```

## Home Scope

This is a property of each variable reference in the syntax tree.  It is the scope associated with that reference.

Most of the time, the **home scope** is the smallest scope whose area includes the reference.

However, certain variable references are not part of that scope and are part of the parent scope.  These exceptions are references which are, or which occur in:

- Class and function names.
- Class and function decorators.
- Arguments in class definitions (base classes and metaclass keyword arguments).
- Function and lambda argument default values.
- Function argument annotations (unless they are turned into forward references by `from __future__ import annotations`).
- The leftmost iterable expression in any comprehension.

### Walrus considerations

Also, for an assigment expression within any comprehension, the home scope of the target variable reference is the owner non-comprehension scope.  That is, it skips over enclosing comprehensions.  The comprehension is owned by the home scope.

For example, at the top level, the home scope of the variable in 

```[x for x in [(variable := y) for y in iterable]]```

is the global scope, not the `[x for ...]` comprehension.

In addition, the following conditions are errors:

- The variable is a target in the 'for' clause of a comprehension and also a walrus target in any comprehension owned by it (defined above).
- A walrus occurs in an iterable clause in any comprehension
  (even if as part of a lambda or another comprehension).
- The owner scope is a class definition.

(For the walrus-related rules, see
[PEP 572](https://www.python.org/dev/peps/pep-0572/#scope-of-the-target).)

## Context of a variable

This is an enumeration `Scope.VarCtx` in the `Basic` class (a base class of `Scope`).  It describes how a variable is used in a scope.  It is returned by [scope.context(var: str)](#scope.context).
During the build of the scope, it may change.  
It can be one of:

- **Local**.  The variable appears in a binding reference in the scope, or in `variable := value` in any [owned comprehension](#owned-comprehension-scope).  Also, in a GlobalScope, if its context is Global in any enclosed scope.
- **Nonlocal**.  The scope contains a `nonlocal variable` statement.
- **Global**.  The scope contains a `global variable` statement.
This does not apply in the global scope itself, in which it is redundant and ignored.
- **Seen**.  The variable appears (so far) in, and only in, a non-binding context.
- **Walrus**.  Only used in comprehensions.  The variable appears as a walrus target in any [owned comprehension](#owned-comprehension-scope).
- **Unused**.  None of the above.  The initial state.

The Scope object records the contexts of all variables with other than Unused context.
At the beginning of the scope, the context of any variable is Unused.  This will change to one of the other contexts the first time the variable is used.  After that, the only allowed change is from Seen to Local.  Any other occurrence of the variable raises a SyntaxError.

Each occurrence of an identifier has exactly one context.
Context is determined purely by the grammar.

The method `scope.context(var: str)` returns a `VarCtx` object for the context.  This may change before the entire scope's text has been built.

## Closed and open scopes

Function, lambda and comprehension scopes are **closed scopes**.
At runtime, the known variable names cannot be extended dynamically
(e.g. by monkey-patching).

All other scopes are **open scopes**.  At runtime, additional variables can be associated with the scope.

## Binding scope of a variable

This is determined at compile time for any scope and variable name.  It is the home scope, or some scope which encloses it.  It is denoted by the method call

`scope.binding_scope(var: str)`

The algorithm for this is contained below.

The variable is always *Local* in its binding scope.

A fundamental idea here is that a variable is considered to be **the identical variable** in both the home scope and the binding scope.  At runtime, any changes to the variable are seen in both scopes.

At runtime, any binding operation is always performed in the binding scope.  However, the current value of a variable is not always its value in the binding scope.  This is discussed in the [namespaces](namespaces.md) document.

Note: this cannot be computed until the *entire* module text has been processed and `outer._cleanup()` has been called for every `outer` which encloses `scope`.

## Closure scope of a variable

This concept is related to the determination of the binding scope.
It is denoted by the method call

`scope._closure_scope(var: str) -> Scope | None`

The algorithm for this is detailed below.

The closure for a closed scope where `var` has Local context, is itself.
The closure for a closed scope where `var` has Global context, is None.
The closure for the global scope is None.
Otherwise, the closure is the closure of its parent.

Note: this cannot be computed until the *entire* module text has been processed and `outer._cleanup()` has been called for every `outer` which encloses `scope`.

## Scope for eval() and exec()

These functions do not have the same effect as their code strings would have if located in the same place directly in the scope.  The difference is in the value of a variable which is captured from an enclosing scope.  If there is a nonlocal declaration in the scope, then the results are the same.  Otherwise, the value in the global scope is used (or a NameError is raised).

The **eval scope** of a variable is the scope in which `eval()` will find the value.  It uses the `globals()` and `locals()` values at the point where `eval()` is called.

The **local scope** of a variable is the same, if it is found in `locals()`, otherwise it is a NameError.  It is in `locals()` if its context is either Local or Nonlocal, but not if it is Capture or Global.

These are implemented by the methods `scope.eval_scope(var)` and `scope.locals_scope(var)`, *resp.*, which are detailed below.

# Scope Building

A Scope is built by first constructing it, and then calling primitive methods in the same order as corresponding items in the syntax tree.
This will create and build all the nested scopes.

The top of the Scopes tree is a RootScope, which contains a GlobalScope for each module.  There are two ways to build the tree:
1. Construct a RootScope() directly,  
    Build each GlobalScope using  
    `with root.nest(root.GLOB, module name (optional)) as glob:`  
    - primitive methods on glob and any nested scopes.
2. Construct a `GlobalScope(name (optional))` directly.  This creates a RootScope as its parent.  The name, if provided, is bound in the RootScope.  
    `with glob.build():`  
    - primitive methods on glob and any nested scopes.

After any GlobalScope has been built, then any post-build methods may be called on any scope in its scope tree.

## Primitive Methods

A scope is specified by calling various primitive methods while scanning the scope's text.

- **`with scope.build(): ...`**  
    All other primitives are called in this context.  
    Afterwards,
    - the name of a Class or Function scope is bound in the parent scope
    - the name of a Global scope, if given, is bound in the Root scope,  
    - for a Global scope, `scope._cleanup()` is called.
- **`with scope.nest(kind, name = '') -> Scope: ...`**  
    Creates, and yields, a new scope enclosed in the current scope.  Includes new scope.build(), so all other primitives for the new scope are called within this context.
- **`scope.use(var: str)`**  Variable in a non-binding reference.
- **`scope.bind(var: str, **kwds)`**  Variable in a binding reference.  
    Keywords are used to indicate if it is annotated, a function argument, or a nested scope.  
    The semantics are affected by these context managers:
    - **`with scope.use_walrus(): ...`**  
    Any `bind()` call is for the target in a `target := value` expression.
    - **`with scope.no_walrus(): ...`**  
    Any `with use_walrus():` raises a SyntaxError.  This is done while processing the iterable expression in a `for x in iterable` which is part of a comprehension.

- **`scope.nonlocal_statement(var: str)`**  In `nonlocal variable`.
- **`scope.global_statement(var: str)`**  In `global variable`.
- **`scope._cleanup()`**  
    Called implicitly at the end of `glob.build()` for any GlobalScope `glob`.  
    Then called recursively for all nested scopes in the tree.  
    1. Any variable with a Free, Seen or Nonlocal context is resolved to either Nonlocal or Global, using the `scope.binding_scope(variable)` method (detailed below).  In the case of Nonlocal, it may raise a SyntaxError.
    2. Call `child._cleanup()` recursively for each child scope.
## Post-build Methods
These may be called after `outer._cleanup()` has been called for all `outer` scopes that enclose `scope`.
- **`scope.binding_scope(var: str) -> Scope`**  
Returns the binding scope for `var` (defined above and detailed below).

- **`scope._closure_scope(var: str) -> Scope | None`**  
This is a helper function for `binding_scope(var)`
Returns the binding scope for `var`, if any (defined above and detailed below).

# Algorithms

## Scope.context
Scope.context(self, var: str) -> VarCtx

The context of a variable is determined by a state machine which responds to certain events, which correspond to some `ast` nodes in the program.  These are applied in the program order.

Initial context = Unused.

Any non-binding reference to `var`:

    Free -> Seen
Reference to `var` as a walrus target in an [owned comprehension](#owned-comprehension-scope) of a comprehension.

    Unused | Seen -> Walrus
    Local -> syntax error
    other contexts are not possible here.

Any other binding reference to `var` :

    Unused | Seen -> Local
    Nonlocal | Global | Walrus -> syntax error

A `nonlocal var` statement:

    Unused -> Nonlocal
    Seen | Local | Global -> syntax error

A `global var` statement:

    Unused -> Global
    Seen | Local | Nonlocal -> syntax error

## Scope._closure_scope

The method `scope._closure_scope(var)` works by searching from the scope along the parent chain, looking for a *closed* scope in which the var is Local.  The search fails if it reaches a scope in which the var is Global, or if it reaches the global scope.

```py
def _closure_scope(self, var: str):
    if self is global scope: return None
    if self.context(var) is Global: return None
    if self is closed and self.context(var) is Local: return self
    else: return self.parent._closure_scope(var)
```

## Scope.binding_scope

The method `scope.binding_scope(var)` varies by the context of `var`.

```py
def binding_scope(self, var: str):
    context = self.context(var)
    if context is Global: return global scope
    if context is Local: return self
    closure = self._closure_scope(var)
        if closure: return closure
        if context is Nonlocal:
            raise SyntaxError
        else:
            return global scope
```


# Acknowledgments

This document started with an [essay](https://github.com/gvanrossum/gvanrossum.github.io/blob/main/formal/scopes.md) written by Guido van Rossum.
I removed the Toplevel scope.
I moved all the runtime discussion to a new document [namespaces.md](namespaces.md).

Otherwise, I simplified some definitions and revised the search algorithms.

