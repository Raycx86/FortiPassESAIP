import string

alphabet = string.ascii_letters #+ string.digits + string.punctuation

def keyLen(key):
    l_alphabet = len(alphabet)
    long = len(key)
    keyspace = l_alphabet ** long
    return keyspace

def keyTime(key):
    h = 2 * 10 # 2 * attaque par seconde
    keyTime = key / h
    return keyTime

password = input("Password ? : ")
keys = keyLen(password)
print(f"Keyspace : {keys}")
print("Time : ", keyTime(keys))