sample="""
⊢ ((¬p → q) → (¬p → ¬p))\n
1.⊢ (A → (B → C)) → ((A → B) → (A → C))...AX2\n
2.⊢ (¬p → (B → C)) → ((¬p → B) → (¬p → C))...Sub1[A:=¬p]\n
3.⊢ (¬p → (q → ¬p)) → ((¬p → q) → (¬p → ¬p))...Sub2[C:=¬p,B:=q]\n
4.⊢ (A → (B → A))...AX1\n
5.⊢ (¬p → (q → ¬p))...Sub4[A:=¬p,B:=q]\n
6.⊢ ((¬p → q) → (¬p → ¬p))...MP3,5
"""

AX1="A → (B → A)"
AX2="(A → (B → C)) → ((A → B) → (A → C))"
AX3="(¬B → ¬A) → (A → B)"


from sympy.logic.boolalg import Or, And, Not, Implies
from sympy import symbols, sympify
from sympy.logic import simplify_logic
from sympy.parsing.sympy_parser import parse_expr
import re

class RawImplies(Implies):
    @classmethod
    def eval(cls, lhs, rhs):
        # completely disable evaluation
        return None

def remove_outer_brackets(s):
    if not s or s[0] != '(' or s[-1] != ')':
        return s  

    depth = 0
    for i, char in enumerate(s):
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        if depth == 0 and i < len(s) - 1: # not fully wrapped
            return s
    return s[1:-1] # fully wrapped

def parser(s):
    if type(s) == list:
        s = "".join(f"({item})" for item in s)
    if type(s)!=str:
        print("Parsing error, wrong type entered")
    s=remove_outer_brackets(s)
    s=s.replace(" ", "")
    stack = []
    result = []
    skip=False
    current_str=""
    for i, char in enumerate(s):
        if skip:
            skip=False
            continue
        if char == '(':
            stack.append(i)
        elif char == ')':
            if stack:
                start = stack.pop()
                # Extract the content inside the current matching parentheses
                if stack==[]:
                    result.append(s[start + 1:i])
        elif stack==[]:
            if char == "¬" and (len(s)>2) and i!=len(s)-1 and s[i+1].isalpha():
                # print(s[i:i+2],"eeee")
                result.append(s[i:i+2])
                skip=True
            else:
                result.append(char)
    # print(s,result)
    return result
    
def make_sympy(s:str):
    array=parser(s)
    # print(array)
    answer=None
    if len(array)==1 and isinstance(array[0], str) and len(array[0]) == 1:
        char=array[0]
        if not char.isalpha():
            print("Error: lone floating operator",char)
            return
        return symbols(char)
    for i,item in enumerate(array):
        if item == "¬":
            if i==len(array)-1:
                print("Error: floating ¬")
                return
            # print(item,array[i+1],"!!!!!!!!!")
            answer=Not(make_sympy(array[i+1]), evaluate=False)
            # print(item,array[i+1],":")
            # print(answer,"..........")
            # wont nessisarily break
        if item == "→":
            if i==0 or i==len(array)-1:
                print("Error floating →")
                return
            if answer:
                # print(answer,"→",make_sympy(array[i+1:]),":")
                answer=RawImplies(answer,make_sympy(array[i+1:]), evaluate=False)
                # print(answer,"......")
            else:
                # print(make_sympy(array[i-1]),"→",make_sympy(array[i+1:]),":")
                answer=RawImplies(make_sympy(array[i-1]),make_sympy(array[i+1:]), evaluate=False)
                # print(answer,".....")
            break
        # if i==len(array)-1:
            # print("ERROR no operators")
    return answer

# print(make_sympy("¬(¬B → ¬A) → ¬(A → B)"))

axiom1=make_sympy(AX1)
axiom2=make_sympy(AX2)
axiom3=make_sympy(AX3)

class proof_line:
    def __init__(self,expr,step):
        self.expr=expr
        self.step=step

