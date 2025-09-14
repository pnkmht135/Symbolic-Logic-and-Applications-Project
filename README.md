# Documentation for proof checker and LLM proof generator
Note: AI was used to help with sympy module syntax.

## Libraries and preliminaries
- The sympy library was to represent the symbolic logic expressions.
- the re library to handle the string outputs of the LLM proof generator.
- The LLM used is llama3 from ollama, hosted locally and fitted with a system message as seen in "Modelfile".

## How to use

##### Set up:
Make sure you have ollama installed, and create a correctly named model using the Modelfile provided.
The terminal command to do this is: 
**`ollama create Prop_llama -f Modelfile`** on windows.
Note: this reqires llama3, which is 4.7GB and requires the model file to be in the same directory in which you are running the terminal command.

##### Running:

Create and run a cell calling the "make_and_check_proof()" function (no parameters needed). You will be prompted to enter your desired proof.
Make sure the proof you enter is formatted correctly:  
- Use the symbols "→" and "¬" for Implies and Not respectively (if needed you can copy paste these from the examples listed in the notebook).
- Only use alphabets, round brackets, "→" and "¬" for writing the formlae themselves. Do not use numbers or any other symbols (spaces are ok).
- Make sure whatever conclusion you wish to derive is preceeded by a "⊢".
- Make sure any premises specified are comma seperated and preceed the "⊢" symbol.

Examples of valid inputs:
⊢((¬p → q) → (¬p → ¬p))
p→q,q→r,p ⊢r

The model may requre a few minutes to run, once it does it will print out the LLM generated proof along with either "VALID PROOF" if the proof generated is valid, or "INVALID PROOF" along with an error message otherwise.

## Function explainations and use cases

### 1. remove_outer_brackets()
Helper function that removes brackets that encapsulate entire string, if they exist.
eg: (xyz) ==> xyz
does not change strings such as (xyz)pqr(abc).
### 2. parser()
Helper function to parse an input string of a propositional logic formula to return an array containing each (ordered) component of the formula, where sub-formulae within brackets are treated as one unit.
eg: (abc)→¬(xyz) ==> ["abc","→","¬","xyz"]

Can also take in an array in order to handle a case where make_sympy() function calls it on an array of paresed elements to the right of an implication sign needed since ["abc","→","¬","xyz"] is correct syntax formula
Parses ¬+atomic proposition (eg: ¬A) together when the two symbols do not compose the entire formula.

### 3. make_sympy() and RawImplies subclass
Recursive function to turn propositional logic formulae from an input string to a sympy format.
Only handles the "Implies" and "Not" logical operators, since those are the only ones present in Łukasiewicz's P2.
Utilises a custom subclass, "RawImplies", of sympy's "Implies" which is set such that formulae are not automatically evaluated when constructed. 

### 4. check_proof() and proof_line class
The proof_line class is used to define each line from a proof as an object containing the expression of said line (self.expr) and the step used in the line to obtain the expression (self.step).

The check_proof() function takes in an array of proof lines (forming a proof) and checks if the given proof is valid or not by checking the expression of each proof line against its step as well as any previous proof lines reffered to by its step (eg: steps Sub1[...] and MP2,4 refer to lines 1, and 2 and 4 respectively).
If any proof line fails to align with its step, the function return "INVALID PROOF" as well as an error corresponding to the misalignment.

##### Steps and their validity checks:
- premise: no validity check needed
- axiom introduction (AX1,2,3): compare line expression against axiom listed in the line step
- Subsitution: compare line expression against the outcome of preforming all subsitutions detailed in the line step on the line number mentioned in the step. Also checks if the line number mentioned in the step is valid, e.i. refers to an existing line that is listed before the current line.
- Modus ponenes: checks if the first line reffered to in the line step is an implies() expression, then compares the LHS of the fist line to the second line reffered to in the line step and compares the RHS of the first line to the current line expression. Also checks if the line number mentioned in the step is valid, e.i. refers to an existing line that is listed before the current line.
- Final validity: checks expression of the final line against the target conclusion (which is always the first element fo the proof array) to see if the derived conclusion matches the target.

### 5. make_and_check_proof()
Function that requests an input of a desired proof from the user, calls the LLM to generate said proof, parses the proof and then checks the proof.

- The function extracts the desired proof conclusion from input to add as the target conclusion (first element) in the proof array
- Passes desired proof to LLM to generate the proof
- The LLM is instructed by the system message not to include any text besides the proof, and to preceed each proof line by its step number.
-  Sometimes the LLM restates or rewrites the desired proof conclusion before begining the proof steps. Whenever it does this, the rewriten conclusion does not have a step number, so make_and_check_proof() checks for this and ignores such lines.
- Otherwise, the function extracts the expression and step from each line using regular expressions and helper functions, and makes them into a proof_line which then constructs a proof array to be passed to check_proof function.
