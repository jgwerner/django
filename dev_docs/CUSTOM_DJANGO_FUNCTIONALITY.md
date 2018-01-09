# Custom Django Functionality
This document outlines ways in which we have either extended or modified Django's default functionality. If something
is behaving in a manner different than you would expect, this document may have an explanation.


## namespace
Namespaces correspond to either a user or a team. The queryset managers for many of our models make
use of this method. It is used like this: `Project.objects.namespace(request.namespace)`. Note that the argument
is expected to be a namespace object, not a string. This method is crucial in avoiding naming collisions. This method 
_should_ be implemented in a `managers.py` file in the same app as the model in question. This needs to be standardized.


## tbs_<get|filter>
The `tbs_get` and `tbs_filter` methods are defined in `base/models.py`. Most of our heavily used models define a 
QuerySet manager class that inherits from `TBSQuerySet`, which is the base class that defines these methods. They can be
overridden of course.

The purpose of these two methods is to allow filtering on either a UUID primary key, or an object's name (or equivalent 
identifier) without knowing the type ahead of time. For example:
```python
Project.objects.tbs_filter("MyProjectName")
```

will ascertain that `"MyProjectName"` must be the projects name, and will filter as such.


## NATURAL_KEY
Any model that makes use of `tbs_<filter|get>` must define this as a class attribute. `NATURAL_KEY` is simply
the model field which humans would typically identify an object by. This is what allows using `tbs_filter` without
passing the field name as an argument.


## is_active
Many models define `is_active`. The `tbs_<filter|get>` methods automatically search for objects where `is_active=True`,
unless `is_active` is explicitly passed to the method call. It is important to make sure inactive records are removed
from API results in order to avoid naming collisions.