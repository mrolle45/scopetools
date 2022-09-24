# Building a Tree

This document explains how to build a tree using functions and methods in the [treebuild](../scopetools/treebuild.py) module.

A tree is any instance of `ScopeTree[TreeT, SrcT]`.  `TreeT` is a base class of the tree and all its ancestors and descendants, and is a subclass of `ScopeTree`

The term **scope tree** means that `TreeT` is the `Scope` class.

The term **general tree** means that `TreeT` is some subclass of `ScopeTree` other than `Scope`.  A general tree refers to some scope tree with an identical tree structure, using the attribute `tree.scope`.  An application can have several general trees, even some trees of identical tree types, with the same scope tree.

This distinction is made because the structure of these tree types differs slightly, and their method of building these is different.

A tree is built one module at a time, resulting in a GLOB tree for the module, which is a child of a single ROOT object.

The components needed to build a tree are:
- A **ROOT tree**.  There is a function to create one.  A new one will be created if one is not provided.  If several modules are involved, they will all have to provide the same ROOT.
- A **source** object, of type `SrcT`, for the module.

  It is also possible to create some other kind of scope instead of a GLOB.  In this case the source for that scope is provided, and an unnamed GLOB will be created to be the parent of the new tree.
- A **traverser** object, which has methods to examine the source object and find various program elements in it.  The traverser is stored in the GLOB object.
- A **scope tree**, if a general tree is being created.  If one is not provided, then a source tree is built from the source and the traverser.
- A **builder**, which manages the build.  It creates the new GLOB tree and all its descendants, and provides static information to them.

The tree can be built from either (1) a source and a traverser, or (2) a scope tree.

## `treebuild.build()` Function

This creates a new tree, called `newtree`, and all its descendants, and fills them with static information.  
If `newtree` is not a GLOB, then a new GLOB is created as parent for `newtree`.  
The new GLOB will have a given ROOT as parent, or if one is not provided, a new ROOT is created.  
It returns `newtree`.

Arguments to `build()`:

- `cls: Type[TreeT]`,  
The class used to construct `newtree`.  `cls.tree_type` must be defined.  
If `cls.kind` is not defined, then `newtree` will be an instance of `cls.tree_type` and `newtree.kind` will be the kind provided in the call (or GLOB if the kind is not provided).
- `root: TreeT = None`,  
a ROOT object which will be the root of the tree hierarchy.  
If not provided, then a new ROOT is created instead.  
- `name: str = ""`,  
module name for the new GLOB.  Not required.
- `builder: Builder = None`,  
This is to allow the caller to provide a subclass of `Builder` to perform extra functionality.  Default is a new `Builder` instance.  

Either (1) arguments when creating `newtree` directly ...
- `src: SrcT = None`,  
 The source object (required in this case)
- `trav: Traverser[SrcT] = None`,  
The traverser.  Default is a new traverser for `SrcT` = `ast.AST`.  
    `common args...)`
- `kind: Kind = None`,
Used to determine the actual class of `newtree` if `cls.kind` is not defined.  Otherwise it must agree with `cls.kind`.

Or (2) arguments when creating general `newtree` with existing scope tree ...
- `scopes: Scope = None,`  
The scopes tree (required in this case), used as `newtree.scope`.  
The `scopes.src`, `scopes.glob.trav`, and `scopes.kind` attributes are used in place of the above arguments of the same names.  These arguments may also be provided in (1), but they must be identical.

### Building a Scope Tree

Only the form (1) of arguments is used.  `cls` must be a subclass of `Scope`.

- `newtree` is constructed, using `cls`, `src`, and `kind`.
- A GLOB scope tree is constructed as `newtree.parent` if `newtree` is not itself a GLOB.  Sets `GLOB.name` = `name`
` A ROOT scope tree is constructed as `GLOB.parent` if `root` argument is not provided.
- Initializes `builder` with `builder.init(trav, newtree)`.  This also initializes `trav` to use `builder` and `newtree.glob` to use `trav`.
- Calls `trav.visit(newtree.src).  This finds items in `src`, which are reported to `builder` and then forwarded to its current tree.  Nesting events create a nested tree, temporarily make it the current tree, visit the new tree with the traverser, then return to the original tree.
- Performs a cleanup on the GLOB tree and all its descendants, and marks them all as being built.
### Building a General Tree

With form (1) of the arguments:
- Build a `scopes` object by calling `build()` with the same arguments, except using `cls=the subclass of Scope corresponding to kind`.
- Use form (2), with `scopes=scopes` to create `newtree`.

With form (2) of the arguments:
- Create a GLOB tree using `cls`.
- Create descendants for GLOB corresponding to descendants of `scopes.glob`
- Recursively, for each `tree`, `scope`, and child `scope_child` of `scope`:
    - Create `tree_child` as a child of `tree`, with the same kind as `scope_child`
    - Set `tree_child.scope` = `scope_child`.
    - Perform this process with `tree_child` and `scope_child`.
