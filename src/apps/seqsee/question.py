from tide.question.question import BooleanQuestion

class AreTheseTheNextTermsQuestion(BooleanQuestion):
  def __init__(self, terms):
    BooleanQuestion.__init__(self, 'Are these the next few terms: %s?' % terms)
