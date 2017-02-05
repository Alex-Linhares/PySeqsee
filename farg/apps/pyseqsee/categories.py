"""Defines the categories for objects."""
from farg.core.meta import MemoizedConstructor
from farg.apps.pyseqsee.objects import PSElement

class InstanceLogic(object):
  """Describes how an item is an instance of a category.

    TODO(amahabal): What about cases where an item can be seen as an instance of a category in a
    number of ways? When that happens, there are rich possibilities for creation of novel categories
    that we should not miss out on. Punting on this issue at the moment.
    One way to achieve this would be to add the method ReDescribeAs to categorizable, which will
    not use the stored logic; it will then look at the two logics and perhaps merge.
  """

  def __init__(self):
    pass

class PyCategory(metaclass=MemoizedConstructor):
  pass

class CategoryAnyObject(PyCategory):
  def IsInstance(self, item):
    return InstanceLogic()

class CategoryEvenInteger(PyCategory):
  def IsInstance(self, item):
    if not isinstance(item, PSElement):
      return None
    if item.magnitude % 2 != 0:
      return None
    return InstanceLogic() 

class MultiPartCategory(PyCategory):
  """Category whose instances are made up of N different parts.

  Each part can specify its own category.
  """

  def __init__(self, *, parts_count, part_categories):
    pass