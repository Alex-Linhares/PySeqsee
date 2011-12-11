"""Argument processing for Seqsee."""
import argparse
import logging
import sys

from apps.seqsee.gui.gui import SeqseeGUI

# Corresponding Perl code in Seqsee.pm

def ParseSeqseeArguments():
  parser = argparse.ArgumentParser(
      description="Seqsee: A cognitive architecture for integer sequence "
                  "perception")
  parser.add_argument('sequence', metavar='N', type=int, nargs='+',
                      help='terms of the sequence')
  parser.add_argument('--coderack_size', default=10, type=int)
  parser.add_argument('--ui',
                      help='Type of ui (cmdline, gui, batch)',
                      choices=['cmdline', 'gui', 'batch'],
                      default='gui')
  parser.add_argument('--unrevealed_terms',
                      help='Extra terms (which Seqsee will ignore expcept in batch mode)',
                      default='')
  parser.add_argument('--debug', default='', help='Logging level')

  # Parse
  args = parser.parse_args()

  # Validate and Pre-process
  if args.ui is 'gui':
    args.ui = SeqseeGUI
  else:
    print "%s is not a supported UI (yet)" % args.ui
    sys.exit(1)

  args.unrevealed_terms = [int(x) for x in args.unrevealed_terms.split()]

  if args.debug:
    numeric_level = getattr(logging, args.debug.upper(), None)
    if not isinstance(numeric_level, int):
      raise ValueError('Invalid log level: %s' % args.debug)
    logging.basicConfig(level=numeric_level)

  return args
