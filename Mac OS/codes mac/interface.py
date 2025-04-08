# -*- coding: utf-8 -*-

import sys, os
if hasattr(sys, 'frozen'):
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open(os.devnull, "w")

# IMPORTS
import tkinter as tk                # IHM
from tkinter import messagebox      # IHM pour les messages d'erreur
from tkinter import filedialog      # IHM pour l'explorateur de fichiers
from PIL import Image, ImageTk      # Pour les transformations d'image (sur les boutons principalement)
import os                           # Pour la manipulation des chemins absolus et relatifs des fichiers
from code_arbre import *            # Pour les classes Node et Tree qui permettent de modeliser un arbre
from interaction_serveur import *   # Pour les fonctions download et upload
from tkinter import PhotoImage
import subprocess

# PARTIE ARBRE - Toutes ces variables sont globales et sont amenées a changer
arbre = None                        # Variable de type Tree, contenant l'arbre à afficher
l_NodeRectangle = []                # Liste contenant tous les noeuds graphiques (de type NodeRectangle)
l_link = []                         # Liste contenant tous les segments graphiques reliants les noeuds (de type Link)
r_px = 1                            #ratio pixels/unité graphique du dessin. Utile pour le zoom 
copied_node = None                  # Variable de type Node, contenant un noeud copié (pour le copier coller)

# CONSTANTES - Toutes ces variables sont globales et ne sont pas censees changer
e = 10                              # Espacement entre les widgets
bordure = 2                         # Epaisseur des bordures de frame
size_tool_button = (50, 50)         # Taille des boutons

# CREATION  DE LA FENETRE
window = tk.Tk()                                                                                            # Creation de la fenetre
window.title("IA-MVTE Modification arbre de décision")                                                      # Titre de la fenetre
icon = PhotoImage(file=os.path.join(base_path,"icones/IA_MVTE.png"))
window.wm_iconphoto(True, icon)                                                                    # Icone de la fenetre
window.geometry("{}x{}".format(int(window.winfo_screenwidth()*0.5),int(window.winfo_screenheight()*0.5)))   # Taille de la fenetre

# FRAME CONTENANT LES BOUTONS
tools_frame = tk.Frame(window, relief='groove', bd=bordure)
tools_frame.place(x=e, y=e)

# LISTE POUR STOCKER LES ACTIONS EFFECTUEES, CTRL-Z et CTRL-Y
# undo_stack = []
# redo_stack = []

# def add_action_undo_stack(undo_action, redo_action):
#     if callable(undo_action) and callable(redo_action): # On vérifie que undo_action et redo_action soient bien des fonctions
#         undo_stack.append((undo_action, redo_action))
#     else:
#         print("Erreur, il faut en paramètre des fonctions sans paramètres")

# def control_z(event):
#     if len(undo_stack)>0:
#         undo_action, redo_action = undo_stack.pop()
#         redo_stack.append((undo_action, redo_action))
#         undo_action()
# window.bind("<Control-z>", control_z)

# def control_y(event):
#     if len(redo_stack)>0:
#         undo_action, redo_action = redo_stack.pop()
#         undo_stack.append((undo_action, redo_action))
#         redo_action()
# window.bind("<Control-y>", control_y)

# BOUTON TELECHARGER
def push_download():
    global l_NodeRectangle, l_link, arbre
    push_MouseButton() #Pour se mettre dans le meme mode que le mode souris
    info_label.config(text="Telechargement en cours ...")
    window.update_idletasks()
    code_retour = download()
    info_label.config(text="")
    if code_retour==-1:
        messagebox.showerror("Erreur", "Erreur de telechargement")
    else :
        arbre = Tree()
        arbre.read_file_json("decision_tree.json")
        actualiser_dessin()
download_img = ImageTk.PhotoImage(Image.open(os.path.join(base_path,"icones/outil_telecharger.png")).resize(size_tool_button))
bouton_download = tk.Button(tools_frame, image=download_img, command=push_download)
bouton_download.place(x=e,y=e)
window.update_idletasks()#pour actualiser les tailles des boutons

