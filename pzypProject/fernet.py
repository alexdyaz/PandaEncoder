from cryptography.fernet import Fernet


def password(key):
	key = Fernet.generate_key()

	with open('filekey.key', 'wb') as filekey:
		filekey.write(key)
	return key


if __name__ == '__main__':
	password()
