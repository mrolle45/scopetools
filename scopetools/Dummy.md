# Dummy
xx [^foo]

[^foo]: Bar

An AST has some **child** objects[^ASTChild], some of which can be other ASTs.  A non-AST child is called a **leaf**, or **AST leaf**

[^ASTChild]: The children of an AST node are found by looking at the class attribute `node._fields`, which is a tuple of attribute names.  Some nodes have other attributes that are not fields, and these are ignored.  

    The [ast grammar](https://docs.python.org/3.10/library/ast.html#abstract-grammar) shows the names and types of fields of each AST node class, in the form `class(field, ...)`.  

    For each `field` the node has 0 or more child objects, depending on the coding of `field` as shown in this table.  `T` is the type of the child.  `value` is the value of `node.name`.  

