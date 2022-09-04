# Running Tests

This mostly[^othertests] describes the module [scopestest.py](scopestest.py).  This is a standalone module, to be run separately as a script.

[^foo]
Its purpose is twofold:
- Verify that the models for scope and namespace behavior in Python are correct.
- Check that the code implementing those models is correct.

Performing the test has these steps:
1. [Build](#Building-the-Tree) a `ScopeTree`.  
2. [Generate](#Generating-Python) the code for a Python module, which creates a parallel tree structure of scopes, and has items to set or get various static and dynamic properties of the scopes.
3. [Perform](#Dynamic-Methods) dynamic state methods on the tree objects.
4. [Execute](#Executing-the-Python-Module) the Python code.  In addition to creating the scopes and getting/setting state properties, it verifies that the actual result of a dynamic getter agrees with the corresponding result in step 3.
5. [Verifiy](#Comparing-Trees) that the scope trees in steps 1 and 2 agree.

## The Variable Name

All static and dynamic properties involve a single variable names `x`, or `__x` if testing in mangle mode.  This name will be designated by the name **`var`**.
## Building the Tree

The first thing that `scopestest` does is build a `Scope` tree, and a `Namespace` tree which uses the scope tree.

The GLOB tree contains several child CLASS and FUNC trees, which in turn each contain several child CLASS and FUNC trees, and so on, up to a depth of 3 (which can be altered with a command line argument).  Some of these lowest level trees have some **helper** child objects (either a COMP or a FUNC).

The tree is built using a custom builder and traverser.  This provides an **example of how to define and use these custom classes**.  It uses a custom scope source class, which is used by the traverser to describe each scope tree being built.

Each tree in the overall tree structure has certain properties, which are specified by its corresponding `tree.src` object:
- kind, either CLASS or FUNC.
- position in the hierarchy.  `level` is the distance from the GLOB, and `depth` is the distance to the bottom level.
- mode, specifying how `var` is used within the scope.
- nocapt.  If true, then nested scopes cannot capture `var` as a nonlocal variable.

## Generating Python
## Dynamic Methods
## Executing the Python Module
## Comparing Trees
[^othertests]: Some other modules in the package, when run as standalone scripts, contain a few simple tests to verify that their functionality works.  You can run them as part of a test suite.
- [namespaces.py](namespaces.py)
- [scopes.py](scopes.py)
- [treebuild.py](treebuild.py)
[^foo]: footnote