import json

class Node():
    """
    Objet Noeud d'un arbre de décisions
    """
    def __init__(self, name, coord=""):
        """
        Variables d'instance :
        ------------------------------------------------------------------------------------------------------------------
        name     : str           : Nom du noeud
        children : liste de Node : Liste des noeuds enfants
        coord    : str           : Coordonnées du noeud dans l'arbre. Sous la forme '021' -> Noeud 1 du noeud 2 du noeud 0 
        """
        self.name = name
        self.children = []
        self.coord = coord

    def add_children(self, child):
        """
        Ajoute un noeud enfant

        Parametres :
        -------------------------------------
        child : Node : Noeud enfant à ajouter
        """
        if isinstance(child, Node):
            self.children.append(child)
        #else:
            #print("Erreur : Il faut un Node en parametre")

    def supp_child(self, child):
        """
        Supprime un noeud enfant

        Parametres :
        ---------------------------------------
        child : Node : Noeud enfant à supprimer
        """
        if isinstance(child, Node):
            if child in self.children:
                self.children.pop(self.children.index(child))
            #else:
                #print("Noeud inexistant")
        #else:
            #print("Erreur : Il faut un Node en parametre")

    def copy(self):
        """
        Retourne un nouveau objet Node avec le même nom que self, des coordonnées et enfants différents
        """
        copied_node = Node(self.name)
        copied_node.children = [c.copy() for c in self.children]
        return copied_node

    def __str__(self):
        return "Noeud {"+self.name+"}"

class Tree():
    def __init__(self):
        """
        starting_node : Node : Noeud de départ
        """
        self.starting_node = None

    def add_node(self, name, parent):
        """
        Ajoute un noeud fils au noeud parent passé en parametre

        Parametres :
        ---------------------------------------
        name   : str  : Nom du noeud à rajouter
        parent : Node : Noeud parrent
        """
        n = Node(name, parent.coord + str(len(parent.children)))
        parent.add_children(n)

    def supp_node(self, node_to_supp):
        """
        Supprime le noeud en parametre et retourne le noeud parent auquel on a supprime un enfant

        Parametres :
        ----------------------------------------
        node_to_supp : Node :  Noeud à supprimer
        """
        if isinstance(node_to_supp, Node):
            pile = [self.starting_node]
            while len(pile)>0:
                node = pile.pop(0)

                if node_to_supp in node.children:
                    node.supp_child(node_to_supp)
                    self.actualiser_coord()
                    return node
                else:
                    for c in node.children:
                        pile.append(c)
        #else:
            #print("Erreur : Il faut un Node en parametre")
        #self.actualiser_coord()

    def actualiser_coord(self):
        """
        Actualise l'attribut coord de tous les noeuds de l'arbre
        """
        pile = [self.starting_node]
        while len(pile)>0:
            node = pile.pop(0)
            for k in range(len(node.children)):
                pile.append(node.children[k])
                node.children[k].coord = node.coord + str(k)
    
    def read_file_json(self, file_name):
        """
        Ouvre l'abre contenu dans un fichier json

        Parametres :
        -----------------------------------
        file_name : str : Chemin du fichier
        """
        f = open(file_name, "r",  encoding='utf-8')
        data = json.load(f)
        f.close()
        
        self.starting_node = Node(data["data"]['0']['title'],"0")
        dic = {"0":self.starting_node}
        for coord in data["data"]:
            if coord != "0":
                dic[coord] = Node(data["data"][coord]["title"], coord)
                dic[coord[:-1]].add_children(dic[coord])
    
    def read_file_txt(self, file_name):
        """
        Ouvre l'abre contenu dans un fichier txt genere par framindmap

        Parametres :
        -----------------------------------
        file_name : str : Chemin du fichier
        """
        f = open(file_name,"r", encoding='utf-8')
        data = [c.strip().split() for c in f.readlines() if c.strip()[0] in ["0","1","2","3","4","5","6","3","8","9"]]
        f.close()
        for k in range(len(data)):
            data[k] = ["".join([str(int(i)-1) for i in data[k][0].split(".")]), " ".join(data[k][1:])]

        self.starting_node = Node(data[0][1], "0")
        dic = {"0":self.starting_node}
        for elem in data[1:]:
            dic[elem[0]] = Node(elem[1],elem[0])
            dic[elem[0][:-1]].add_children(dic[elem[0]])
      
    def save_json(self, file_name):
        """
        Enregistre l'arbre dans un fichier json

        Parametres :
        -----------------------------------
        file_name : str : Chemin du fichier
        """
        pile = [self.starting_node]
        dic = {"message":"Built by Dina, Julien, Johan, Jawad and Naim at ENSTA Bretagne",
               "source":"serveur",
               "lastUpdated":None,
               "data":{}}

        while len(pile)>0:
            node = pile.pop(0)
            dic["data"][node.coord] = {"id":node.coord,
                                       "title":node.name,
                                       "type":1*(len(node.children)==0),
                                       "next":[c.coord for c in node.children]}
            for c in node.children:
                pile.append(c)

        f = open(file_name+".json", "w")
        f.write(json.dumps(dic, indent=4))
        f.close()
    
    def representation(self):
        """
        Retourne un dictionnaire du type {coordonée du node dans l'arbre : altitude du noeud dans la colonne}
        Ce dictionnaire sert uniquement pour de la représentation graphique
        """
        pile = [self.starting_node]
        dic_taille =  {self.starting_node.coord:0}
        dic_colonne = {self.starting_node.coord:0}
        nb_colonnes = 0
        while len(pile)>0:
            node = pile.pop(0)
            dic_colonne[node.coord] = 0
            nb_colonnes = max(nb_colonnes, len(node.coord))
            dic_taille[node.coord] = 0
            if len(node.children)== 0: #si l'enfant est en bout d'arbre
                dic_taille[node.coord] = 1
                for i in range(1,len(node.coord)):
                    dic_taille[node.coord[:-i]] += 1
                    
            for c in node.children:
                pile.append(c)

        dic_y = dic_taille.copy()
        dic_y["0"] = dic_taille["0"]/2
        for key in dic_taille:
            if key != '0':
                dic_y[key], dic_colonne[key[:-1]] = dic_taille[key]/2 + dic_colonne[key[:-1]] + dic_y[key[:-1]] - dic_taille[key[:-1]]/2, dic_colonne[key[:-1]] + dic_taille[key]
        
        return dic_y
