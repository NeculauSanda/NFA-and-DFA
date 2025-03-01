from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs


@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def epsilon_closure(self, stare: STATE) -> set[STATE]:
        # compute the epsilon closure of a stare (you will need this for subset construction)
        # see the EPSILON definition at the top of this file

        starielipson = {stare} #punem in setul starielipson starea initiala pentru inceput
        # functie recursiva care verifica toate starile accesibile cu epsilon din starea curenta
        def apelare_recursiva_verificare(stare_curenta):
        # cautam toate starile accesibile din starea curenta prin tranzitiile epsilon
            for stare_urmatoare in self.d.get((stare_curenta, EPSILON), []):
                if stare_urmatoare not in starielipson:
                    # daca starea aflata nu se alfa in setul cu stari care pot fi accesate prin epsilon o ADAUGAM
                    starielipson.add(stare_urmatoare)
                    apelare_recursiva_verificare(stare_urmatoare) # verificam de la starea gasita in continuare

        apelare_recursiva_verificare(stare)  # apelam functia recursiva cu prima stare        
        return starielipson

    def subset_construction(self) -> DFA[frozenset[STATE]]:
        # convert this nfa to a dfa using the subset construction algorithm
        starileDFA = []
        tranzitiDFA = {}
        # starile moarte sunt starile care ajuta celelalte stari care nu au definite toate tranzitiile pe toate simbolurile
        # o tranzitie nevalida (care nu exista) va duce in starea moarta
        stareMoarta = frozenset() 

        # starea initiala va fi epsilon-closure (stare initiala = multimea starilor la care se poate ajunge prin epsilon) 
        # a starii initiale a NFA-ului
        stareInitiala = frozenset(self.epsilon_closure(self.q0))


        starileDFA.append(stareInitiala)

        # parcurgem starile din DFA incepand cu starea initiala care poate sa contina mai multe stari
        for stare in starileDFA:
            # pentru fiecare simbol din alfabet
            for simbol in self.S:

                #cautam toate straile din nfa la care se pot ajunge din starea curenta(sau starile curente pot fi mai multe) cu simbolul actual
                stareUrmatoare = set()
                for stareNFA in stare:
                    if (stareNFA, simbol) in self.d:
                        for st in self.d[(stareNFA, simbol)]:
                            stareUrmatoare.add(st) # adugam starea urmatoare pe care am gasit tranzitia
                stareUrmatoare = frozenset(stareUrmatoare)

                # cautam inchiderea elipson pentru starea urmatoare, cea de sus
                epsilonstari = set()
                for st in stareUrmatoare:
                    epsilonstari.update(self.epsilon_closure(st))
                starea_Urmatoare_inchideri = frozenset(epsilonstari)
                
                # daca exista stari accesibile prin simbolul actual si nu exista deja in DFA ul final o adaugam si adaugam si tranzitia
                # altfel daca setul e gol o adaugam tranzitiile pe simbol actual in starea moarta
                if starea_Urmatoare_inchideri:
                    if starea_Urmatoare_inchideri not in starileDFA:
                        starileDFA.append(starea_Urmatoare_inchideri)
                    tranzitiDFA[(stare, simbol)] = starea_Urmatoare_inchideri
                else:  # setul e gol 
                    tranzitiDFA[(stare, simbol)] = stareMoarta

        # adaugam toate tranzitiile din STAREA MOARTA tot in STAREA MOARTA pe toate simbolurile
        for simbol in self.S:
            tranzitiDFA[(stareMoarta, simbol)] = stareMoarta

        # starile finale
        # cautam prin starile DFA ului nostru, daca starea contine o stare finala din NFA atunci o adugam si dam break,
        # deoarce in multimea starii curente am gasit o stare finala => stare finala
        
        stariFinale = set()
        for stare in starileDFA:
            for st in stare:
                if st in self.F:
                    stariFinale.add(stare)
                    break
        
        return DFA(
            S = self.S,
            K = set(starileDFA) | {stareMoarta}, # facem uniunea dintre starile dfa ului si starea moarta
            q0 = stareInitiala,
            d = tranzitiDFA,
            F = stariFinale
        )

    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        # optional, but may be useful for the second stage of the project. Works similarly to 'remap_states'
        # from the DFA class. See the comments there for more details.
        new_K = set()
        for stare in self.K:
            new_K.add(f(stare))
        
        new_q0 = f(self.q0)

        new_d = {}
        for (stare, simbol), stari in self.d.items():
            starenoua = set()
            for s in stari:
                starenoua.add(f(s))
            new_d[(f(stare), simbol)] = starenoua
        
        new_F = set()
        for stare in self.F:
            new_F.add(f(stare))
        
        return NFA(S=self.S, K=new_K, q0=new_q0, d=new_d, F=new_F)
