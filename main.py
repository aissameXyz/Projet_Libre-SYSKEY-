import os
import getpass
from database_utils import *
from consts import *
from inquirer import (List, prompt)

options = [
    {'name': 'Ajouter un mot de passe', 'value': 'n'},
    {'name': 'Récupérer un mot de passe', 'value': 'r'},
    {'name': 'Supprimer un mot de passe', 'value': 'd'},
    {'name': 'Changer un mot de passe', 'value': 'c'},
    {'name': 'Lister tous les mot de passe', 'value': 'l'},
    {'name': 'Quiter', 'value': 'q'},
]

def get_name(opt):
    return f"({opt['value']}) {opt['name']}"

options = [get_name(opt) for opt in options]

questions = [
    List(
        'Choose an option',
        choices=options
    )
]




def register():
    """
    enregistre l'utilisateur et crée la base de données
    :return :
    """
    username = input("Entrez votre nom d'utilisateur : ")
    master_passwd = getpass.getpass("Entrez le mot de passe principal : ")
    master_passwdr = getpass.getpass("Entrez à nouveau le mot de passe principal : ")
    if master_passwd == master_passwdr:
        create_db()
        add_user(username, master_passwd)
        print(REGISTRATION_SUCCESS_TEXT)
    else:
        print(REGISTRATION_FAILED_TEXT)
        register()


def new_passwd(key):
    """
    ajoute la nouvelle entrée à la chambre forte
    :param key : clé pour crypter les données en clair
    :return :
    """
    app_name = input("Saisissez le nom de l'application : ")
    username = input("Entrez le nom d'utilisateur : ")
    password = input("Entrez le mot de passe : ")
    plain_data = [app_name, username, password]
    add_passwd(plain_data, key)


def retrieve_passwd(key):
    """
    récupère le mot de passe dans la chambre forte
    :param key : clé pour décrypter les données cryptées
    :return : correspondances trouvées dans la base de données
    """
    i_app_name = input("Entrez le nom de l'application: ")
    matches = get_passwd(i_app_name, key)
    if len(matches) > 1:
        print("Il semble qu'il y ait plusieurs identifiants associés à cette application.")
        match = get_spec_passwd(matches)
        match = [match]
    else:
        match = matches
    print_formatted(match)
    return match[0]


def delete_passwd(key):
    """
    supprime l'entrée du coffre-fort
    :param key :
    :return :
    """
    match = retrieve_passwd(key)
    choice = input("Voulez-vous supprimer l'entrée ci-dessus ? (y/n) : ")
    if choice == 'n':
        pass
    else:
        authorised, key = authorise()
        if authorised:
            del_passwd(match, key)
            print(DELETED_TEXT)


def list_apps():
    """
    liste toutes les applications sauvegardées dans le coffre-fort
    :retour :
    """
    results = list_all()
    print(f"Total {len(results)} entrées trouvées...")
    fetched = []
    for enc_data in results:
        plain_data = decrypt_all(enc_data, key)
        plain_data[2] = '*' * len(plain_data[2])
        fetched.append(plain_data)
    print_formatted(fetched)


def quit_passmgr():
    """
    quitte le coffre-fort
    :retour :
    """
    pass


def authorise():
    """
    autoriser l'utilisateur en lui demandant et en vérifiant ses informations d'identification.
    :retour : True et le mot de passe maître haché s'il existe
    """
    username = input("Entrez votre nom d'utilisateur : ")
    # master = input('Enter your master password: ')
    master = getpass.getpass('Entrez votre mot de passe principal : ')
    master = hashed(master)
    exists, key = verify_user(username, master)
    return exists, key


def change_passwd(key):
    """
    changer le mot de passe
    :param key :
    :return :
    """
    match = retrieve_passwd(key)
    choice = input("Voulez-vous changer le mot de passe ci-dessus ? (y/n) : ")
    if choice == 'n':
        pass
    else:
        new_pass = input("Entrez le nouveau mot de passe : ")
        authorised, key = authorise()
        if authorised:
            chng_passwd(match, new_pass, key)
            print(CHANGED_TEXT)


def print_formatted(results):
    """
    imprimer les entrées dans un format stylisé
    :param results : correspondances requises
    :return :
    """
    print("------------------------------------------------------------------------------------------------")
    print("|           APP NAME             |           USERNAME         |           PASSWORD             |")
    print("------------------------------------------------------------------------------------------------")
    if len(results) == 1:
        print(f"|   {results[0][0]:29s}| {results[0][1]:27s}| {results[0][2]:31s}|")
        print("------------------------------------------------------------------------------------------------")
    else:
        cnt = 1
        for result in results:
            print(f"| {cnt}. {result[0]:28s}| {result[1]:27s}| {result[2]:31s}|")
            print("------------------------------------------------------------------------------------------------")
            cnt += 1
    print("\n")

def get_spec_passwd(matches):
    """
    trouve une correspondance spécifique en demandant au nom d'utilisateur le nom d'application spécifique
    :param matches : correspondances trouvées par le nom de l'application
    :return : correspondance unique trouvée à partir du nom d'utilisateur
    """
    username = input("Entrez le nom d'utilisateur pour l'application : ")
    for match in matches:
        if username == match[1]:
            return match


if __name__ == '__main__':
    print(SUPER_START_TEXT)
    if not os.path.isfile('database.db'):
        register()
    failed_try = 0
    authorised, key = authorise()
    while not authorised:
        print(VERIFICATION_FAILED_TEXT)
        failed_try += 1
        if failed_try > 3:
            authorised = False
            print("Vous avez dépassé les limites maximales d'essai !")
            break
        else:
            authorised, key = authorise()
    if authorised:
        answer = prompt(questions)
        choice = answer['Choose an option'][1]
        while choice != 'q':
            if choice == 'n':
                new_passwd(key)
            elif choice == 'r':
                retrieve_passwd(key)
            elif choice == 'd':
                delete_passwd(key)
            elif choice == 'c':
                change_passwd(key)
            elif choice == 'l':
                list_apps()
            else:
                print(WRONG_INPUT_TEXT)
            answer = prompt(questions)
            choice = answer['Choose an option'][1]
        quit_passmgr()
    else:
        quit_passmgr()
