import string
import random
from random import randrange

def id_generator(size=16, chars=string.ascii_letters + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))
