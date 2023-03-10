from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.Cipher import AES
from base64 import b64encode, b64decode

def hashed(text):
    """
    hachage du texte brut
    :param text : texte brut
    :return : texte lisible haché en hexadécimal
    """
    h = SHA256.new(text.encode())
    hashed_text = h.hexdigest()
    return hashed_text


def digest(key):
    """
    digérer le texte en clair
    :param key : texte en clair
    :return : texte haché
    """
    h = SHA256.new(key.encode())
    hashed_text = h.digest()
    return hashed_text


class AESCipher(object):
    def __init__(self, key):
        self.block_size = AES.block_size
        self.key = digest(key)

    def encrypt(self, plain_text):
        """
        crypte le texte en clair
        :param plain_text :
        :return : texte crypté
        """
        plain_text = self.__pad(plain_text)
        iv = Random.new().read(self.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted_text = cipher.encrypt(plain_text.encode())
        return b64encode(iv + encrypted_text).decode("utf-8")

    def decrypt(self, encrypted_text):
        """
        décrypte le texte crypté
        :param encrypted_text :
        :return : texte en clair
        """
        encrypted_text = b64decode(encrypted_text)
        iv = encrypted_text[:self.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plain_text = cipher.decrypt(encrypted_text[self.block_size:]).decode("utf-8")
        return self.__unpad(plain_text)

    def __pad(self, plain_text):
        """
        ajoute au texte brut le remplissage nécessaire au cryptage.
        :param plain_text :
        :return : texte chiffré
        """
        number_of_bytes_to_pad = self.block_size - len(plain_text) % self.block_size
        ascii_string = chr(number_of_bytes_to_pad)
        padding_str = number_of_bytes_to_pad * ascii_string
        padded_plain_text = plain_text + padding_str
        return padded_plain_text

    @staticmethod
    def __unpad(plain_text):
        """
        supprime le texte supplémentaire paddé du texte décrypté
        :param plain_text :
        :return : texte brut actuel
        """
        last_character = plain_text[len(plain_text) - 1:]
        return plain_text[:-ord(last_character)]
