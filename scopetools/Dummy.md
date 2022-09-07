# Dummy
xx [^foo]

[^foo]: Bar

An AST has some **child** objects[^ASTChild], some of which can be other ASTs.  A non-AST child is called a **leaf**, or **AST leaf**

[^ASTChild]: The children of an AST node are found by looking at the class attribute `node._fields`, which is a tuple of attribute names.  Some nodes have other attributes that are not fields, and these are ignored.  
