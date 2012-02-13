from apps.seqsee.sobject import SObject, LTMStorableSObject
from farg.codelet import Codelet, CodeletFamily
from farg.exceptions import FargError, FargException
from farg.focusable_mixin import FocusableMixin
from farg.ltm.storable import LTMStorableMixin
import logging


logger = logging.getLogger(__name__)

# TODO(# --- Feb 10, 2012): Find a better home
class CF_DescribeAs(CodeletFamily):
  @classmethod
  def Run(cls, controller, item, category):
    if not item.IsKnownAsInstanceOf(category):
      item.DescribeAs(category)

class NonAdjacentGroupElementsException(FargException):
  """Raised if group creation attempted with non-adjacent parts."""
  def __init__(self, items):
    FargException.__init__(self)
    self.items = items

  def __str__(self):
    return ', '.join(str(x) for x in self.items)

# This class has more than 7 attributes, disable that pylint check.
# pylint: disable=R0902
class SAnchored(LTMStorableMixin, FocusableMixin):
  """An object with position information.
  
  .. warning:: This way of doing things differs from the way in Perl, where I was
    subclassing instead of just having an sobject as a member.
  """
  def __init__(self, sobj, items, start_pos, end_pos, is_sequence_element=False):
    FocusableMixin.__init__(self)
    #: The object which is anchored.
    self.object = sobj
    #: The items --- sub-anchored-objects --- that make up this object. Empty if this has no
    #: structure (i.e., it holds an SElement).
    self.items = items
    #: The start position. The first element in the workspace has position 0.
    self.start_pos = start_pos
    #: The end position. Note that this is the rightmost edge (unlike, say, in the case
    #: of iterators, where end is beyond the rightmost item).
    #: For an element, left and right edges are identical.
    self.end_pos = end_pos
    #: All items in the workspace --- what used to be elements and groups in the Perl
    #: version --- are SAnchored objects now. This bit distinguishes elements that are
    #: elements in the sequence.
    self.is_sequence_element = is_sequence_element
    #: What metonym does this have? Metonym, if present, is a SObject.
    self.metonym = None
    #: Is the metonym active?
    self.is_metonym_active = False
    #: Relations.
    self.relations = set()

  def __str__(self):
    return 'Anchored (%d, %d): %s' % (self.start_pos, self.end_pos, self.Structure())

  def SetPosition(self, start_pos, end_pos):
    """Sets the end-point of the anchored object."""
    self.start_pos = start_pos
    self.end_pos = end_pos

  def Span(self):
    """Returns a 2-tuple with start and end points."""
    return (self.start_pos, self.end_pos)

  def Structure(self):
    """The structure of the contained object."""
    return self.object.Structure()

  def GetLTMStorableContent(self):
    structure = self.Structure()
    return LTMStorableSObject(structure=structure)

  def GetStorable(self):
    structure = self.object.Structure()
    return (structure, str(structure))

  @staticmethod
  def Create(*items, **kwargs):
    """Given a list of items, each a SAnchored, creates another SAnchored, provided that the
       items are contiguous. Raises a NonAdjacentGroupElementsException if they are
       non-adjacent.
       
       The only acceptable kwarg is 'underlying_mapping'
    """
    underlying_mapping = kwargs.pop('underlying_mapping', None)
    assert(not kwargs)
    if not items:
      raise FargError("Empty group creation attempted. An error at the moment.")
    if len(items) == 1:
      if isinstance(items[0], SAnchored):
        return items[0]
      else:
        raise FargError("Attempt to SAnchored.Create() from non-anchored parts: %s" %
                        items[0].__repr__())

    # So there are multiple items...
    for item in items:
      if not isinstance(item, SAnchored):
        raise FargError("Attempt to SAnchored.Create() from non-anchored parts: %s" %
                        item.__repr__())
    # .. Note:: This can probably be speeded up and cleaned up.
    left_edge, right_edge = items[0].Span()
    for item in items[1:]:
      left, right = item.Span()
      if left != right_edge + 1:
        raise NonAdjacentGroupElementsException(items=items)
      right_edge = right
    new_object = SObject.Create(list(x.object for x in items))
    new_object.underlying_mapping = underlying_mapping
    if underlying_mapping:
      from apps.seqsee.categories import MappingBasedCategory
      new_object.DescribeAs(MappingBasedCategory(mapping=underlying_mapping))
    return SAnchored(new_object, items, left_edge, right_edge)

  def AddRelation(self, relation):
    self.relations.add(relation)

  def GetRelationTo(self, other):
    return [x for x in self.relations if (x.first == other or x.second == other)]

  def GetRightwardRelations(self):
    return [x for x in self.relations if x.first == self]

  def GetFringe(self, controller):
    """Gets the fringe (needed for stream-related activities)."""
    fringe = { 'pos:%d' % self.start_pos: 0.6,
               'pos:%d' % self.end_pos: 0.6,
               'pos:%d' % (self.end_pos + 1): 0.3,
               'pos:%d' % (self.start_pos - 1): 0.3}
    fringe.update(self.object.GetFringe(controller))
    return fringe

  def GetAffordances(self, controller):
    logging.debug('GetAffordances called for %s', self)
    codelets = []
    from apps.seqsee.codelet_families.all import CF_FocusOn
    for relation in self.relations:
      # QUALITY TODO(Feb 10, 2012): Whether to add a relation-focusing codelet should depend
      # on its confidence, whether it is internal (part of a group), and other considerations.
      codelets.append(Codelet(CF_FocusOn, controller, 25, focusable=relation))
    my_node = controller.ltm.GetNodeForContent(self)
    outgoing_isa_edges = my_node.GetOutgoingEdgesOfTypeIsa()
    for edge in outgoing_isa_edges:
      # QUALITY TODO(Feb 10, 2012): Category activation and edge strength relevant here.
      category = edge.to_node.content

      # The following appears to repeatedly check; However, note that the link in the LTM
      # suggests that the categorization is possible.
      if not self.object.IsKnownAsInstanceOf(category):
        codelets.append(Codelet(CF_DescribeAs, controller, 25,
                                item=self.object, category=category))
    return codelets

  def GetSimilarityAffordances(self, other, other_fringe, my_fringe, controller):
    logging.debug('GetSimilarityAffordances called: [%s] and [%s] ', self, other)
    if not isinstance(other, SAnchored):
      return ()
    left, right = sorted((self, other), key=lambda x: x.start_pos)
    # Do they overlap?
    if left.end_pos >= right.start_pos:
      # They overlap. So we will want to form a bigger group...
      from apps.seqsee.codelet_families.overlapping_groups import CF_ActOnOverlappingGroups
      return [Codelet(CF_ActOnOverlappingGroups, controller, 100,
                      left=left, right=right)]
    else:
      # So both are anchored, and have overlapping fringes. Time for subspaces!
      urgency = 100.0 / (right.start_pos - left.end_pos)  # denominator is at least 1.
      from apps.seqsee.get_mapping import CF_FindAnchoredSimilarity
      return [Codelet(CF_FindAnchoredSimilarity, controller, urgency,
                      left=left, right=right)]