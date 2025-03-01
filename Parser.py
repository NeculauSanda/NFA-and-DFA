from .DFA import DFA
from .NFA import NFA
from .Regex import Regex, parse_regex
from .Lexer import Lexer


class Parser():
    def __init__(self, input: str = None) -> None:
        self.input = input
        self.lexer = Lexer([
            ("VAL", r"[0-9]+"),  # valori numerice
            ("VAR", r"[a-zA-Z]+"),  # variabile
            ("LAMBDA", r"\\"),
            ("DOT", r"\."),
            ("LPAREN", r"\("),
            ("RPAREN", r"\)"),
            ("OP", r"[+*/-]"),
            ("SPACE", r"\\ ")
        ])

        self.tokens = []
        self.current = 0 # indexul la care ne aflam in lista de tokens
        self.without_para = False # flag pentru a sti daca suntem in paranteze sau nu
        self.nr_open_para = 0 # numarul de paranteze deschise
    
    def parse(self, input: str = None) -> str:
        # this method should parse the input string and print the result of the parsing process
        
        self.tokens = self.lexer.lex(input) # lista de tokens
        self.current = 0

        result = self.parse_expression()
        return result

    def skip_spaces(self):
        # daca avem TOKEN-UL SPACE, trecem peste el
        while self.current < len(self.tokens) and self.tokens[self.current][0] == "SPACE":
            self.current += 1

    def parse_expression(self):
        self.skip_spaces() # trecem peste space

        if self.current >= len(self.tokens):
            raise ValueError("Sfarsit de expresie")
        
        token, value = self.tokens[self.current]
        
        # Variabila sau valoare numerica, salvam ca rezultat, deoarece nu stim daca dupa se mai afla o alta operatie
        # fara paranteze si v-om avea nevoie de rezultatul din stanga, adica valorile
        if token == "VAR":
            self.current += 1
            self.skip_spaces()
            result =  f"Var \"{value}\""
        
        elif token == "VAL":
            self.current += 1
            self.skip_spaces()
            result = f"Val {value}"
        
        # expresia lambda
        elif token == "LAMBDA":
            self.current += 1
            self.skip_spaces()
            token, value = self.tokens[self.current]

            if token != "VAR":
                raise ValueError("lambda asteapta variabila")
            
            var = value # salvam variabila
            self.current += 1
            self.skip_spaces()
            token, value = self.tokens[self.current]
            if token != "DOT":
                raise ValueError("Asteapta '.' dupa variabila lambda")
            
            self.current += 1
            self.skip_spaces()
            body = self.parse_expression() # parsam corpul expresiei lambda
            return f"Lambda (Var \"{var}\") -> {body}"
            
        # Expresie în paranteze
        elif token == "LPAREN":
            self.without_para = True # setam flag-ul la True pentru a sti ca suntem in paranteza\paranteze
            self.nr_open_para += 1 

            self.current += 1
            self.skip_spaces()

            #analizam corpul expresiei din stanga
            left = self.parse_expression()

            #cautam operatia din interiorul parantezelor
            self.skip_spaces()
            token, value = self.tokens[self.current]
            if token not in {"OP"}:
                raise ValueError(f"Asteapta operatie, a primit {token}")
            operatie = value # operatia

            self.current += 1
            self.skip_spaces()

            # analizam corpul expresiei din dreapta
            right = self.parse_expression()

            # vedem daca gasim paranteza inchisa
            self.skip_spaces()
            token, value = self.tokens[self.current]
            if token != "RPAREN":
                raise ValueError("Trebuia ')' dupa expresie")
            self.current += 1
            self.skip_spaces()
            
            operatie_token = {
                "+": "Plus",
                "-": "Minus",
                "*": "Mult",
                "/": "Div"
            }
            
            # eliminam din parantezele deschise
            self.nr_open_para -= 1 
            # daca nu mai avem paranteze deschise, setam flag-ul la False
            if self.nr_open_para == 0:
                self.without_para = False
            
            # cand am ajuns la finalul expresiei si observam ca dupa ce inchidem toate parantezele, mai avem token-uri in continuare
            # salvam rezultatul si nu-l afisam direct, deoarece asta v-a fi corpul STANG al expresiei atunci cand avem operatii fara paranteze
            # ex  (x + y) * z. Daca nu mai avem operatii se afiseaza direct
            if self.current + self.nr_open_para < len(self.tokens):
                result = f"Parant ({operatie_token[operatie]} ({left}) ({right}))" 
            else: 
                return f"Parant ({operatie_token[operatie]} ({left}) ({right}))"
            
        else:
            raise ValueError(f"TOKEN GRESIT: {token}")
        
        # facem operatiile care nu se afla intre paranteze si apelam DOAR ATUNCI CAND NU SUNTEM IN ALTE PARANTEZE
        # ex: 5 + x sau x + (y * z)-> '+' sau (x + y) * z
        if self.current < len(self.tokens) and self.tokens[self.current][0] == "OP" and not self.without_para:
            token_op, operatie_value = self.tokens[self.current] 
            self.current += 1
            self.skip_spaces()
            # analizam corpul expresiei din dreapta
            right = self.parse_expression()
            operatie_token = {
                "+": "Plus",
                "-": "Minus",
                "*": "Mult",
                "/": "Div"
            }
            result = f"{operatie_token[operatie_value]} ({result}) ({right})"

        # afisam atunci cand nu avem operatii cu paranteze
        return result