sample="""
⊢ ((¬p → q) → (¬p → ¬p))\n
1.⊢ (A → (B → C)) → ((A → B) → (A → C))...AX2\n
2.⊢ (¬p → (B → C)) → ((¬p → B) → (¬p → C))...Sub1[A:=¬p]\n
3.⊢ (¬p → (q → ¬p)) → ((¬p → q) → (¬p → ¬p))...Sub2[C:=¬p,B:=q]\n
4.⊢ (A → (B → A))...AX1\n
5.⊢ (¬p → (q → ¬p))...Sub[A:=¬p,B:=q]\n
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

def parser(s:str):
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
    print(s,result)
    return result
    
def make_sympy(s:str):
    array=parser(s)
    answer=None
    if len(array)==1 and isinstance(array[0], str) and len(array[0]) == 1:
        char=array[0]
        if not char.isalpha():
            print("Error: lone floating operator",char)
            return
        return char
    for i,item in enumerate(array):
        if item == "¬":
            if i==len(array)-1:
                print("Error: floating ¬")
                return
            # print(item,array[i+1],"!!!!!!!!!")
            answer=Not(make_sympy(array[i+1]))
            break # wont nessisarily break
        if item == "→":
            if i==0 or i==len(array)-1:
                print("Error floating →")
                return
            if answer:
                answer=Implies(answer,make_sympy(array[i+1]))
            else:
                answer=Implies(make_sympy(array[i-1]),make_sympy(array[i+1]))
            break
        if i==len(array)-1:
            print("ERROR no operators")
    return answer
# print(parser(parser(AX3)[0]))
print(make_sympy(AX3))

# recursive function that splits shit by brackets 
