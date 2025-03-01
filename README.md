# NFA-and-DFA
1.NFA.py
- The function epsilon_closure receives a state of the automaton and returns a set of states, which represent the states that can be reached only by epsilon-transitions from the initial state (without consuming any characters)
- The subset_construction function will return an AFD, built from the current AFN by the subset construction algorithm. The returned AFD will have states type frozenset[STATE]. We use frozenset instead of set, because the latter is not immutable (sets can be modified by side effects). We need an immutable object to be able to calculate a hash (always the same), and implicitly to be able to use such objects as keys in a dictionary (something impossible if the key object is mutable).
- The remap_states function has the same format and purpose as the function from AFDs

2.DFA.py
- In this class you will have to implement the accept function, which receives a word and simulating the execution of the AFD on that word will return True if the word is accepted, and False otherwise.
- The minimize function minimizes the DFA

3.Regex.py
- Implementation of the thompson method, the method that receives a regex type object and returns an NFA (with int type states as a convention). The regex received as input will have the form shown

regex ::= regexregex |
regex '|' regex | 
regex'*' | regex'+' | regex'?' | 
'(' regex ')' | 
"[A-Z]" |
            "[a-z]" |
            "[0-9]" |
            "eps" | character

- two new operations:
  - plus + -> the expression to which it is applied appears 1 time or more.
  - the question mark ? -> the expression to which it is applied appears once or never.
- 3 syntactic sugars:
  - [a-z] - any lowercase letter in the English alphabet
  - [A-Z] - any uppercase character in the English alphabet
  - [0-9] - any number

4.Lexer.py 
- divides a character string into substrings called lexemes, each of which is classified as a token, based on a specification. The specification contains a sequence of pairs (tokens, regexes)
 where each token is described by a regular expression
- We have the specifications by which we manage to identify the tokens that match best according to correctness, length and priority
  - example:
    - the specifications are spec = [("C", "c"), ("ABS", "(ab)+"), ("BS", "b*")]
    - input : "bbbcbbabbc"
    - result : [
					("BS", "bbb"),
					("C", "c"),
					("BS", "bb"),
					("ABS", "ab"),
					("BS", "b"),
					("C", "c"),
				]

5.Parser.py
- the parser receives input that can also be lambda expressions that are processed using the grammar for example
  - \x.(x * (x + 2)) -> Lambda (var "x") -> Mul (var "x") (Parent (Plus (var "x") (val 2)))
