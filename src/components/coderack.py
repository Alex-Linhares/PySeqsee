import random

class CoderackEmptyException(Exception):
  """Raised if :func:`~Coderack.GetCodelet` called on an empty coderack."""
  pass

class Coderack:
  """Implements the coderack --- the collection of codelets waiting to run.
  
  .. todo:: Choose the codelet to expunge based on a better criteria than uniformly randomly.
  """

  def __init__(self, max_capacity):
    #: Maximum number of codelets that the coderack can hold.
    self._max_capacity = max_capacity
    #: Sum of urgencies of all codelets in coderack.
    self._urgency_sum = 0
    #: Number of codelets present.
    self._codelet_count = 0
    #: The set of codelets.
    self._codelets = set()

  def IsEmpty(self):
    """True if contains no codelets."""
    return (self._codelet_count == 0)

  def GetCodelet(self):
    """Randomly selects a codelet (biased by urgency). Requires the coderack to be nonempty."""
    if self._codelet_count == 0:
      raise CoderackEmptyException()
    random_urgency = random.uniform(0, self._urgency_sum)
    # The following loop is guarenteed to terminate.
    for codelet in self._codelets:
      if codelet.urgency >= random_urgency:
        self._RemoveCodelet(codelet)
        return codelet
      else:
        random_urgency -= codelet.urgency

  def AddCodelet(self, codelet):
    """Adds codelet to coderack. Removes some existing codelet if needed."""
    if self._codelet_count == self._max_capacity:
      self._ExpungeSomeCodelet()
    self._codelets.add(codelet)
    self._codelet_count += 1
    self._urgency_sum += codelet.urgency

  def _RemoveCodelet(self, codelet):
    """Removes named codelet from coderack."""
    self._codelets.remove(codelet)
    self._codelet_count -= 1
    self._urgency_sum -= codelet.urgency

  def _ExpungeSomeCodelet(self):
    """Removes a codelet, chosen uniformly randomly."""
    codelet = random.choice(list(self._codelets))
    self._RemoveCodelet(codelet)
