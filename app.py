import random
import string

from ItemProject import app
app.secret_key = "".join(random.choice(string.punctuation + string.ascii_letters) for i in range(32))
app.debug = True