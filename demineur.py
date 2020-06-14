import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sys import setrecursionlimit
from functools import partial
from random import randint, randrange


setrecursionlimit(100_000)
NB_ITER = 0


class Demineur:
    def __init__(self, hauteur=50, largeur=50, nb_bombes=None, bombes_min=10, bombes_max=5):
        self.gagne = False
        self.perdu = False
        self.hauteur = hauteur
        self.largeur = largeur
        self.nb_cases_inconnues = largeur * hauteur
        self.grille = np.zeros((hauteur, largeur), dtype=np.int8)
        self.connu = np.zeros((hauteur, largeur), dtype=np.int8) - 1
        self.bombes = []

        if nb_bombes is None:
            nb_bombes = randint(hauteur * largeur // bombes_min, hauteur * largeur // bombes_max)
        self.nb_bombes = nb_bombes

        self.nb_bombes_restantes = nb_bombes

        for _ in range(nb_bombes):
            i, j = randrange(0, hauteur), randrange(0, largeur)
            while self.grille[i][j]:
                i, j = randrange(0, hauteur), randrange(0, largeur)
            self.grille[i][j] = -2
            self.bombes.append((i, j))

        for i, j in self.bombes:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if (dx != 0 or dy != 0) and 0 <= i + dy < hauteur and 0 <= j + dx < largeur and self.grille[i + dy][j + dx] != -2:
                        self.grille[i + dy][j + dx] += 1

    def __str__(self):
        return f'Démineur : {self.nb_bombes} bombes, {self.grille.shape}\n{self.grille}'

    def __repr__(self):
        print(str(self))

    def __iter__(self):
        yield from self.grille

    def __getitem__(self, i):
        return self.grille[i]

    def __setitem__(self, i, data):
        self.grille[i] = data

    def show(self, connu=True, victoire=False, defaite=False):
        global NB_ITER
        plt.clf()
        cmap = ListedColormap(['black', 'lightgray','white', 'blue', 'green', 'red', 'darkblue', 'darkred', 'cyan', 'orange', 'purple', 'yellow'])
        if connu:
            im = plt.imshow(self.connu, cmap=cmap, vmin=-2.5, vmax=9.5)
        else:
            im = plt.imshow(self.grille, cmap=cmap, vmin=-2.5, vmax=9.5)
        plt.colorbar(im, ticks=np.arange(-2, 10))
        plt.axis('off')
        if victoire:
            plt.title('Victoire !')
        elif defaite:
            plt.title('Defaite.')
        else:
            plt.title(str(self).split('\n')[0] + f', {self.nb_bombes_restantes} bombes restantes')
        plt.savefig(f'{NB_ITER}.jpg', dpi=300, bbox_inches='tight')
        NB_ITER += 1
        plt.pause(0.001)

    def decouvre(self, i, j):
        '''
        DFS
        '''
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if (dx != 0 or dy != 0) and 0 <= i + dy < self.hauteur and 0 <= j + dx < self.largeur and self.connu[i + dy][j + dx] == -1:
                    self.connu[i + dy][j + dx] = self.grille[i + dy][j + dx]
                    self.nb_cases_inconnues -= 1
                    if self.grille[i + dy][j + dx] == 0:
                        self.decouvre(i + dy, j + dx)

    def joue(self, IA, show=False):
        while True:
            i, j, bombe = IA(self.connu, self.nb_bombes, partial(self.show, connu=True, victoire=False, defaite=False), show)
            if bombe:
                if self.connu[i][j] != 9:
                    self.nb_bombes_restantes -= 1
                self.connu[i][j] = 9
            else:
                if self.connu[i][j] == 9:
                    self.nb_bombes_restantes += 1
                elif self.connu[i][j] != -2 and self.connu[i][j] == -1:
                    self.nb_cases_inconnues -= 1
                self.connu[i][j] = self.grille[i][j]
                if self.grille[i][j] == -2:
                    self.perdu = True
                    if show:
                        self.show(defaite=True)
                    return False
                if self.grille[i][j] == 0:
                    self.decouvre(i, j)
                if self.nb_cases_inconnues == self.nb_bombes:
                    self.gagne = True
                    if show:
                        self.show(victoire=True)
                    return True


def humain(connu, nb_bombes, show, show_bool):
    if show_bool:
        show()
    return eval(input('Entrer i, j, bombe : '))


def bonobo(connu, nb_bombes, show, show_bool):
    # Choisit au hasard.
    if show_bool:
        show()
    i, j = randrange(0, connu.shape[0]), randrange(0, connu.shape[1])
    while connu[i][j] !=  -1:
        i, j = randrange(0, connu.shape[0]), randrange(0, connu.shape[1])
    return i, j, False


def trivial(connu, nb_bombes, show, show_bool):
    '''
    Remplit les cases évidentes.
    '''
    if show_bool:
        show()
    global PILE
    if len(PILE) != 0:
        f = PILE.pop()
        return f[0], f[1], f[2]
    global NB_BONOBO
    for i in range(connu.shape[1]):
        for j in range(connu.shape[0]):
            if connu[i][j] != 9 and connu[i][j] != -1:
                nb_bombes_voisines = connu[i][j]
                nb_cases_voisines_inconnues = 0
                cases_voisines_inconnues = []
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if (dx != 0 or dy != 0) and 0 <= i + dy < connu.shape[1] and 0 <= j + dx < connu.shape[0]:
                            if connu[i + dy][j + dx] == -1:
                                nb_cases_voisines_inconnues += 1
                                cases_voisines_inconnues.append((i + dy, j + dx))
                            elif connu[i + dy][j + dx] == 9:
                                nb_bombes_voisines -= 1
                if nb_bombes_voisines == 0 and nb_cases_voisines_inconnues != 0:
                    for idx in range(len(cases_voisines_inconnues)):
                        PILE.append((cases_voisines_inconnues[idx][0], cases_voisines_inconnues[idx][1], False))
                if nb_cases_voisines_inconnues == nb_bombes_voisines != 0:
                    for idx in range(len(cases_voisines_inconnues)):
                        PILE.append((cases_voisines_inconnues[idx][0], cases_voisines_inconnues[idx][1], True))
    if len(PILE) == 0:
        NB_BONOBO += 1
        return bonobo(connu, nb_bombes, show, show_bool)
    else:
        f = PILE.pop()
        return f[0], f[1], f[2]


NB_BONOBO = 0
PILE = []

if __name__ == '__main__':
    d = Demineur(nb_bombes=400)
    res = d.joue(trivial, show=True)
    print(res)
    print(NB_BONOBO)

    plt.show()

