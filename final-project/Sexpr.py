import sys

# note: this parser requires full sentences to be on 1 line
# case-sensitive (a!=A)
# '#' is comment char (anywhere on line)
# no quotes
# all chars besides ( and ) are treated as parts of tokens
# top level is assumed to be only 1 Sexpr (atom or list), not multiple exprss automatically enclosed in parens; could be singleton prop

def tokenize(s):
  toks = []
  i,n = 0,len(s)
  while i<n:
    if s[i]==' ': i += 1; continue # skip whitespace
    elif s[i]=='(' or s[i]==')': toks.append(s[i]); i += 1; continue
    else:
      j = i
      while j<n and s[j] not in " ()": j += 1 # scan for end of token
      toks.append(s[i:j])
      i = j
  return toks

# takes string, or tokenized list of strings, or empty as input

class Sexpr:
  def __init__(self,toks=None,i=0): # i is index in token list
    self.atom = None
    self.list = []
    self.next = i 

    if toks==None: return # this is effectively a constructor for "empty" Sexpr instances
    if isinstance(toks,str): toks = tokenize(toks)

    # parse expr
    n = len(toks)
    if i>=n: return # empty list
    if toks[i]=='(':
      i += 1
      while i<n and toks[i]!=')':
        expr = Sexpr(toks,i)
        self.list.append(expr)
        i = expr.next # index in toks
      if i==n: raise Exception("syntax error: list not closed: %s" % ' '.join(toks))
      self.next = i+1; return
    elif toks[i]==')': self.next = i; return # this is not my close paren; parent might be interested in it
    else: self.atom = toks[i]; self.next = i+1; return

  def copy(self):
    temp = Sexpr() # make an empty copy
    temp.atom = self.atom
    temp.list = [x.copy() for x in self.list]
    temp.next = self.next
    return temp
  
  def toString(self):
    if self.atom!=None: return self.atom
    else: 
      x = ' '.join([x.toString() for x in self.list])
      return "(%s)" % x

  # assume expr is a clause

  def toDIMACS(self):
    if self.atom!=None: return self.atom
    lits = ""
    for arg in self.list[1:]:
      if arg.atom!=None: lits += " "+arg.atom
      else: lits += " -"+arg.list[1].atom # assume it is a neg lit
    return lits.strip()

###############################

# could make these member functions...

def isVar(expr): return expr.atom!=None and expr.atom[0]=='?'

def isConst(expr): return expr.atom!=None and expr.atom[0]!='?'

def isliteral(expr): return expr.atom!=None or (expr.list[0].atom=='not' and expr.list[1].atom!=None) # what about upper-case?

def negate(expr):
  if expr.atom==None and expr.list[0].atom=='not': return expr.list[1]
  return construct_Sexpr(["not",expr])

# a list of Sexpr's or strings (which will get converted to atoms, not tokenized?)

def construct_Sexpr(exprlist):
  newexp = Sexpr()
  newexp.list = [Sexpr(x) if isinstance(x,str) else x for x in exprlist] # convert strings to Sexpr's
  return newexp

# assume expr is: (not <list>)
# transform: (not (or X1 .. Xn)) -> (and (not X1) .. (not Xn))
# transform: (not (and X1 .. Xn)) -> (or (not X1) .. (not Xn))
# transform: (not (implies A B)) -> (and A (not B)) - implication elimination + negation
# transform: (not (not X)) -> X - double-negation elimination

def demorgan(expr): 
  # assume expr.list[0].atom=='not'
  sub = expr.list[1]
  oper = sub.list[0].atom
  if oper=='and': newexp = construct_Sexpr(["or"]+[negate(x) for x in sub.list[1:]])
  elif oper=='or': newexp = construct_Sexpr(["and"]+[negate(x) for x in sub.list[1:]])
  elif oper=='not': newexp = sub.list[1] # (not (not X)) -> X, double negation elim.
  elif oper=='implies':
    LHS,RHS = sub.list[1],sub.list[2]
    newexp = construct_Sexpr(['and',LHS,negate(RHS)])
  else: print("error in demorgan()"); sys.exit(0)
  return newexp

########################################################
# strip-out comments; skip blank lines

def read_file_one_expr_per_line(fname):
  exprs = []
  for line in open(sys.argv[1]):
    if '#' in line: line = line[:line.find('#')]
    line = line.strip()
    if len(line)==0: continue
    a = Sexpr(line)
    exprs.append(a)
  return exprs

# assuming balanced parens

def find_close_paren(s):
  cnt,lparens = 0,0
  for i in range(len(s)):
    if s[i]=='(': 
      cnt += 1
      lparens += 1
    if s[i]==')': 
      cnt -= 1
      if cnt==0 and lparens>0: return i
  print("error: unbalanced parens")
  sys.exit(0)

def read_file_multiline(fname):
  S = ""
  for line in open(sys.argv[1]):
    if '#' in line: line = line[:line.find('#')]
    line = line.strip()
    if len(line)==0: continue
    S += " "+line

  exprs = []
  i,n = 0,len(S)
  while i<n:
    j = find_close_paren(S[i:])+1
    estr = S[i:i+j]
    a = Sexpr(estr)
    exprs.append(a)
    i += j

  return exprs
  

########################################################

if __name__=="__main__":
  #exprs = read_file_one_expr_per_line(sys.argv[1])
  exprs = read_file_multiline(sys.argv[1])
  for e in exprs: 
    print(e.toString())