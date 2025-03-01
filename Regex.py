from typing import Any, List, Set, Tuple
from .NFA import NFA
from dataclasses import dataclass
# from src.DFA import DFA

EPSILON = ''

class Regex:
    def thompson(self) -> NFA[int]:
        raise NotImplementedError('the thompson method of the Regex class should never be called')

# you should extend this class with the type constructors of regular expressions and overwrite the 'thompson' method
# with the specific nfa patterns. for example, parse_regex('ab').thompson() should return something like:

# >(0) --a--> (1) -epsilon-> (2) --b--> ((3))

# extra hint: you can implement each subtype of regex as a @dataclass extending Regex


@dataclass
class Character(Regex):
    char: str

    def thompson(self) -> NFA:
        start = 0
        end = 1
        nfa = NFA(
            S={self.char},
            K={start, end},
            q0=start,
            d={(start, self.char): {end}},
            F={end}
        )
        return nfa

# STAR, QUESTION SI PLUS sunt la fel, dar difera doar o tranzitie
@dataclass
class Star(Regex):
    expr: Regex

    def thompson(self) -> NFA:
        nfa = self.expr.thompson()

        start = 0
        final = 1
        offset = 2 # nr de stari adaugate in plus

        nfa = nfa.remap_states(lambda x: x + offset) 

        nfa.K.update({start, final})

        nfa.d[(start, EPSILON)] = {nfa.q0, final}
        nfa.d[(nfa.F.pop(), EPSILON)] = {nfa.q0, final}

        
        nfa.q0 = start
        nfa.F = {final}

        return nfa


@dataclass
class Plus(Regex):
    expr: Regex

    def thompson(self) -> NFA:
        nfa = self.expr.thompson() 

        start = 0
        final = 1
        offset = 2 # nr de stari adaugate in plus

        nfa = nfa.remap_states(lambda x: x + offset)

        nfa.K.update({start, final})

        nfa.d[(start, EPSILON)] = {nfa.q0}
        nfa.d[(nfa.F.pop(), EPSILON)] = {nfa.q0, final}

        nfa.F = {final}
        nfa.q0 = start

        return nfa



@dataclass
class Question(Regex):
    expr: Regex

    def thompson(self) -> NFA:
        nfa = self.expr.thompson()

        start = 0
        final = 1
        offset = 2 # nr de stari adaugate in plus

        nfa = nfa.remap_states(lambda x: x + offset) # remapam starile

        # actualizare nfa
        nfa.K.update({start, final})

        nfa.d[(start, EPSILON)] = {nfa.q0, final}
        nfa.d[(nfa.F.pop(), EPSILON)] = {final}

        nfa.F = {final}
        nfa.q0 = start

        return nfa




@dataclass
class Union(Regex):
    left: Regex
    right: Regex

    def thompson(self) -> NFA:
        left_nfa = self.left.thompson() # nfa pentru stanga
        right_nfa = self.right.thompson() # nfa pentru dreapta

        start = 0 
        final = 1
        offset = 2  # nr de stari adaugate in plus in cazul asta sunt 2 stari

        left_nfa = left_nfa.remap_states(lambda x: x + offset) # remapam starile
        offset += len(left_nfa.K) # adaugam la offset nr de stari din stanga
        right_nfa = right_nfa.remap_states(lambda x: x + offset)


        nfa = NFA(
            S=left_nfa.S.union(right_nfa.S), # adaugam la alfabetul noului nfa alfabetul celor doua nfa-uri
            K=left_nfa.K.union(right_nfa.K).union({start, final}), # adaugam la starile noului nfa starile celor doua nfa-uri si cele noi
            q0=start,
            d={},
            F={final}
        )
        
        # actualizam tranzitiile
        nfa.d[(start, EPSILON)] = {left_nfa.q0, right_nfa.q0}
        nfa.d.update(left_nfa.d)
        nfa.d.update(right_nfa.d)
        nfa.d[(right_nfa.F.pop(), EPSILON)] = {final}
        nfa.d[(left_nfa.F.pop(), EPSILON)] = {final}
        
        return nfa



@dataclass
class Concat(Regex):
    left: Regex
    right: Regex

    def thompson(self) -> NFA:
        left_nfa = self.left.thompson()  # NFA pentru partea din stanga
        right_nfa = self.right.thompson()  # NFA pentru partea din dreapta
        
        offset = 0 # nr stari puse in plus

        left_nfa = left_nfa.remap_states(lambda x: x + offset) # remapam starile
        offset += len(left_nfa.K) # adaugam la offset nr de stari din stanga
        right_nfa = right_nfa.remap_states(lambda x: x + offset)

        start = left_nfa.q0 # starea de start
        final = right_nfa.F.pop() # starea finala


        nfa = NFA(
            S=left_nfa.S.union(right_nfa.S), # adaugam la alfabetul noului nfa alfabetul celor doua nfa-uri
            K=left_nfa.K.union(right_nfa.K), # adaugam la starile noului nfa starile celor doua nfa-uri
            q0=start,
            d={}, 
            F={final} 
        )
        
        #actualiza tranzitiile
        nfa.d.update(left_nfa.d)
        nfa.d.update(right_nfa.d)
        nfa.d[(left_nfa.F.pop(), EPSILON)] = {right_nfa.q0} 
        return nfa


