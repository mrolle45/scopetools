# scopetools -- a Tools Package for Analyzing Scopes in Python Code.

By Michael Rolle, September, 2022.  Comments to < m at rolle dot name >.

There are three major purposes for the files in this repository.

## Define the Precise Rules for Semantics of Variable Names

This is found in [Rules.md](docs/Rules.md).

### Scope Rules

This all pertains strictly to compile time aspects of the code.

Specifies what is a Scope in Python code.

Specifies what is a Variable in Python code.  It is an identifier in the Python grammar, but not all identifiers are variables.

Which scope does the variable **belong** to.  Every grammar element, not just variables, belongs to exactly one scope.

Which scope does the variable **resolve** to.  This is, in effect, the *identity* of the variable.  Two variables in the code are the **same variable** if they have the same name (adjusting for private names) and resolve to the same scope.  That means that at run time, any changes (assignments or deletions) to the variable in any ns are visible to any other occurrence of the identical variable.

### Namespace Rules

This pertains to runtime aspects of the code.

How a ns is created and its relationship to a scope.

The hierarchy of namespaces.  It parallels the hierarchy of their corresponding scopes.  This is a *lexical* property, rather than a *temporal* one.

The dynamic state of a ns.  That is, what variable names are currently bound and to what values.

Which ns does a variable operation **resolve** to.  This is most commonly the ns in the hierarchy which corresponds to the scope which it resolves to.  But not always, in the case of some variable lookups; it can be some other ns in the current hierarchy.

In whichever ns the operation resolves to, the variable is looked up, or (re)bound, or deleted.

## Implement these Rules in Python Code

### Scopes

This is found in [scopes.py](scopetools/scopes.py).  Details are found in [scopes.md](docs/scopes.md).

It contains methods for recording things of interest that affect a variable in a scope, based on examination of the Python code.

After the *entire* top level (a module, usually) has been examined, there are methods for resolving a variable name, following the rules in Rules.md.

### Namespaces

This is found in [namespaces.py](scopetools/namespaces.py).  Details are found in [namespaces.md](docs/namespaces.md).

There are methods for recording runtime operations that pertain to a variable in the ns.  These are presumed to occur in the same order that they occur while executing the ns.

After each operation, the dynamic state of the ns which the operation resolves to may be updated.

## Verify the Rules and their Implementation

This is covered in [Testing.md](docs/Testing.md).

The major test is performed by running [scopestest.py](scopetools/scopestest.py) as a script with the scopetools directory on the import path.  It constructs a huge number (hopefully enough to cover every possible edge case) of nested scopes and variable operations, predicts the current value of the variable, and compares it to the actual runtime value of the variable.

Certain other modules in the package can be run standalone to provide simpler verifications of the implementation.