# BOUTON UPLOADER
def push_upload():
    push_MouseButton() #Pour se mettre dans le meme mode que le mode souris
    arbre.save_json("decision_tree")
    upload()
upload_img = ImageTk.PhotoImage(Image.open(os.path.join(base_path,"icones/outil_enregistrer.png")).resize(size_tool_button))
download_button = tk.Button(tools_frame, image=upload_img, command=push_upload)
download_button.place(x=2*e+bouton_download.winfo_width(), y=e)

# BOUTON OUVRIR UN FICHIER
def push_open():
    global arbre
    push_MouseButton() #Pour se mettre dans le meme mode que le mode souris
    file_path = filedialog.askopenfilename(title="Ouvrir un fichier",filetypes=[("Fichiers JSON,", ".JSON"),("Fichiers TXT,", ".txt")])
    try :
        arbre = Tree()
        if file_path[-5:]==".json" or file_path[-5:]==".JSON":
            arbre.read_file_json(file_path)
        elif file_path[-4:]==".txt" or file_path[-4:]==".TXT":
            arbre.read_file_txt(file_path)
        elif file_path=="":
            return -1
        else :
            messagebox.showerror("Erreur", "Extension de fichier inconnue")
        actualiser_dessin()
    except Exception as e:
        #print(e)
        messagebox.showerror("Erreur", "Impossible de lire le fichier")

open_img = ImageTk.PhotoImage(Image.open(os.path.join(base_path,"icones/outil_ouvrir.png")).resize(size_tool_button))
open_button = tk.Button(tools_frame, image=open_img, command=push_open)
open_button.place(x=3*e+2*bouton_download.winfo_width(), y=e)

# BOUTON SAUVEGARDER UN FICHIER
def push_save():
    push_MouseButton() #Pour se mettre dans le meme mode que le mode souris
    if arbre == None:
        messagebox.showerror("Erreur","Aucun arbre à enregistrer")
    else :
        file_path = filedialog.asksaveasfilename(title="Enregistrer sous",filetypes=[("Fichiers JSON", ".json")])
        arbre.save_json(file_path)
save_img = ImageTk.PhotoImage(Image.open(os.path.join(base_path,"icones/outil_sauvegarder.png")).resize(size_tool_button))
save_button = tk.Button(tools_frame, image=save_img, command=push_save)
save_button.place(x=4*e+3*bouton_download.winfo_width(), y=e)

# BOUTON DEPLACER
def on_click_HandButton(event):
    global x0_HandButton, y0_HandButton
    x0_HandButton, y0_HandButton = event.x, event.y
def on_hold_HandButton(event):
    global x0_HandButton, y0_HandButton
    canva.move(tk.ALL,event.x-x0_HandButton, event.y-y0_HandButton)
    x0_HandButton, y0_HandButton = event.x, event.y
def push_HandButton():
    push_MouseButton() #Pour se mettre dans le meme mode que le mode souris
    canva.config(cursor="hand2")
    canva.bind("<Button-1>", on_click_HandButton)
    canva.bind("<B1-Motion>", on_hold_HandButton)
hand_img = ImageTk.PhotoImage(Image.open(os.path.join(base_path,"icones/outil_main.png")).resize(size_tool_button))
hand_button = tk.Button(tools_frame, image=hand_img, command=push_HandButton)
hand_button.place(x=5*e+4*bouton_download.winfo_width(), y=e)

# BOUTON SOURIS
def push_MouseButton():
    for r in l_NodeRectangle: #on passe tous les noeud en normal_mode dans le doute ou ils seraient en mode modif
        r.turn_normal_mode()
    canva.config(cursor="arrow")
    canva.unbind("<Button-1>")
    canva.unbind("<B1-Motion>")
mouse_img = ImageTk.PhotoImage(Image.open(os.path.join(base_path,"icones/outil_souris.png")).resize(size_tool_button))
Mouse_button = tk.Button(tools_frame, image=mouse_img, command=push_MouseButton)
Mouse_button.place(x=6*e+5*bouton_download.winfo_width(), y=e)