def extinde_clasa_nr_litere(char_param: str) -> Set[str]:
    set_caractere = set()
    i = 0
    while i < len(char_param):
        if i + 2 < len(char_param) and char_param[i + 1] == '-':
            start = char_param[i] # primul termen
            end = char_param[i + 2] # al doilea termen
            for c in range(ord(start), ord(end) + 1):  # adaugam toate caracterele de la start-end
                set_caractere.add(chr(c))
            i += 3
        else:
            set_caractere.add(char_param[i]) # adaugam caracterul
            i += 1
    return set_caractere


def remove_space(regex: str) -> str:
    rezultat = []
    i = 0
    while i < len(regex):
        if regex[i] == '\\' and i + 1 < len(regex) and regex[i + 1] == ' ':
            rezultat.append(' ')
            i += 2
        elif regex[i] == ' ': # sarim peste spatiu
            i += 1
        else:
            rezultat.append(regex[i])
            i += 1
    return ''.join(rezultat)  # unim = returnam string-ul fara spatii


def parse_regex(regex: str) -> Regex:
    # create a Regex object by parsing the string

    # you can define additional classes and functions to help with the parsing process

    # the checker will call this function, then the thompson method of the generated object. the resulting NFA's
    # behaviour will be checked using your implementation form stage 1

    regex = remove_space(regex)  # eliminam spatiile
    tokens_list = []  # lista de token-uri
    #salvam mai intai toate token-urile in lista
    i = 0
    while i < len(regex):
        if regex[i] in '()*+?|':
            tokens_list.append(regex[i])
            i += 1
        elif regex[i] == '[':  # daca avem clasa de caractere
            j = i + 1
            while j < len(regex) and regex[j] != ']':
                j += 1
            if j == len(regex):  # daca nu gasim inchiderea
                raise ValueError("Nu am gasit inchiderea clasei de caractere ']'")
            # adaugam clasa de caractere
            rez_extindere = extinde_clasa_nr_litere(regex[i + 1:j])
            unim_rez = ''.join(rez_extindere) 
            tokens_list.append(f"[{unim_rez}]") # punem rezultatul in lista 
            i = j + 1
        elif regex[i] == '\\': # daca avem escape
            if i + 1 < len(regex):
                tokens_list.append('\\' + regex[i + 1])
                i += 2
            else:
                raise ValueError("Eroare Escape")
        else:
            tokens_list.append(regex[i]) # adaugam caractere
            i += 1
    return parse_tokens(tokens_list)



def parse_tokens(tokens: List[str]) -> Regex:

    def parse_expression(i: int) -> Tuple[Regex, int]:
        stiva = []  # stiva pentru a construi expresia

        # la parcurge o sa avem nevoie de i pentru a sti unde am ramas cand apelam recursiv
        while i < len(tokens):
            token = tokens[i]
            if token == '(':  # daca avem paranteza deschisa apelam recursiv pentru continutul parantezei
                sub_expr, i = parse_expression(i + 1)
                stiva.append(sub_expr) # adaugam rezultatul la final
            elif token == ')':
                return constructie_regex(stiva), i + 1 # construim expresia si returnam
            elif token in '*+?':  # operatori care au asemanator nfa ul 
                if not stiva:
                    raise ValueError(f"Operatorului {token} ii lipseste operandul")
                # il luam pe cel din stanga din stiva si il inlocuim cu rezultatul dupa aplicarea operatorului
                if token == '*':
                    stiva[-1] = Star(stiva[-1]) 
                elif token == '+':
                    stiva[-1] = Plus(stiva[-1])
                elif token == '?':
                    stiva[-1] = Question(stiva[-1])
                i += 1
            elif token == '|':    # UNIUNEA
                left = constructie_regex(stiva) # ce e in stanga putem sa il construim
                right, i = parse_expression(i + 1) # apelam recursiv pentru ce e in dreapta
                return Union(left, right), i # returnam unirea celor doua
            else:
                if token.startswith('\\'):  
                    stiva.append(Character(token[1]))  # daca avem escape adaugam caracterul
                elif token.startswith('[') and token.endswith(']'):
                    char_param = None
                    for char in token[1:-1]: # ignoram parantezele
                        if char_param is None:
                            char_param = Character(char)
                        else:
                            char_param = Union(char_param, Character(char)) # unim toate caracterele
                    stiva.append(char_param) 
                else:
                    for char in token:  # adaugam caracterele
                        stiva.append(Character(char)) 
                i += 1
        return constructie_regex(stiva), i


    def constructie_regex(stack: List[Regex]) -> Regex:
        if len(stack) == 1:
            return stack[0]
        rezultat = stack[0]
        for regex in stack[1:]:
            rezultat = Concat(rezultat, regex) # concatenam rezultatele
        return rezultat

    regex, _ = parse_expression(0) # apelam functia de parsare
    return regex
