from .Regex import Regex, parse_regex
from .NFA import NFA
from .DFA import DFA
from functools import reduce

class Lexer:
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        self.spec = spec

        self.afd_map = []

        #map pentru a retine ordinea specificatiile -> (nume: index)
        self.spec_order = {token_name: idx for idx, (token_name, _) in enumerate(spec)} 

        # toate caracterele acceptate de nfa-uri
        self.nfaS = [] 

        for idx, (token_name, regex) in enumerate(spec):
            # Construim un NFA pentru regex-ul specificat
            nfa = parse_regex(regex).thompson()
            #salvam toate caracterele acceptate de nfa-uri
            self.nfaS.append(nfa.S) 
            # Convertim NFA-ul in DFA folosind subset construction
            dfa = nfa.subset_construction()
            # salvam perechea (nume token, DFA) pentru fiecare token
            self.afd_map.append((token_name, dfa))
    
    def lex(self, word: str) -> list[tuple[str, str]] | None:
        # this method splits the lexer into tokens based on the specification and the rules described in the lecture
        # the result is a list of tokens in the form (TOKEN_NAME:MATCHED_STRING)

        # if an error occurs and the lexing fails, you should return none
        tokens = []
        i = 0

        #linia la care ne aflam
        line = 0 
        #salvam indexurile la care am gasit separatorul '\n' de pe fiecare linie
        line_first_idx = []

        while i < len(word):
            #cautare patern
            max_match = ""
            name_token = None
            max_pos = i

            # lista de specificatiilor acceptate
            lista_spec_accept = []

            # alfam linia pe care suntem 
            if word[i] == '\n':
                line += 1
                line_first_idx.append(i + 1)

            # pentru fiecare SPECIFICATIE verificam daca se potriveste o secventa din cuvant(analizam caracter cu caracter) cu DFA-ul lui
            for token_name, dfa in self.afd_map:

                current_state = dfa.q0
                j = i # pozitia la care am ajuns ultima data cu verificatul(adica la ultimul SPECIFICATIE gasita buna)
                last_valid_pos = None # index pentru ultima pozitie valida gasita pentru un SPECIFICATIA actuala
                while j < len(word):
                    # facem tupluri din seturi pentru a le putea folosi ca chei in dictionar
                    if isinstance(current_state, set):
                        current_state = tuple(current_state)

                    # verificam daca avem tranzitie valida pe caracterul actual
                    current_state = dfa.d.get((current_state, word[j]))

                    # iesim si trecem l-a urmatorul patern daca nu avem tranzitie valida
                    if current_state is None:
                        break
                    
                    #daca am ajuns la o stare finala salvam pozitie valida unde am gasit PATERN-UL si continuam cu urmatoarea litera
                    if current_state in dfa.F:
                        last_valid_pos = j + 1

                    j += 1

                # daca am gasit o potrivire pentru acest DFA
                if last_valid_pos is not None:
                    # salvam PATERN-ul gasit pana la pozitia valida
                    match = word[i:last_valid_pos]
                    # salvam detaliile PATERN-ului gasit in lista de spec-uri acceptate (NUME, PATERN, POZITIE, STARE URMATOARE)
                    lista_spec_accept.append((token_name, match, last_valid_pos, current_state))
                    

                

            # alegem cea mai BUNA SPECIFICATIE
            if lista_spec_accept:
                # aranjam SPECIFICATIILE gasite in functie de lungimea sectiunii gasite, descrescator
                lista_spec_accept.sort(key=lambda x: (-len(x[1])))

                # pentru specificatiile care au ACELASI PATTERN GASIT, care NU au ca STARE URMATOARE frozenset() si care AU ACELASI IDEX LA CARE S-AU OPRIT
                # le ordonam in functie de ordinea in care ni s-au dat spec-urile
                patern_same = []
                spec_first = lista_spec_accept[0] # primul PATERN
                nr_same = 0 # numarul de PATERN-uri care au acelasi pattern gasit

                # adaugam in lista de patern-uri asemanatoare
                for c in lista_spec_accept:
                    if c[1] == spec_first[1] and c[2] == spec_first[2] and c[3] != frozenset() and spec_first[3] != frozenset():
                        nr_same += 1
                        patern_same.append(c)

                # daca am gasit patern-uri la fel le soratam
                if patern_same != []:
                    #ordonam in functie de ordinea in care ni s-au dat specificatiile
                    patern_same.sort(key=lambda x: self.spec_order[x[0]])
                    name_token, max_match, max_pos, _ = patern_same[0] # luam prima specificatie, deoarece este cel mai bun
                else: 
                    name_token, max_match, max_pos, _ = lista_spec_accept[0]

                tokens.append((name_token, max_match)) # adaugam in lista de token-uri SPECIFICATIA GASITA 

                i = max_pos  # avansam cursorul in cuvant la pozitia l-a care s-a terminat ultima SPECIFICATIE gasita
            else:
                # NU AM GASIT NICIO SPECIFICATIE
                # determinare numarul de caractere acceptate de masina
                nr_cararctere = 0
                for d in self.nfaS:
                    for litera in d:
                        nr_cararctere += 1

                #lungime cuvant
                lungime_cuvant = len(word)

                #daca a ajuns la sfarsitul cuvantului si nu a gasit un PATERN
                sfarsit_cuvant = False
                if(i + 1 == lungime_cuvant):
                    sfarsit_cuvant = True

                #determinare sa vedem daca litera la care s-a ajuns face parte sau nu din caracterele acceptate
                nr_carctere_accept = 0
                for d in self.nfaS:
                    for litera in d:
                        if litera != word[i]:
                            nr_carctere_accept += 1

                # caracterul nu este in carcterele acceptate de specificatii 
                if nr_carctere_accept == nr_cararctere:
                    error_message = f"No viable alternative at character {i}, line {line}"
                else:
                    # s-a terminat cuvantul si n-a gasit un PATERN valida (sau o stare finala) 
                    if sfarsit_cuvant == True:
                        error_message = f"No viable alternative at character EOF, line {line}"
                    else:
                        #afisare in functie de linie, daca nu e zero scadem din indexul la care am ajuns valoare la care am gasit ultimul separator '\n'
                        if line != 0:
                            error_message = f"No viable alternative at character {(i + 1) - line_first_idx[line - 1]}, line {line}"
                        else:
                            error_message = f"No viable alternative at character {(i + 1)}, line {line}"

                return [("", error_message)]

        return tokens
