import sys
import hashlib
from typing import Type
import argon2
import time
from random import randrange


start = time.time()

ph = argon2.PasswordHasher(parallelism=4, hash_len=32, salt_len=32, type=argon2.Type.I, memory_cost=2000000, time_cost=6)
answer = "$argon2id$v=19$m=65536,t=3,p=4$NcCkD/Kkr52xUfN0+3D0rQ$ta/67wLRPDQLhU16nhRihgxkMrnJjtGNVwsBT9i3xxg"
print(ph.hash("correct horse battery staple"))


print("time taken : ", time.time() - start)