- Mark all new trees as being built.
- Create ROOT tree, if not provided, and make GLOB a child.
- Return `newtree`.

## The Traverser

A traverser is an instance of `Traverser[SrcT]`.  Its job is to find program elements by examining a source object and then report them to its builder.

The elements in the source vary in nature with the type `SrcT`.  But the builder's methods are defined independently of `SrcT`.  These methods may have another `src` keyword for something representing the elements, if available.

The traverser is initialized by `trav.init(builder: Builder)`.

All attributes of the traverser that are not defined therein will be delegated to the builder.  For example, `trav.xyz` is `trav.builder.xyz`.  This is a convenience for coding the traverser.

A source object is inspected by **`trav.visit`**`(src: SrcT)`.  This is recursive.  Visiting `src` can lead to other child objects, and so `trav.visit(src)` may call `visit(child)`.

### Events
While examining the source object, the traverser will find things which correspond to elements of the program.  Some of these elements are of interest to the tree being built, and are called **event elements**.  Examples would be a class definition or a variable name.

An **event** is a call to a corresponding method of the builder, which is termed **reporting** the event.

## The Builder

A builder is an instance of `Builder[TreeT, SrcT]`.  Its job is to create an **origin** tree, create all descendants of the origin, and set the state of all of these trees.  
The origin is kept in **`builder.orig`**.  It is usually a GLOB.  However, an application may want to work with some smaller scope in a module, and use the corresponding `Scope` as the origin.  The origin is never a ROOT.  
The constructor for the origin fills in the tree hierarchy above the origin, using optional `root` and `name` parameters given to the builder:
- If the origin is not a GLOB, then a new GLOB is created, with the origin as its child.
- `origin.glob`, in either case, is given the name `name`, if provided.
- If `root` is not provided, then a new ROOT is used.
- In either case, `origin.glob` is added as a child of `root`.  

**`builder.glob`** is the GLOB tree in the hierarchy.  Usually it is the same as the origin.  In general, `builder.glob` is `builder.orig.glob`.

### The Current Tree
At any time, the attribute **`builder.curr`** is the origin or some descendant thereof.  The builder **navigates** the tree hierarchy (that is, changes `builder.curr`) in response to nesting events.

All state methods are delegated to the current tree.  For example, `builder.use(var)` calls `builder.curr.use(var)`.

A custom Builder subclass could override some of these state methods.

### Nesting events
Some program elements specify a new scope, which is a child of the scope it is contained in.  The traverser handles this using a context manager provided by the builder:
```py
with self.nest(..., src=child_src) as child_tree:
    The buider creates a nested child_tree and navigates to it.
    Report events found in child_src.
    The builder navigates back to the earlier tree.
```

Occasionally the traverser will need to report an item to the parent scope while traversing the source of a child scope.  It can do this with:
```py
with self.use_parent() as parent_tree:
    The builder navigates to the parent of the current tree.
    Report elements to the parent tree.
    The builder navigates back to the earlier tree.
```

- An example of this is that within a COMP scope, there are several iteration clauses, as in `for targ1 in iter1 for targ2 in iter2 ...`  The *first* iterable (`iter1`) is evaluated, and hence reported, to the parent scope of the COMP.  Thus the traverser could use `with self.use_parent(): self.visit(source of iter1)` (or otherwise report elements within `iter1`).  See `treebuild.ASTTraverser.visit_comp()

### State events
These are events which deal with a single category of the tree state.
These are described [here](scopescommon.md#tree-state-methods)

### Compound events
These are events which affect more than one category of the tree state.
The `Builder` class breaks these up into individual state events and reports them.
However, a custom subclass of `Builder` could override an event method and in some way report to the current tree that it all came from the same source.
- **`tree.anno(var: str, anno: str, param: bool = False)`**
This binds the variable as an annotated variable (and possibly also as a function parameter) and also reports the annotation as a typing state method.  The `ScopeTree` base class implements this as:
    ```py
    self.bind(var, anno=True, param=param) # static state
    self.type_hint(var, anno) # typing state
    ```
    - Curiously, a function parameter can have *both* an annotation *and* a type comment.  This is allowed by the grammar and is accepted by `ast.parse()`.  mypy reports this as an error, even if the types are the same.  A traverser should also raise a SyntaxError.  If there is an annotation or a type comment, whichever one is present is reported as the `anno` parameter.

- **`tree.anno_store(var: str, anno: str, value: ValT)`**  
This performs the assignment and then notes the annotation.  The `ScopeTree` base class implements this as
    ```py
    typ = anno or type_comment
    self.anno(var, typ)    # compound, see above
    self.store(var, value) # dynamic state
    ```  

- Any method which has a **`type_comment`** keyword argument.  
    It is a combination of the same event, but without the type comment, and a separate type hint for the comment.
    The `ScopeTree` base class implements this as
    ```py
    def xxx(self, var: str, ..., type_comment: str = ''):
        if type_comment:
            self.type_hint(var, type_comment) # typing state
        return self.curr.xxx(var, ...) # without the type comment
    ```

