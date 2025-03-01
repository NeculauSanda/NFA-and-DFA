from collections.abc import Callable
from dataclasses import dataclass
from itertools import product
import pandas as pd
from typing import TypeVar
from functools import reduce

STATE = TypeVar('STATE')

@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]

    def accept(self, word: str) -> bool:
        # simulate the dfa on the given word. return true if the dfa accepts the word, false otherwise
        stare_actuala = self.q0 # setam starea curenta ca fiind starea initiala
        for simbol in word:
            stare_actuala = self.d.get((stare_actuala, simbol))
            if stare_actuala is None:
                return False
        # returneaza adevarat daca cuvantul este in starea finala 
        return stare_actuala in self.F

    def remap_states[OTHER_STATE](self, f: Callable[[STATE], 'OTHER_STATE']) -> 'DFA[OTHER_STATE]':
        # optional, but might be useful for subset construction and the lexer to avoid state name conflicts.
        # this method generates a new dfa, with renamed state labels, while keeping the overall structure of the
        # automaton.

        # for example, given this dfa:

        # > (0) -a,b-> (1) ----a----> ((2))
        #               \-b-> (3) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        # applying the x -> x+2 function would create the following dfa:

        # > (2) -a,b-> (3) ----a----> ((4))
        #               \-b-> (5) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

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
        
        return DFA(S=self.S, K=new_K, q0=new_q0, d=new_d, F=new_F)
    
    def minimize(self) -> 'DFA[STATE]':

        # I. eliminam starile inaccesibile, starile in care nu se ajunge niciodata pornind de la starea initiala
        Stari_Accesibile = set()
        stari_in_procesare = {self.q0}
        while stari_in_procesare:
            stare = stari_in_procesare.pop()
            if stare not in Stari_Accesibile:
                Stari_Accesibile.add(stare) # adaugam starea in setul de stari Stari_Accesibile
                for simbol in self.S:
                    #pentru fiecare simbol verificam daca exista stari urmatoare si le adaugam in setul de stari de procesare 
                    stareUrmaoare = self.d.get((stare, simbol))
                    if stareUrmaoare is not None:
                        stari_in_procesare.add(stareUrmaoare)

        Kaccesibile = self.K.intersection(Stari_Accesibile) # pastram doar starile accesibile
        Faccesibil = self.F.intersection(Stari_Accesibile) # pastram doar starile finale accesibile
        # pastram doar tranzitiile care au stari accesibile
        Daccesibile = {}
        for (stare, simbol), stareUrmatoare in self.d.items():
            # daca starea din tranzitie e accesibila si starea urmatoare e accesibila atunci adaugam tranzitia
            if stare in Stari_Accesibile and stareUrmatoare in Stari_Accesibile:
                Daccesibile[(stare, simbol)] = stareUrmatoare

        # II. Facem matricea pentru a determina perechile de stari care nu se disting
        Stari = list(Kaccesibile)  # Convertim starile accesibile in lista pentru indexare
        nr_stari = len(Stari)
        index_mat = {}
        for i, stare in enumerate(Stari):
            index_mat[stare] = i

        # initializam matricea cu valoare False <=> starile sunt ecivalente/nu se disting
        # pe fiecare linie vor fi nr_stari elemente = false
        Matrice_Distingere = []
        for _ in range(nr_stari):
            Matrice_Distingere.append([False] * nr_stari)
        
        # REZOLVARE MATRICE DISTINGERE
        # A. Marcam toate perechile (stare finala, stare non-final)
        for i in range(nr_stari):
            for j in range(i):
                if (Stari[i] in Faccesibil) != (Stari[j] in Faccesibil):
                    Matrice_Distingere[i][j] = True  # stari diferite

        # B. verificam fiecare pereche din matrice sa vedem daca putem forma perechi din predecesori pe fiecare simbol
        Matrice_Verificata = True
        while Matrice_Verificata:
            Matrice_Verificata = False
            # vom verifica doar sub diagonala principala
            for i in range(nr_stari):
                for j in range(i):
                    if Matrice_Distingere[i][j] == False:
                        # daca perechea nu e marcata inca, cautam starile in care se pot ajunge pe simbolul ales pentru fiecare stare
                        for simbol in self.S:
                            next_stare_i = Daccesibile.get((Stari[i], simbol))
                            next_stare_j = Daccesibile.get((Stari[j], simbol))
                            # daca exista tranziti pe ambele stari cu simbolul curent verificam sa vedem daca putem marca pereche(i,j) in matrice
                            if next_stare_i is not None and next_stare_j is not None:
                                next_i_index = index_mat[next_stare_i]
                                next_j_index = index_mat[next_stare_j]
                                
                                val_i = max(next_i_index, next_j_index)
                                val_j = min(next_i_index, next_j_index)
                                # daca exista perechea de succesori deja in matrice marcata cu True, atunci si predesori ii marcam in matrice
                                if Matrice_Distingere[val_i][val_j] == True:
                                    Matrice_Distingere[i][j] = True
                                    Matrice_Verificata = True
                                    break

        # C. grupam starile echivalente
        stari_echivalente = [] # lista cu subliste
        stare_multime = {} # ma ajuta sa mapez fiecare stare la un reprezentant(cheia) = prima stare gasita 

        # cautam pentru fiecare stare un grup in care sa fie plasat
        for i in range(nr_stari):
            gasit = False
            for eq in stari_echivalente:
                # daca perechea formata din starea curenta si cheia grupului este marcata cu False
                # in matrice atunci inseamna ca sunt echivalente si o adaugam in grupul respectiv
                if not Matrice_Distingere[i][index_mat[eq[0]]]:
                    eq.append(Stari[i])
                    stare_multime[Stari[i]] = eq[0] # marcam starea ca fiind in grupul respectiv => va avea valoarea reprezentantului
                    gasit = True
                    break
            # daca nu am gasit atunci se formeaza un nou grup de sine statator
            if not gasit:
                stari_echivalente.append([Stari[i]])
                stare_multime[Stari[i]] = Stari[i]

        # III. Construim noul DFA
        new_stari = set()
        for eq in stari_echivalente:
            new_stari.add(frozenset(eq))
        
        new_q0 = stare_multime[self.q0]
        new_F = set()
        for state in Faccesibil:
            new_F.add(stare_multime[state])

        new_d = {}
        for (state, simbol), next_state in Daccesibile.items():
            new_d[(stare_multime[state], simbol)] = stare_multime[next_state]

        return DFA(self.S, new_stari, new_q0, new_d, new_F)