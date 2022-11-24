# `scopes` Module

Michael Rolle, 2022

This documents the `scopes` module.  It has classes and functions for examining the scopes found in a python program.

Basic information about scopes and the resolution of names is found in [Rules.md](Rules.md#scope)


# Scope Building

A Scope is built by first constructing it, and then calling primitive methods in the same order as corresponding items in the syntax tree.
This will create and build all the nested scopes.

The top of the Scopes tree is a RootScope, which contains a GlobalScope for each module.

The tree is built using the classmethod `ScopeTree.build()`.
- The class is usually GlobalScope, but could be some other subclass of Scope.  If the tree is not a GLOB, then a GLOB will be created as its parent.
- A new ROOT is created to be the parent of the GLOB if one is not provided to `build()`.
- `build()` is a context manager.  It yields the new tree
After any GlobalScope has been built, then any post-build methods may be called on any scope in its scope tree.

## Primitive Methods

A scope is specified by calling various primitive methods while traversing the scope's source.

- **`with scope.build(): ...`**  
    All other primitives are called in this context.  
    Afterwards,
    - the name of a Class or Function scope is bound in the parent scope.
    - the name of a Global scope, if given, is bound in the Root scope.  
    - for a Global scope, `scope._cleanup()` is called.
    - no more primitives are allowed.

- **`with scope.nest(kind, name = '') -> Scope: ...`**  
    Creates, and yields, a new scope enclosed in the current scope.  Includes new scope.build(), so all other primitives for the new scope are called within this context.
- **`scope.use(var: str)`**  Variable in a value reference.
- **`scope.bind(var: str, **kwds)`**  Variable in a binding reference.  
    Keyword `flags: VarCtx` indicates any binding flags that apply.  They are accumulated over multiple `bind()` calls for the same `var`.  
    
    The semantics are affected by these context managers:
    - **`with scope.use_walrus(): ...`**  
    Any `bind()` call is for the target in a `target := value` expression.
    - **`with scope.in_iterable(): ...`**  
    Only implemented by COMP.  Events in this context are part of the `iterable` expression in a `for var in iterable` clause.  All walrus expressions are `SyntaxError`s, including those in nested scopes (which includes LAMBs as well as COMPs).

- **`scope.decl_nonlocal(var: str)`**  In `nonlocal var`.
- **`scope.decl_global(var: str)`**  In `global var`.
- **`scope._cleanup()`**  
    Called implicitly at the end of `glob.build()` for any GlobalScope `glob`.  
    Then called recursively for all nested scopes in the tree.  
    * Any variable with a USE or NLOC_DECL context is resolved to either FREE or GLOBAL, using the [scope.binding](#scope.binding)`(variable)` method (detailed below).  In the case of FREE, it will raise a SyntaxError if the binding scope is not found.

    * Call `child._cleanup()` recursively for each child scope.
## Post-build Methods
These may be called after `outer._cleanup()` has been called for all `outer` scopes that enclose `scope`.
- [`scope.binder(var: str)`](Rules.md#binder-scope)` -> Scope`  
Returns the binding scope for `var`.

- [`scope.context(var: str)`](Rules.md#context-of-a-variable) and related `scope.usage(var: str)`, `scope.bind_flags(var: str)`, and `scope.type(var: str)`.  An enum which describes how a variable is used in the scope.

# Algorithms


## eval and exec methods

... to be provided ...

# Acknowledgments

This document started with an [essay](https://github.com/gvanrossum/gvanrossum.github.io/blob/main/formal/scopes.md) written by Guido van Rossum.
I removed the Toplevel scope.
I moved all the runtime discussion to a new document [namespaces.md](../scopetools/namespaces.md).

Otherwise, I simplified some definitions and revised the search algorithms.