# BOUTON AJOUTER UN NOEUD
def push_add():
    push_MouseButton()
    canva.config(cursor="plus")
    for r in l_NodeRectangle:
        r.turn_modify_mode(r.add_child)
add_img = ImageTk.PhotoImage(Image.open(os.path.join(base_path,"icones/outil_ajouter.png")).resize(size_tool_button))
add_button = tk.Button(tools_frame, image=add_img, command=push_add)
add_button.place(x=7*e+6*bouton_download.winfo_width(), y=e)

# BOUTON SUPPRIMER UN NOEUD
def push_del():
    push_MouseButton()
    canva.config(cursor="X_cursor")
    for r in l_NodeRectangle:
        r.turn_modify_mode(r.del_node)
del_img = ImageTk.PhotoImage(Image.open(os.path.join(base_path,"icones/outil_supprimer.png")).resize(size_tool_button))
del_button = tk.Button(tools_frame, image=del_img, command=push_del)
del_button.place(x=8*e+7*bouton_download.winfo_width(), y=e)

# BOUTON RECHERCHER
# def push_find(event=None):
#     info_label.place_forget()
#     entry_find.place(x=e, y=e)
#     window.update_idletasks()
#     find_next_button.place(x=2*e+entry_find.winfo_width(), y=e)
#     window.update_idletasks()
#     find_close_button.place(x=3*e+entry_find.winfo_width()+find_next_button.winfo_width(), y=e)
# find_img = ImageTk.PhotoImage(Image.open("icones/outil_chercher.png").resize(size_tool_button))
# find_button = tk.Button(tools_frame, image=find_img, command=push_find)
# find_button.place(x=9*e+8*bouton_download.winfo_width(), y=e)
# window.bind("<Control-f>", push_find)

