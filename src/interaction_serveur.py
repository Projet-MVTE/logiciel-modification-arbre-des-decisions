import requests
import os
import sys

base_path = ""
if getattr(sys, 'frozen', False):  # Si c'est un exécutable compilé
    base_path = os.path.dirname(sys.executable)
else:  # Si c'est un script Python
    base_path = os.path.dirname(os.path.abspath(__file__))

#Importe depuis le fichier data les url necessaires
f = open(os.path.join(base_path, "data.txt"), "r")
data = [c.strip() for c in f.readlines()]
f.close()
url_download, url_upload = data[0], data[1]

def download():
    """
    Telecharge dans le repertoire courant l'abre stocké sur le serveur
    """
    try:
        response = requests.get(url_download)
        response.raise_for_status()  # Vérifier si la requête a réussi
        
        f = open("decision_tree.json", "wb") #write bytes
        f.write(response.content)
        f.close()
        return 1
    
    except requests.exceptions.RequestException as e:
        print("Erreur lors de la recuperation du fichier")
        return -1

def upload():
    """
    Envoi sur le serveur le fichier json contenant l'abre
    """
    with open("decision_tree.json", 'rb') as f:
        files = {'file': f}
        response = requests.post(url_upload, files=files)
    print(response.json())
























# import requests

# # Importe depuis le fichier data les url necessaires
# f = open("data.txt", "r")
# data = [c.strip() for c in f.readlines()]
# f.close()
# url_download, url_upload = data[0], data[1]

# def download():
#     """
#     Telecharge dans le repertoire courant l'abre stocké sur le serveur
#     """
#     try:
#         response = requests.get(url_download)
#         response.raise_for_status()  # Vérifier si la requête a réussi
        
#         f = open("decision_tree.json", "wb") #write bytes
#         f.write(response.content)
#         f.close()
#         return 1
    
#     except requests.exceptions.RequestException as e:
#         print("Erreur lors de la recuperation du fichier")
#         return -1

# def upload():
#     """
#     Envoi sur le serveur le fichier json contenant l'abre
#     """
#     with open("decision_tree.json", 'rb') as f:
#         files = {'file': f}
#         response = requests.post(url_upload, files=files)
#     print(response.json())