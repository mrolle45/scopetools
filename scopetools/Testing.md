# Running Tests

This mostly[^othertests] describes the module [scopestest.py](scopestest.py).  This is a standalone module, to be run separately as a script.

Its purpose is twofold:
- Verify that the models for scope and namespace behavior in Python are correct.
- Check that the code implementing those models is correct.

Performing the test has these steps:
1. [Build](#Building-the-Tree) a `ScopeTree`.  
2. [Generate](#Generating-Python) the code for a Python module, which creates a parallel tree structure of scopes, and has items to set or get various static and dynamic properties of the scopes.
3. [Perform](#Dynamic-Methods) dynamic state methods on the tree objects.
4. [Execute](#Executing-the-Python-Module) the Python code.  In addition to creating the scopes and getting/setting state properties, it verifies that the actual result of a dynamic getter agrees with the corresponding result in step 3.
5. [Verifiy](#Comparing-Trees) that the scope trees in steps 1 and 2 agree.

The above may be run **twice**.  The second time is done in [mangled mode](#Mangled-Mode), unless suppressed in the [command line](#Command-Line-Arguments).  Separate Python code is generated, but line numbers are as though it is appended to the code from the first run.

## The Variable Name

All static and dynamic properties involve a single variable names `x`, or `__x` if testing in [mangled mode](#Mangled-Mode).  This name will be designated by the name **`var`**.
## Building the Tree

The first thing that `scopestest` does is build a `Scope` tree, then a `Namespace` tree which uses the scope tree.

The GLOB tree contains several child CLASS and FUNC trees, which in turn each contain several child CLASS and FUNC trees, and so on, up to a depth of 3 (which can be altered with a command line argument).  Some of these trees have some [**helper**](#Helper-Scopes) child objects (either a COMP or a FUNC).

The tree is built using a custom builder and traverser.  This provides an **example of how to define and use these custom classes**.  It uses a custom scope source class, which is used by the traverser to describe each scope tree being built.

### Tree source
Each tree in the overall tree structure has certain properties, which are specified by its corresponding **`tree.src`** object:
- kind, either CLASS or FUNC for nested scope, GLOB for the GLOB scope, and either FUNC or COMP for a helper scope.  
For a CLASS, the class name is `A`, `B`, *etc.* based on the level in the hierarchy.  
For a FUNC, the class name is `a`, `b`, *etc.* based on the level in the hierarchy.  
In both cases, the above class name is appended to the name of the parent tree (if this is not the GLOB).
- position in the hierarchy.  `level` is the distance from the GLOB, and `depth` is the distance to the bottom level.
- mode, specifying how `var` is used within the scope.  Each mode adds a suffix to the scope's name.  

#### Tree Modes
| mode | suffix | prolog | modifies? | captures? |
|:--|:--|:--|:--|:--|
| Unused | (none) | | | |
| Used | _use | var | | |
| Anno | _anno | var: str | | |
| Nonlocal | _nloc | nonlocal var | Yes | Yes |
| Global | _glob | global var | Yes | Yes |
| Local | _loc | | Yes | Yes |
| NoCap [^nocap] | _ncap | | Yes | |

[^nocap]: Same as Local, except for limited set of nested scopes.

The source for the GLOB scope has mode = Local.

### Child Trees
A [helper scope] has no child trees.
Otherwise, a tree has the following child trees, in that order:

1. Except at the bottom level, a CLASS child for each possible mode.
  - *However*, if the tree or any of its ancestors has NoCap mode, then only modes which [capture](#Tree-Modes) `var` are used.
2. Corresponding FUNC children.

If the mode [modifies](#Tree-Modes) `var`, then  

2. Two [helper scopes](#Helper-Scopes).  
3. The same child trees as in 1. and 2., but "2" is suffixed to the scope names.

### Helper Scopes
When a tree modifies the binding of `var`, as indicated by its mode, then it has two **helper** child scopes, in this order:
1. A **setter**, which sets `var` = some value based on the scope's qualified name.  
In some cases, where this is possible, the helper is a list comprehension containing a walrus assignment; this illustrates the use of assignment expressions inside comprehensions.  
Otherwise, the helper is a FUNC which declares `var` as either global or nonlocal and performs the assignment.
2. A **deleter**, which deletes `var`.  
This is always a FUNC which declares `var` as either global or nonlocal and performs the delete.

Both of these operations take place in the parent scope of the helper scope.  They have the same effect as `var = something` and `del var`, respectively, appearing in the parent scope.

## Generating Python
The Python code is generated at the same time as the Scope and Namespace trees are being created (above step), using the source objects for the GLOB tree and all its descendants.  
The Builders define some custom event methods which create the helper scopes.
For all FUNC scopes (including helpers), the generated code calls the function immediately following the definition.
The code for each scope contains the following, in order:
1. [Prolog](#Tree-Modes) usage of `var`, according to mode.
0. Test `var`.
0. The rest appear in some order...
- Generate [child trees](#Child-Trees). 

- If the current scope's mode [modifies](#Tree-Modes) `var`:

  - Set `var` directly, and test it.
  - Delete `var` directly, and test it.

     These may appear twice each.
  - Test `var` after each helper scope.  
  - The binding state of `var` will be the sme at the end of the scope code as at the beginning.  That is, whether `var` has a current value and, if so, the current value.  

**Exception**, with an unresolvable nonlocal variable, the [alternate code](#Unresolved-Nonlocals) is generated instead of the above.  There will be no child scopes or helpers.

### Test Operations

Basically, after every operation that either assigns or deletes `var`, a call to a function `test(value, expected)` is made.  The value is the variable name (evaluated in Python), and the expected value comes from calling `tree.load(var)` on the current Namespace tree if `var` is bound at this time, or None otherwise.
If `var` is not bound at runtime, it will raise a NameError, and the handler will call `test(None, expected`).
`test()` will raise an exception if the value and expected value are not equal.

### Unresolved Nonlocals

A special situation occurs when the tree has Nonlocal mode, but there is no enclosing scope in which the variable name is resolved.  To declare it as nonlocal would raise a SyntaxError in the generation of the Scope tree, so that is not possible.  
Instead, the tree code calls `compile("nonlocal {var}")`  If this raises a SyntaxError, then the test passes, otherwise the test fails.  
The unresolved condition is detected by searching the ancestors chain starting with the current tree, skipping over any CLASS trees.  If a Glob mode is reached, or the GLOB tree, the condition is true.  If the mode is Anno or Local, the condition is false.

## Dynamic Methods

These are called while building the Namespace tree.

As it is generating code to store or delete `var`, it calls the corresponding methods on the current tree.  
Each time a test is generated, the builder gets the expected value using `tree.has(name) and tree.load(name) or None`.  
To support the proper sequence of stores and deletes, the builder calls `tree.has_bind(var)`.  This simply checks whether the binding namespace has a binding or not, and does not look elsewhere if not.

## Executing the Python Module

After the Python code has been generated, it is executed using `exec(prolog + code)`.  `prolog` is a few lines which define the `test()` and `error()` that are called in `code`.

If there is a failure of any test, `exec()` raises an exception.  This exception includes the line number of the failed test.  A few lines surrounding the failed test are printed.  The exception is reraised, so that the remainder of the testing is skipped.

## Comparing Trees

This verifies that the tree structure in the generated Python `code` matches the tree structure of the Namespace tree.

It also serves as an illustration of building a Namespace tree from parsing `code` into an `ast.AST` syntax tree.

Here, **`orig`** means the Namespace tree generated originally, and **`py`** means the Namespace tree created from the parsed `code`.

The two trees aren't identical in all resects.  The function `compare(orig, py)` does verify:
- They have the same name (COMP trees are exempted from this).
- They have the same values, if any, for `var`.  That is, they are both unbound, or they are bound to the same value and have the same binding scope (same scope name).
- They have comparable nested trees.  They have the same number of them.  The corresponding nested trees for `orig` and `py` pass, recursively, `compare()`.

# Mangled Mode

The tests can optionally be run in **mangled mode**.  This is the same as the [standard tests](#Running-Tests), with these differences:
- The name of the variable `var` is "__x", not "x".
- If a scope `b` is the binding scope for `var` for a descendant `b`, *and* `var` is mangled to a name `mang`,  
then anything in `b` which uses `var` will have a duplicate which uses `mang`.
- Most uses of `var` automatically replace it with the mangled name.  However, where `var` appears as a literal string or an attribute name, then the mangled name is used in the literal string.
- Due to a compiler bug, `mang` appears instead of `var` where the bug would be encountered with `var`.  This is a setter [helper](#Helper-Scopes) that uses a COMP child.

# Command Line Arguments

These are used when `scopetest` is run as a script.

```
usage: scopestest.py [-h] [-d {2,3,4}] [-s] [-t] [-o O] [--nomangle]

optional arguments:
  -h, --help  show this help message and exit  
  -d {2,3,4}  Depth of the scopes and namespaces tree (default 3)  
  -s          Save the output file  
  -t          Copy the output file to file with ".txt" appended to the name  
  -o O        Output file name (default "sc_test.py")  
  --nomangle  Skip tests with mangled names  
```

If running the mangled mode test, the output file (if requested) is a concatenation of the code generated by both runs.

The `-t` option is useful for an editor which would choke on the Python file of such a size.

The `-d2` option is mainly useful for debugging.  Two levels are not enough to test all situations, some of which require three levels of nested scopes.  However, it runs much faster.

The `-d4` option is for someone who wants to run a more thoroug test.  It has so many tests (around 500,000) that it is broken up into 14 parts, each one having a single level-1 child tree; and it will not write an output file.


[^othertests]: Some other modules in the package, when run as standalone scripts, contain a few simple tests to verify that their functionality works.  You can run them as part of a test suite.  
    - [namespaces.py](namespaces.py)
    - [scopes.py](scopes.py)
    - [treebuild.py](treebuild.py)
