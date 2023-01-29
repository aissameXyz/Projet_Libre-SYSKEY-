import sqlite3
from encryption_utils import AESCipher, hashed


def connect():
    """
    Se connecter à la base de données
    :return: connection and cursor objects pour interagir avec la base de données
    """
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    return conn, cursor


def disconnect(conn):
    """
    déconnexion de la connexion active
     -conn: connection object to the database
    """
    conn.commit()
    conn.close()


def create_db():
    """
    Creation de la base de données, et les deux tables:
    -users: pour stocker les utilisateur
    -passwords: pour stocker les mot de passe
    """
    with open("database.db", 'w'):
        pass
    conn, cursor = connect()

    cursor.execute('''CREATE TABLE users(
                    username TEXT NOT NULL,
                    master_pwd BLOB NOT NULL
                    );
                    ''')

    cursor.execute('''
                    CREATE TABLE passwords(
                    app_name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password BLOB NOT NULL
                    );
                    ''')
    disconnect(conn)


def add_passwd(plain_data, key):
    """
    crypte l'entrée reçue et l'insère dans la base de données

    :param plain_data : liste composée de app_name, username, password
    :param key : valeur hachée du mot de passe principal
    :return :
    """
    conn, cursor = connect()
    enc_data = encrypt_all(plain_data, key)
    cursor.execute('''INSERT INTO passwords (app_name, username, password)
                    VALUES ("{}", "{}", "{}")
                    '''.format(*enc_data))
    disconnect(conn)


def del_passwd(match, key):
    """

    :param match : liste composée du nom de l'application, du nom d'utilisateur et du mot de passe ; l'utilisateur à supprimer.
    :param key : valeur hachée du mot de passe principal
    :return :
    """
    conn, cursor = connect()
    hashed_match = get_hashed_match(match, key)
    appn, usern, _ = [i for i in hashed_match]
    cursor.execute(f"DELETE FROM passwords WHERE (app_name='{appn}' AND username='{usern}')")
    disconnect(conn)


def list_all():
    """
    Récupère toutes les entrées de la base de données
    :return : liste des entrées cryptées de la base de données
    """
    conn, cursor = connect()
    cursor.execute("SELECT * FROM passwords")
    result = cursor.fetchall()
    disconnect(conn)
    return result


def get_hashed_match(match, key):
    """
    trouve l'entrée chiffrée correspondante dans la base de données
    :param match : liste composée de app_name, username, password
    :param key : valeur hachée du mot de passe principal
    :return : entrée chiffrée correspondante stockée dans la base de données
    """
    results = list_all()
    for enc_data in results:
        plain_data = decrypt_all(enc_data, key)
        if match == plain_data:
            return list(enc_data)


def get_passwd(i_app_name, key):
    """
    trouve toutes les correspondances avec le nom d'application donné.
    :param i_app_name : nom de l'application de l'utilisateur
    :param key : valeur hachée du mot de passe principal
    :return : retourne toutes les correspondances avec le nom de l'application.
    """
    results = list_all()
    matches = []
    for enc_data in results:
        plain_data = decrypt_all(enc_data, key)
        if i_app_name.lower() == plain_data[0].lower():
            matches.append(plain_data)
    return matches


def add_user(username, master_pass):
    """
    insérer le profil de l'utilisateur et le mot de passe maître haché dans la base de données
    :param username : nom d'utilisateur pour la chambre forte
    :param master_pass : mot de passe principal pour le coffre-fort
    :return :
    """
    conn, cursor = connect()
    master_pass = hashed(master_pass)
    cursor.execute(f'''INSERT INTO users (username, master_pwd)
                    VALUES ("{username}", "{master_pass}")
                    ''')
    disconnect(conn)


def get_stored_master(username):
    """
    trouve la valeur hachée correspondante stockée pour l'utilisateur si elle existe
    :param username : nom d'utilisateur pour la chambre forte
    :return : valeur hachée correspondante stockée si elle existe
    """
    conn, cursor = connect()

    cursor.execute(f'SELECT master_pwd FROM users WHERE username="{username}"')
    stored_master = cursor.fetchone()
    disconnect(conn)
    if stored_master is None:
        return None
    else:
        return stored_master[0]


def verify_user(i_username, i_master):
    """
    vérifier l'utilisateur en utilisant le nom d'utilisateur et le mot de passe principal
    :param i_username : entrée du nom d'utilisateur
    :param i_master : entrée du mot de passe principal
    :return : True et le mot de passe maître haché si vérifié
    """
    stored_master = get_stored_master(i_username)
    if stored_master is not None:
        return stored_master == i_master, stored_master
    else:
        return False, None


def chng_passwd(match, new_pass, key):
    """
    changer le mot de passe de l'entrée
    :param match : l'entrée que l'utilisateur veut supprimer
    :param new_pass : nouveau mot de passe pour l'application
    :param key : mot de passe maître haché
    :return :
    """
    del_passwd(match, key)
    plain_data = [match[0], match[1], new_pass]
    add_passwd(plain_data, key)


def encrypt_all(plain_data, key):
    """
    crypte l'entrée en clair
    :param plain_data : liste de app_name, username, password
    :param key : mot de passe maître haché
    :return : entrée chiffrée
    """
    cipher = AESCipher(key)
    enc_app_name = cipher.encrypt(plain_data[0])
    enc_username = cipher.encrypt(plain_data[1])
    enc_password = cipher.encrypt(plain_data[2])
    return [enc_app_name, enc_username, enc_password]


def decrypt_all(enc_data, key):
    """
      décrypte l'entrée chiffrée stockée dans la base de données
    :param enc_data : données cryptées de la base de données
    :param key : mot de passe maître haché
    :return : entrée décryptée en clair
    """
    cipher = AESCipher(key)
    app_name = cipher.decrypt(enc_data[0])
    username = cipher.decrypt(enc_data[1])
    password = cipher.decrypt(enc_data[2])
    return [app_name, username, password]