#BOUTON ZOOM PLUS
def push_zoom_plus(event=None):
    zoom(FakeEvent(1, x=canva.winfo_width()//2, y=canva.winfo_height()//2))
zoom_plus_img = ImageTk.PhotoImage(Image.open(os.path.join(base_path,"icones/zoom_plus.png")).resize(size_tool_button))
zoom_plus_button = tk.Button(tools_frame, image=zoom_plus_img, command=push_zoom_plus)
zoom_plus_button.place(x=9*e+8*bouton_download.winfo_width(), y=e)

#BOUTON ZOOM MOINS
def push_zoom_moins(event=None):
    zoom(FakeEvent(-1, x=canva.winfo_width()//2, y=canva.winfo_height()//2))
zoom_moins_img = ImageTk.PhotoImage(Image.open(os.path.join(base_path,"icones/zoom_moins.png")).resize(size_tool_button))
zoom_moins_button = tk.Button(tools_frame, image=zoom_moins_img, command=push_zoom_moins)
zoom_moins_button.place(x=10*e+9*bouton_download.winfo_width(), y=e)

# BOUTON INFORMATIONS
def push_info(event=None):
    subprocess.run(["open", os.path.join(base_path,"Notice_Utilisation.pdf")])
info_img = ImageTk.PhotoImage(Image.open(os.path.join(base_path,"icones/outil_info.png")).resize(size_tool_button))
info_button = tk.Button(tools_frame, image=info_img, command=push_info)
info_button.place(x=11*e+10*bouton_download.winfo_width(), y=e)

def actualiser_dessin():
    global l_NodeRectangle, l_link, arbre, r_px
    if len(l_NodeRectangle)>0: #si il y'avait deja un dessin, il faut connaitre l'offset du deplacement
        xy_offset = canva.coords(l_NodeRectangle[0].id_rectangle)[0:2] #deplacement du dessin
        first_diaplay = False
    else: #sinon c'est pas la peine
        first_diaplay = True
    canva.delete("all")
    dic_y = arbre.representation()
    l_NodeRectangle = [NodeRectangle(arbre.starting_node, [len(arbre.starting_node.coord)*300, dic_y[arbre.starting_node.coord]*100])]
    l_link = [] #arretes
    pile = [arbre.starting_node]
    i=0
    while len(pile)>0: #Remplissage de la liste des noeuds
        node = pile.pop(0)
        parent = l_NodeRectangle[i]
        i += 1
        for c in node.children:
            pile.append(c)
            l_NodeRectangle.append(NodeRectangle(c, [len(c.coord)*300, dic_y[c.coord]*100]))
            l_link.append(Link(parent, l_NodeRectangle[-1]))
    
    if not first_diaplay:
        r_px_init = r_px
        r_px = 1
        if r_px_init>1:
            event = FakeEvent(1)
            while r_px < r_px_init:
                zoom(event)
        elif r_px_init<1:
            event = FakeEvent(-1)
            while r_px>r_px_init:
                zoom(event)

        canva.move(tk.ALL, -canva.coords(l_NodeRectangle[0].id_rectangle)[0]+xy_offset[0], -canva.coords(l_NodeRectangle[0].id_rectangle)[1]+xy_offset[1])

class NodeRectangle():
    size = (200, 50)
    def __init__(self, node=None, pos=[50,50]):
        self.node = node
        self.pos = pos
        self.id_rectangle = canva.create_rectangle(self.pos[0], self.pos[1], (self.pos[0]+NodeRectangle.size[0]), (self.pos[1]+NodeRectangle.size[1]))
        canva.itemconfig(self.id_rectangle, width=3) #epaisseur du trait
        self.id_text = canva.create_text(self.pos[0]+NodeRectangle.size[0]/2, self.pos[1]+NodeRectangle.size[1]/2,text=node.name)
        canva.tag_bind(self.id_rectangle, "<Enter>", self.highlight)
        canva.tag_bind(self.id_rectangle, "<Leave>", self.unhighlight)
        canva.tag_bind(self.id_text, "<Enter>", self.highlight)
        canva.tag_bind(self.id_rectangle, "<Button-3>", self.right_click)
        canva.tag_bind(self.id_text, "<Button-3>", self.right_click)
        self.turn_normal_mode()
        self.char_size = len(node.name)/abs(canva.bbox(self.id_text)[0] - canva.bbox(self.id_text)[2]) #tailile mmoyenne d'un caractere
        self.zoom(r_px)  #on appelle cette fonction pour ajuster la taille des textes dans les cases
        
    def zoom(self, old_r_px):
        x1,y1,x2,y2 = canva.coords(self.id_rectangle)
        canva.coords(self.id_rectangle,x1*r_px/old_r_px,y1*r_px/old_r_px,x2*r_px/old_r_px,y2*r_px/old_r_px)
        x3, y3 = canva.coords(self.id_text)
        canva.coords(self.id_text, x3*r_px/old_r_px, y3*r_px/old_r_px) #reposiotionnement du texte
        x3, y3, x4, y4 = canva.bbox(self.id_text)
        canva.itemconfig(self.id_text, text=self.node.name[:int(self.char_size*abs(x1-x2)*0.8)*(abs(y3-y4)<abs(y1-y2))])#redimensionnement du texte, On garde une marge d'affichage de 80% (0.8) de la largeur du rectangle=)
    
    def highlight(self, event=None):
        canva.itemconfig(self.id_rectangle, fill='grey')
        info_label.config(text=self.node.name)
    
    def unhighlight(self, event=None):
        canva.itemconfig(self.id_rectangle, fill='')
        info_label.config(text="")
    
    def copy(self, event=None):
        global copied_node
        copied_node = self.node.copy()

    def paste(self, event=None):
        self.node.add_children(copied_node)
        arbre.actualiser_coord()
        actualiser_dessin()

    def right_click(self, event=None):
        right_click_menu = tk.Menu(window, tearoff=0)                                   # Création du menu contextuel
        right_click_menu.add_command(label="Modifier", command=self.DoubleClick)
        right_click_menu.add_separator()
        right_click_menu.add_command(label="Supprimer", command=self.del_node)
        right_click_menu.add_command(label="Ajouter un noeud enfant", command=self.add_child)
        right_click_menu.add_separator()
        right_click_menu.add_command(label="Copier", command=self.copy)
        right_click_menu.add_command(label="Coller", command=self.paste)
        right_click_menu.post(event.x_root, event.y_root)                               # Affichage du menu contextuel à la position du clic
    
    def DoubleClick(self, event=None): #pour modifier le nom d'un noeud
        temp_window = tk.Toplevel(window)
        temp_window.title("Modification du champ")
        
        entry = tk.Entry(temp_window, width=30)
        entry.pack(pady=20, padx=20) #marge autour du widget
        entry.insert(0, self.node.name)
        
        frame_button_temp_window = tk.Frame(temp_window, pady=20)
        frame_button_temp_window.pack()
        
        def PushValider():
            # old_name = self.node.name
            self.node.name = entry.get()
            canva.itemconfig(self.id_text, text=self.node.name)
            temp_window.destroy()
            # new_name = self.node.name #On est obligé de faire une copie, sinon ca ne fonctionne pas, je ne sais pas pourquoi
            # add_action_undo_stack(lambda:canva.itemconfig(self.id_text, text=old_name),lambda:canva.itemconfig(self.id_text, text=new_name))
            
        def PushAnnuler():
            temp_window.destroy()
        
        valider_button = tk.Button(frame_button_temp_window, text="Valider", command=PushValider)
        valider_button.grid(row=0, column=0, padx=10)
        
        annuler_button = tk.Button(frame_button_temp_window, text='Annuler', command=PushAnnuler)
        annuler_button.grid(row=0, column=1, padx=10)

        temp_window.geometry("")#Adapte la taille de la fenetre aux widgets
        temp_window.resizable(width=False, height=False)
    
    def turn_normal_mode(self):
        canva.tag_unbind(self.id_rectangle, "<Button-1>")
        canva.tag_unbind(self.id_text, "<Button-1>")
        canva.tag_bind(self.id_rectangle, "<Double-Button-1>", self.DoubleClick)
        canva.tag_bind(self.id_text, "<Double-Button-1>", self.DoubleClick)

    def turn_modify_mode(self, method):
        canva.tag_unbind(self.id_rectangle, "<Double-Button-1>")
        canva.tag_unbind(self.id_text, "<Double-Button-1>")
        canva.tag_bind(self.id_rectangle, "<Button-1>", method)
        canva.tag_bind(self.id_text, "<Button-1>", method)
    
    def add_child(self, event=None):
        temp_window = tk.Toplevel(window)
        temp_window.title("Ajout d'un noeud")
        
        consigne = tk.Label(temp_window, text="Nom du noeud :")
        consigne.pack(pady=10, padx=10)

        entry = tk.Entry(temp_window, width=30)
        entry.pack(padx=20) #marge autour du widget
        
        frame_button_temp_window = tk.Frame(temp_window, pady=20)
        frame_button_temp_window.pack()
        
        def PushValider():
            node_name = entry.get()
            arbre.add_node(node_name, self.node)
            actualiser_dessin()
            fin()

            # def undo(): #pour le ctrl-z
            #     arbre.supp_node(self.node.children[-1])
            #     actualiser_dessin()
            # def redo():#pour le ctrl-y
            #     arbre.add_node(node_name, self.node)
            #     actualiser_dessin()
            # add_action_undo_stack(lambda:undo(),lambda:redo())

        def fin():
            for r in l_NodeRectangle:
                r.turn_normal_mode()
            temp_window.destroy()
            push_MouseButton()
        
        valider_button = tk.Button(frame_button_temp_window, text="Valider", command=PushValider)
        valider_button.grid(row=0, column=0, padx=10, pady=10)
        
        annuler_button = tk.Button(frame_button_temp_window, text='Annuler', command=fin)
        annuler_button.grid(row=0, column=1, padx=10)

        temp_window.geometry("")#Adapte la taille de la fenetre aux widgets
        temp_window.resizable(width=False, height=False)
    
    def del_node(self, event=None):
        if self.node.coord == "0":
            messagebox.showerror("Erreur", "Suppression du noeud de départ interdite")
            return 0
        else :
            parent_node = arbre.supp_node(self.node) #Noeud parent auquel on supprime un enfant
            actualiser_dessin()
            for r in l_NodeRectangle:
                r.turn_normal_mode()
            push_MouseButton()

            # def undo():
            #     parent_node.add_children(self.node)
            #     actualiser_dessin()
            # def redo():
            #     arbre.supp_node(self.node)
            #     actualiser_dessin()
            # add_action_undo_stack(lambda:undo(),lambda:redo())

class Link():
    def __init__(self, node_rectangle1, node_rectangle2):
        self.node_rectangle1 = node_rectangle1
        self.node_rectangle2 = node_rectangle2
        self.id_link = canva.create_line(node_rectangle1.pos[0]+NodeRectangle.size[0], node_rectangle1.pos[1]+NodeRectangle.size[1]//2, node_rectangle2.pos[0], node_rectangle2.pos[1]+NodeRectangle.size[1]//2)
        canva.itemconfig(self.id_link, width=3) #epaisseur du trait
        
    def zoom(self, old_r_px):
        x1,y1,x2,y2 = canva.coords(self.id_link)
        canva.coords(self.id_link,x1*r_px/old_r_px,y1*r_px/old_r_px,x2*r_px/old_r_px,y2*r_px/old_r_px)

#Frame du canva
draw_frame = tk.Frame(window, relief='groove', bd=bordure)
tools_frame.config(width=window.winfo_width()-2*e, height=bouton_download.winfo_height()+2*e)
window.update_idletasks()
draw_frame.place(x=e, y=tools_frame.winfo_height()+2*e)

#Canva dans lequel on dessine l'arbre
canva = tk.Canvas(draw_frame,background="white", highlightthickness=0, relief='flat')
canva.place(x=0,y=0)

#frame bas de fenetre dans laquelle on affiche le texte des cases de l'arbre
info_frame = tk.Frame(window, relief='groove', bd=bordure)
#on la place dans la fonction resize_window

#Label dans la info_frame
info_label = tk.Label(info_frame, text="")
info_label.place(x=e,y=e)

# Widgets de la fonction pour chercher un noeud
entry_find = tk.Entry(info_frame, width=30)
def push_find_next():
    look_for_field = entry_find.get()
    #print(look_for_field)
find_next_button = tk.Button(info_frame, text='Suivant', command=push_find_next)
def push_find_close():
    entry_find.place_forget()
    find_next_button.place_forget()
    find_close_button.place_forget()
    info_label.place(x=e, y=e)
find_close_button = tk.Button(info_frame, text='Fermer', command=push_find_close)

class FakeEvent(): #Simuler un event tkinter
    def __init__(self, delta, x=0, y=0):
        self.delta = delta
        self.x = x
        self.y = y

def zoom(event):
    global r_px
    old_r_px = r_px
    r_px *= 1.1*(event.delta>0)+0.9*(event.delta<=0)
    canva.move(tk.ALL, -event.x, -event.y)
    for w in l_NodeRectangle:
        w.zoom(old_r_px)
    for l in l_link:
        l.zoom(old_r_px)
    canva.move(tk.ALL, event.x, event.y)
canva.bind("<MouseWheel>", zoom)

def resize_window(event): #Fonction appelée à chaque fois que la fenêtre est redimensionnée
    tools_frame.config(width=window.winfo_width()-2*e, height=bouton_download.winfo_height()+2*e)
    draw_frame.config(height=window.winfo_height()-4*e-tools_frame.winfo_height()-info_frame.winfo_height(), width=window.winfo_width()-2*e)
    canva.config(height=window.winfo_height()-4*e-tools_frame.winfo_height()-2*bordure-info_frame.winfo_height(), width=window.winfo_width()-2*e-2*bordure)
    info_frame.config(height=2*e+max(info_label.winfo_height(), find_close_button.winfo_height()), width=window.winfo_width()-2*e)
    info_frame.place(x=e, y=window.winfo_height()-info_frame.winfo_height()-e)
window.bind("<Configure>", resize_window)

window.mainloop()