def check_proof(lines):
    target=lines[0]
    works=True
    for i,line in enumerate(lines):
        if i==0:
            continue
        step=line.step.replace(" ","")
        print("Testing:",step,line.expr)
        if step.lower()=="premise":
            continue
        elif step.lower()=="ax1":
            if line.expr != axiom1:
                works=False
                break
        elif step.lower()=="ax2":
            if line.expr != axiom2:
                works=False
                break
        elif step.lower()=="ax3":
            if line.expr != axiom3:
                works=False
                break
        elif re.search(r"sub[0-9]+\[([a-z]:=[a-z¬→\(\),]+)+\]",step.lower()):
            substr=re.search(r"\[([a-zA-Z]:=[a-zA-Z¬→\(\),]+)+\]",step).group(0).replace("[", "").replace("]", "")
            subint=int(re.search(r"[0-9]+",step).group())
            if subint>=i or subint<=0:
                works=False
                break
            items = [item.strip() for item in substr.split(',')]
            # print(items)
            subby=lines[subint].expr
            for item in items:
                thing=re.search(r"([a-zA-Z]):=([a-zA-Z¬→\(\)]+)",item)
                LHS=symbols(thing.group(1))
                RHS=make_sympy(thing.group(2))
                subby=subby.subs(LHS,RHS)
            if subby!=line.expr:
                works=False
                print("NO SUBSITUION WRONG!!!")
                print(subby)
                print(line.expr)
                break
        elif re.search(r"mp[0-9]+,[0-9]+",step.lower()):
            print("MODES PONENENENENEN")
            mpstr=re.search(r"mp([0-9]+),([0-9]+)",step.lower())
            mpint1=int(mpstr.group(1))
            mpint2=int(mpstr.group(2))
            if mpint1>=i or mpint2>=i or mpint1<=0 or mpint2<=0:
                works=False
                break
            mp1=lines[mpint1].expr
            mp2=lines[mpint2].expr
            if mp1.func!=RawImplies and mp2.func!=RawImplies:
                works=False
                break
            if mp1.func==RawImplies:
                LHS,RHS=mp1.args
                if LHS==mp2 and RHS==line.expr:
                    works = True
                    break
                else:
                    works=False
            if mp2.func==RawImplies:
                LHS,RHS=mp2.args
                if LHS==mp1 and RHS==line.expr:
                    works = True
                    break
                else:
                    works=False
        else: 
            print("AAAAAAA",step.lower())
            works=False
            break
    if works:
        print("yippeeeee!")
    else:
        print("WOMP WOMP")

test_line1=proof_line(axiom2,"ax 2")
# test_line=proof_line(make_sympy("(¬p → (q → ¬p)) → ((¬p → q) → (¬p → ¬p))"),"Sub1[C:=¬p,B:=q,A:=¬p]")

test_proof=[
proof_line(make_sympy("((¬p → q) → (¬p → ¬p))"),""),
proof_line(make_sympy("(A → (B → C)) → ((A → B) → (A → C))"),"AX2"),
proof_line(make_sympy("(¬p → (B → C)) → ((¬p → B) → (¬p → C))"),"Sub1[A:=¬p]"),
proof_line(make_sympy("(¬p → (q → ¬p)) → ((¬p → q) → (¬p → ¬p))"),"Sub2[C:=¬p,B:=q]"),
proof_line(make_sympy("(A → (B → A))"),"ax 1"),
proof_line(make_sympy("(¬p → (q → ¬p))"),"Sub4[A:=¬p,B:=q]"),
proof_line(make_sympy("((¬p → q) → (¬p → ¬p))"),"MP3,5")]

# print("thingyyy")
# for line in test_proof:
#     print(line.expr,line.step)
check_proof(test_proof)
# class RawImplies(Implies):
#     @classmethod
#     def eval(cls, lhs, rhs):
#         # completely disable evaluation
#         return None
# p, B, C = symbols("p B C")
# # Build unevaluated structure
# expr = RawImplies(
#     RawImplies(~p, RawImplies(B, C)),
#     RawImplies(RawImplies(~p, B), RawImplies(~p, C))
# )

# print("before:", expr)

# subby = expr.subs(C,~p)
# print("after:", subby)
