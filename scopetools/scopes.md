# All About Scopes

Michael Rolle, 2022

# Introduction

I've been trying to pin down the definition of scopes.
Here's my latest attempt.
IMO the official
[Naming and binding
](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding)
section in the Language Reference does not do a good job specifying this.

# Definitions

## Syntax Tree

A **Syntax Tree** is a representation of the program text of a module, which is produced by the `ast.parse()` method.  Refer to [ast documentation](https://docs.python.org/3.10/library/ast.html#module-ast) for complete details.

The tree for a Python module is comprised of **nodes** which are subclasses of `ast.AST`.  Each node represents a single contiguous section of the text.  Elements of a node, including other nodes, represent subsets of that section of text.

## Scope

A Scope is a portion of the program text which corresponds to one of a few specific node classes.  They are represented in the `scopetools.scopes` module by corresponding subclasses of `Scope`

These are:
- **`GlobalScope`**, for `ast.Module`.  This is the entire program text.
- **`ClassScope`**, for `ast.ClassDef`.  This is a `class` statement including decorators.
- **`FunctionScope`**, for `ast.FunctionDef`.  This is a `def` statement including decorators.
- **`LambdaScope`**, for `ast.Lambda`.  This is a `lambda` expression.
- **`ComprehensionScope`**, for one of:
    - `ast.ListComp`.  This is an `[expr for var in iter ...]` expression.
    - `ast.SetComp`.  This is an `{expr for var in iter ...}` expression.
    - `ast.DictComp`.  This is a `{key : expr for var in iter ...]` expression.
    - `ast.GeneratorExp`.  This is an `(expr for var in iter ...)` expression.
 
## Scope Kind

This is an enumeration in the `Basic` class (a base class of `Scope`).  The members are also class attributes of `Scope`  They correspond to the actual class of the scope:
- **GLOB**: `GlobalScope`
- **CLASS**: `CkassScope`
- **FUNC**: `FunctionScope`
- **LAMB**: `LambdaScope`
- **COMP**: `ComprehensionScope`

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

### Binding and Non-binding References

Each occurrence of a variable in the program text is called a **reference**.

A **binding reference** implies that the variable is Local in the home scope.  Refer to the [documentation](https://docs.python.org/3.10/reference/executionmodel.html#binding-of-names). The possibilities are:
- An `ast.Name` node, where the context attribute is either `ast.Store()` or `ast.Del()`.  Yes, a `del variable` statement is considered binding.

  This includes a target name in:
    - an assignment statement.
    - an augmented assignment statement.
    - an annotated assignment statement (even if there is no value).
    - an assignment expression.
    - a 'for' stateemnt target
    - a 'for' clause in a comprehension
- The name in a function or class definition.
- A parameter name in a function definition.
- An imported name (module name or module member) or alias in an `as variable` clause.
- After `as` in a with statement, except clause or in the as-pattern in structural pattern matching,
- In a capture pattern in structural pattern matching
A **non-binding reference** is simply the use of the current value of the variable, and does not affect the variable's context (defined below) in the home scope (other than changing from Free to Seen).
    This is any `ast.Name` node in which the context attribute is `ast.Load()`.

Examples:

```py
foo = bar  # 'foo' is binding and 'bar' is non-binding.
foo.append(1)  # 'foo' is a non-binding reference; 'append' is an attribute
import foo  # 'foo' is a binding reference
import foo.bar  # 'foo' is a binding reference;
                # 'bar' is part of the module name and not used in the scope.
```

## Parent or Enclosing Scope

Scopes form a tree structure based on the relationship of **enclosing**.  Any two scopes in the program are either disjoint, or one is completely contained in the other.  In latter case, we say that the larger scope *encloses* the smaller scope.

The **parent** of any scope (other than the GlobalScope) is its smallest enclosing scope.

### Enclosed Comprehension Scope

For any scopes `outer` and `inner`, `inner` is an **enclosed comprehension** of `outer` if:
- `inner` is a comprehension,
- `outer` is an enclosing scope of `inner`,
- recursively, either
    - 'outer' is the parent of 'inner',
    - or `inner.parent` is an enclosed comprehension of `outer`.

That is to say, every scope in the parent chain, starting from `inner` up to, but not including, `outer`, is a comprehension. 

## Home Scope

This is a property of each variable reference in the program text.  It is the scope associated with that reference.

Most of the time, the **home scope** is the smallest scope whose area includes the reference.

However, certain variable references are not part of that scope and are part of the parent scope.  These exceptions are references which are, or which occur in:

- Class and function names.
- Class and function decorators.
- Arguments in class definitions (base classes and metaclass keyword arguments).
- Function and lambda argument default values.
- Function argument annotations (unless they are turned into forward references by `from __future__ import annotations`).
- The leftmost iterable expression in any comprehension.

### Walrus considerations

Also, for an assigment expression within any comprehension, the home scope of the target variable is the nearest enclosing non-comprehension scope.  That is, it skips over enclosing comprehensions.  The comprehension is an *enclosed comprehension* (defined above) of the home scope.

For example, at the top level, the home scope of the variable in 

```[x for x in [(variable := y) for y in iterable]]```

is the global scope, not the `[x for ...]` comprehension.

In addition, the following conditions are errors:

- The variable is a target in the 'for' clause of a comprehension and also a walrus target in that comprehension or any *enclosed comprehension* (defined above).
- A walrus occurs in an iterable clause in any comprehension
  (even if as part of a lambda or another comprehension).
- The home scope is a class definition.

(For the walrus-related rules, see
[PEP 572](https://www.python.org/dev/peps/pep-0572/#scope-of-the-target).)

## Context of a variable

This describes how a variable is used in a scope.  
During the build of the scope, It can be one of:

- **Local**.  The variable appears somewhere in the scope where it is bound to some value, annotated without a value, or deleted.
- **Nonlocal**.  The scope contains a `nonlocal variable` statement.  It is a syntax error if this occurs after any other reference, or in the global scope.  After building the scope, this 
- **Global**.  The scope contains a `global variable` statement.  It is a syntax error if this occurs after any other reference.  This does not apply in the global scope itself.  The variable is considered to be Local in the global scope as well.
- **Seen**.  The variable appears in, and only in, a non-binding context.  It will be changed to Free at the end of the scope text.
- **Walrus**.  Only used in comprehensions.  The variable appears as a walrus target in this scope or any *enclosed comprehension* (defined above).
- **Free**.  None of the above.  The variable appears only in a non-binding context or it might not appear at all in the scope.

After the scope is built, it can be one of these, based on `scope.binding_scope(var)`:
- **Local**.  `scope.binding_scope(var)` is `scope`.
- **Global**.  `scope.binding_scope(var)` is the global scope, if `scope` *is not* the global scope
- **Nonlocal**.  `scope.binding_scope(var)` is neither `scope` nor the global scope.

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

## Context

The context of a variable is determined by a state machine which responds to certain events, which correspond to some `ast` nodes in the program.  These are applied in the program order.

Initial context = Free.

Any non-binding reference to `var`:

    Free -> Seen
Reference to `var` as a walrus target in a comprehension or any *enclosed comprehension* (defined above).

    Free | Seen -> Walrus
    Local -> syntax error
    other contexts are not possible here.

Any other binding reference to `var` :

    Free | Seen -> Local
    Nonlocal | Global | Walrus -> syntax error

A `nonlocal var` statement:

    Free -> Nonlocal
    Seen | Local | Global -> syntax error

A `global var` statement:

    Free -> Global
    Seen | Local | Nonlocal -> syntax error

`cleanup():

    Seen | Free | Walrus -> Nonlocal | Global or syntax error.

## Closure scope

The method `scope._closure_scope(var)` works by searching from the scope along the parent chain, looking for a *closed* scope in which the var is Local.  The search fails if it reaches a scope in which the var is Global, or if it reaches the global scope.

```py
def _closure_scope(self, var):
    if self is global scope: return None
    if self.context(var) is Global: return None
    if self is closed and self.context(var) is Local: return self
    else: return self.parent._closure_scope(var)
```

## Binding scope

The method `scope.binding_scope(var)` varies by the context of `var`.

```py
def binding_scope(self, var):
    context = self.context(var)
    if context is Global: return global scope
    if context is Local: return self
    if context is Nonlocal:
        if self._closure_scope(var): return self._closure_scope(var)
        else: raise SyntaxError
    else:
        closure = self._closure_scope(var)
        if closure: return closure
        else:
            if context is Nonlocal: raise SyntaxError
            else: return global scope
```


# Acknowledgments

This document started with an [essay](https://github.com/gvanrossum/gvanrossum.github.io/blob/main/formal/scopes.md) written by Guido van Rossum.
I removed the Toplevel scope.
I moved all the runtime discussion to a new document [namespaces.md](namespaces.md).

Otherwise, I simplified some definitions and revised the search algorithms.

