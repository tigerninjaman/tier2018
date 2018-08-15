import re

pat1 = '(\w),? a ' + term + '\w? company'
pat2 = 'founder of (\w)'
pat3 = '(\w),? (?inc|INC)'
pat4 = '(\w)(? &)? (?co|Co)'
pat4 = 'the startup (\w)'
pat5 = '(\w),? a \w? ?\w ? startup'