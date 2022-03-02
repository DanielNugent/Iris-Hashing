import sys
import hashlib
from argon2 import PasswordHasher, exceptions
from random import randrange

from scipy import rand

if sys.version_info < (3, 6):
    import sha3

s = hashlib.sha3_256()

total_range = 100
random_int = randrange(total_range)
print(random_int)

data = f'aaaabbbbccccddddeeeeffffggghhhhaaaabbbbccccddddeeeeffffggghhhh{random_int}'
ph = PasswordHasher(parallelism=4, hash_len=32)
answer = "$argon2id$v=19$m=65536,t=3,p=4$NcCkD/Kkr52xUfN0+3D0rQ$ta/67wLRPDQLhU16nhRihgxkMrnJjtGNVwsBT9i3xxg"

verified = False
for i in range(10000):
    if(i % 100 == 0):
        print(i)
    try:
        verified = ph.verify(answer, f"{i}")
    # print(temp)
    except exceptions.VerifyMismatchError: 
        x = 1  
    
    if(verified):
        print(answer, i)
        break
