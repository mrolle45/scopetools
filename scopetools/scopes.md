# All About Scopes

Michael Rolle, 2022

# Definitions

## Syntax Tree


### Ordering Relationship


For scope nodes, the node-to-item relationship is limited to a [subset of the items](#scope-syntax-items) in the node's syntax tree.

## Basic class
This is defined in `basic.py`.  It is the base class of `Scope`, and provides some useful definitions for any subclass that is related to scopes, such as `Namespace` in `namespaces.py`.

A **scope kind** is an enumeration (class `Basic.Kind`).  The members are also class attributes of `Basic`.

|      kind      |  node | Python code |
|:-------------|:------|:--
|ROOT | (see below) |
|GLOB|   ast.Module | entire module
|CLASS|   ast.ClassDef | `class` statement with decorators
|FUNC|   ast.FunctionDef |`def` statement with decorators
|LAMB|   ast.Lambda |`lambda` expression
|COMP|   ast.ListComp |`[expr for var in iter ...]`
|...|   ast.SetComp |`{expr for var in iter ...}`
|...|   ast.DictComp |`{key : expr for var in iter ...]`
|...|   ast.GeneratorExp |`(expr for var in iter ...)`

`ROOT` is used for the top of the tree structure

## Enclosing or Enclosed Scope

For any two scopes, either they are unrelated (that is, they cover disjoint segments of the program code), or else one covers a subset of the other.

In the latter case, the larger scope **encloses**, or it is an **enclosing scope** of, the smaller scope.  Likewise, the smaller scope **is enclosed by**. or it is an **enclosed scope** of, the larger scope.

In this document, it may also be expressed succinctly as **outer > inner** (or **inner < outer**).
## Parent or Child Scope

An outer scope is the **parent** of an inner scope, or the inner scope is a **child** of the outer scope, when
- parent > child, and
- There is no other scope such that parent > scope > child.

In a scope tree, every scope other than the RootScope has a parent, and every scope can be reached from the root by a series of children.

## Variable

A **variable** is almost any occurrence of a Python identifier in a syntax tree.  The grammar determines whether an identifier is a variable or not.

The exceptions are:
- Attributes, as in `(expression).attribute`, in an `ast.Attribute` node.
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

#### Binding reference
This implies that the variable is Local in the scope.  Refer to the [documentation](https://docs.python.org/3.10/reference/executionmodel.html#binding-of-names) for name binding. The possibilities are:
- An `ast.Name` node, where the context attribute is either `ast.Store()` or `ast.Del()`.  Yes, a `del variable` statement is considered binding.

  This includes a target name in:
    - an assignment statement.
    - an augmented assignment statement.
    - an annotated assignment statement, *except as noted below*.  `target` may be either `name` or `(name)`.
        If a value is assigned, as in `target: anno = value`, then this is treated as two statements:
        - `target: anno`.  
        - `target = value`.  This is handled like an ordinary assignment statement, as above, and is a binding reference for `name` in both cases.  

        If `target` is `name`, this is a binding reference.  The `anno` expression is evaluated and added to the `__annotations__` variable for a module or class.  
        If `target` is `(name)`, **this is not** a binding reference.  In fact, it has no effect at all.  It may be followed by a `global name` or `nonlocal name` without raising a syntax error.  
        Examples:
        ```py
       name: anno          # update __annotations__
       global name         # SyntaxError
       ```
        ```py
       name: anno = 0      # update __annotations__, assignname = 0
       global name         # SyntaxError
       ```
        ```py
       (name): anno        # evaluate anno
       global name         # OK
       ```
        ```py
       (name): anno = 0    # evaluate anno, assign name = 0
       global name         # SyntaxError
       ```
        
    - an assignment expression.  Note that the expresion can be contained within an [owned COMP](scopescommon.md#owned-comp).  This is termed a **walrus reference** if the scope itself is a COMP.
    - a 'for' statement target.
    - a 'for' clause in a COMP.
- The name in a function or class definition.  The home scope is the parent.
- A parameter name in a function definition.
- An imported name (module name or module member) or alias in an `as variable` clause.
- After `as` in a with statement or except clause, or in the as-pattern in structural pattern matching.
- In a capture pattern in structural pattern matching.

#### Walrus reference

This is a special case of a binding reference.  The scope is a COMP, and the reference is a walrus target in any [owned COMP](scopescommon.md#owned-comp).
#### Non-binding reference
This is simply the use of the current value of the variable, and does not affect the variable's context (defined below) in its scope (other than changing from Unused to Seen).
    This is any `ast.Name` node in which the context attribute is `ast.Load()`.  
Also, if the scope is a COMP, and variable is the target name of an assignment expression, and scope ->> target, this is a special "walrus" non-binding reference.  The sole purpose of this is to catch a syntax error where the same variable is an ordinary non-binding reference in the same scope.  
Examples:

```py
foo = bar  # 'foo' is binding and 'bar' is non-binding.
foo.append(1)  # 'foo' is a non-binding reference; 'append' is an attribute
import foo  # 'foo' is a binding reference
import foo.bar  # 'foo' is a binding reference;
                # 'bar' is part of the module name and not used in the scope.
```

### Walrus considerations

For an assigment expression within any COMP, the target item (`ast.NamedExpr.target`) is a binding reference for the [owner non-COMP scope](scopescommon.md#owned-comp) of the owned COMP.  That is, it skips over enclosing COMPs.  The COMP is owned by the home scope.

For example, at the top level, the owner scope of the expression `(variable := y)` in 

```py
# global scope
def f(
    # scope of f
    n = [
        # first comp scope 
        x for x in [0] if [
            # second comp scope
            (variable := y) for y in [42]
            ]
        ]
    ): pass
```
is the global scope.  It is neither the second COMP nor the first COMP because they are COMPs.  It is not the scope of `f` because it is part of a default argument value, which is not an item of the function scope.  The owner of the expression is the global scope

In addition, the following conditions are errors:

- The variable is a target in the 'for' clause of a COMP and is also a walrus target in any COMP [owned by it](scopescommon.md#owned-comp).
- A walrus occurs in an iterable clause in any COMP
  (even if as part of a lambda or another COMP).
- The owner scope is a class definition.

(For the walrus-related rules, see
[PEP 572](https://www.python.org/dev/peps/pep-0572/#scope-of-the-target).)

## Name Mangling
In a class, the compiler considers certain variable names as "private" to that class, by changing them to a different name which is (usually) different from the same name in a different class.  The idea is for the variable in that class to be different from the same variable (i.e., the same name) in a subclass or base class.

This is specified by a method  
 **`ClassScope.mangle(self, var: str) -> str`**.
A complete explanation is found in the [Python Tutorial](https://docs.python.org/3.10/tutorial/classes.html?highlight=mangled%20names#private-variables).  
In other `Scope` classes, this method simply returns `var`.  
As an example,
```py
class C:
    __variable = 3
    print(__variable)       # 3    
class D(C):
    __variable = 4
    print(__variable)       # 4
print(C._C__variable)       # 3
print(D._D__variable)       # 4
print(D()._C__variable)     # 3
print(D()._D__variable)     # 4
```

By the way, if `variable` is declared `nonlocal` or `global`, it is still mangled.  The mangled name is used in whatever is the binding scope.  
The [scope building primitives](#primitive-methods) automatically do the mangling (in a ClassScope only), so that the caller supplies the variable name as it appears in the syntax item.  This can, if necessary, be avoided with a `nomangle=True` argument to these primitives.  If the caller supplies a mangled name, this name will be used as-is.  
For any purpose other than building the current scope, an application should check for mangling any variable names it finds in a syntax tree within a class def.  The static method **`Basic.mangle(class_name: str, name: str) -> str`** can be used.  Or if an instance of the current `Scope` class is available, then its `scope.mangle(var)` can be called.

## Context of a variable

This is an enumeration `Scope.VarCtx` in the `Basic` class (a base class of `Scope`).  It describes how a variable is used in a scope.  It is returned by [scope.context(var: str)](#scope.context).
During the build of the scope, it may change.  
It can be one of:

- **Local**.  The variable appears in a binding reference in the scope, other than a [walrus reference](#walrus-reference).  Also, in a GlobalScope, if its context is Global in any enclosed scope.
- **Closure**.  The scope contains a `nonlocal variable` statement.
- **Global**.  The scope contains a `global variable` statement.
This does not apply in the global scope itself, in which it is redundant and ignored.
- **Seen**.  The variable appears (so far) in, and only in, a non-binding context.
- **Walrus**.  Only used in comprehensions.  The variable appears as a walrus target in any [owned COMP](scopescommon.md#owned-comp).
- **Unused**.  None of the above.  The initial state.

The Scope object records the contexts of all variables with other than Unused context.
At the beginning of the scope, the context of any variable is Unused.  This will change to one of the other contexts the first time the variable is used.  After that, the only allowed change is from Seen to Local.  Any other occurrence of the variable raises a SyntaxError.

Each occurrence of an identifier has exactly one context.
Context is determined purely by the grammar.

The method `scope.context(var: str)` returns a `VarCtx` object for the context.  This may change before the entire scope's text has been built.

## Closed and open scopes

FUNC, LAMB and COMP scopes are **closed scopes**.
At runtime, the known variable names cannot be extended dynamically
(e.g. by monkey-patching).

All other scopes are **open scopes**.  At runtime, additional variables can be associated with the scope.

## Binding scope of a variable

This is determined at compile time for any scope and variable name.  It is the home scope, or some scope which encloses it.  It is denoted by the method

`scope.binding_scope(var: str) -> Scope`

The algorithm for this is contained [below](#scope.binding_scope).

The variable is always *Local* in its binding scope.

A fundamental idea here is that a variable is considered to be **the identical variable** in both the home scope and the binding scope.  At runtime, any changes to the variable are seen in both scopes.

At runtime, any binding operation is always performed in the binding scope.  However, the current value of a variable is not always its value in the binding scope.  This is discussed in the [namespaces](namespaces.md) document.

Note: this cannot be computed until the *entire* module text has been processed and `outer._cleanup()` has been called for every `outer` which encloses `scope`.

## Closure scope of a variable

This concept is related to the determination of the binding scope.
It is denoted by the method call

`scope._closure_scope(var: str) -> Scope | None`

The algorithm for this is detailed [below](#scope._closure_scope).

The closure for a closed scope where `var` has Local context, is itself.
The closure for a closed scope where `var` has Global context, is None.
The closure for the global scope is None.
Otherwise, the closure is the closure of its parent.

Note: this cannot be computed until the *entire* module text has been processed and `outer._cleanup()` has been called for every `outer` which encloses `scope`.

## Scope for eval() and exec()

These functions do not have the same effect as their code strings would have if located in the same place directly in the scope.  The difference is in the value of a variable which is captured from an enclosing scope.  If there is a nonlocal declaration in the scope, then the results are the same.  Otherwise, the value in the global scope is used (or a NameError is raised).

The **eval scope** of a variable is the scope in which `eval()` will find the value.  It uses the `globals()` and `locals()` values at the point where `eval()` is called.

**exec scope** is another name for 'eval scope'.

The **local scope** of a variable is the same, if it is found in `locals()`, otherwise it is a NameError.  It is in `locals()` if its context is either Local or Closure, but not if it is Capture or Global.

These are implemented by the methods `scope.eval_scope(var)`, `scope.exec_scope(var)` and `scope.locals_scope(var)`, *resp.*, which are detailed below.

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
    - **`with scope.in_iterable(): ...`**  
    Only implemented by COMP.  Events in this context are part of the `iterable` expression in a `for var in iterable` clause.  All walrus expressions are `SyntaxError`s.

- **`scope.decl_nonlocal(var: str)`**  In `nonlocal variable`.
- **`scope.decl_global(var: str)`**  In `global variable`.
- **`scope._cleanup()`**  
    Called implicitly at the end of `glob.build()` for any GlobalScope `glob`.  
    Then called recursively for all nested scopes in the tree.  
    1. Any variable with a Free, Seen or Closure context is resolved to either Closure or Global, using the `scope.binding_scope(variable)` method (detailed below).  In the case of Closure, it may raise a SyntaxError.
    2. Call `child._cleanup()` recursively for each child scope.
## Post-build Methods
These may be called after `outer._cleanup()` has been called for all `outer` scopes that enclose `scope`.
- **`scope.binding_scope(var: str) -> Scope`**  
Returns the binding scope for `var` (defined above and detailed below).

# Algorithms

## Scope.context
Scope.context(self, var: str) -> VarCtx

The context of a variable is determined by a state machine which responds to certain events, which correspond to some `ast` nodes in the program.  These are applied in the program order.  
The current context of any `var` which is not Unused is kept in the `Scope` object.  The absence of a current context means that the context is Unused.

| Event | Unused | Seen | Local | Closure | Global | Walrus
|---|---|---|---|---|---|---| 
| Initial context | Unused | -- | -- | -- | -- | -- 
| Any non-binding reference to `var` | Seen
| [Walrus reference](#binding-reference) to `var` | Walrus | Walrus | error | n/a [^impossible] | n/a [^impossible]
| Any other binding reference to `var` | Local | Local | | error | error | n/a [^impossible]
| A `nonlocal var` statement | Closure | error | error | | error | n/a [^impossible]
| A `global var` statement | Global | error | error | error | | n/a [^impossible]
| cleanup() with closure scope | | Closure 
| cleanup() with no closure scope | | Global | | error 

[^impossible]: Not possible because a COMP does not contain any statements (*i.e.* `nonlocal` or `global`), nor any binding reference other than a walrus reference.

## Scope.binding_scope()

The method `scope.binding_scope(var)` returns the Scope (if any) where `var` is bound.  Implementation varies by the context of `var`.
The result is None if the context is Closure but there is no scope found.

```py
def binding_scope(self, var: str) -> Scope | None:
    context = self.context(var)
    if context is Global: return global scope
    if context is Local: return self
    closure = self._closure_scope(var)
        if closure: return closure
        if context is Closure:
            raise SyntaxError
        else:
            return global scope
```

## Scope.binding()
This is the same as `scope.binding_scope(var)`, but it returns a `Scope.VarBind` object.  This has attributes:
- `scope: Scope | None` = the Scope (if any) returned by `binding_scope(var)`
- `anno: bool` = if there was a `var: annotation` statement, with or without an assignment.
- `param: bool` = if `var` is a function parameter.  It can also be annotated.
- `nested: bool` =  if `var` is the name of a nested CLASS or FUNC.

## Scope._closure_scope()
This is an internal helper method used to find the binding scope of a variable in a Closure context.

The method `Scope._closure_scope(var) -> Scope | None` works by searching from the scope along the parent chain, looking for a *closed* scope in which the var is Local.  The search fails if it reaches a scope in which the var is Global, or if it reaches the global scope.

```py
def _closure_scope(self, var: str) -> Scope | None:
    if self is global scope: return None
    if self.context(var) is Global: return None
    if self is closed and self.context(var) is Local: return self
    else: return self.parent._closure_scope(var)
```

## eval and exec methods

... to be provided ...

# Acknowledgments

This document started with an [essay](https://github.com/gvanrossum/gvanrossum.github.io/blob/main/formal/scopes.md) written by Guido van Rossum.
I removed the Toplevel scope.
I moved all the runtime discussion to a new document [namespaces.md](namespaces.md).

Otherwise, I simplified some definitions and revised the search algorithms.

