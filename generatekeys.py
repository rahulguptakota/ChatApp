import os
from Crypto.PublicKey import RSA
from Crypto import Random

rng = Random.new().read
RSAkey = RSA.generate(1024, rng) 

privatekey = RSAkey
publickey = RSAkey.publickey()
print(privatekey.exportKey()) #export under the 'PEM' format (I think)
print(publickey.exportKey())

file = open("Keys.txt", "wb")
file.write(privatekey.exportKey()+("\n").encode()) #save exported private key
file.write(publickey.exportKey())
file.close()