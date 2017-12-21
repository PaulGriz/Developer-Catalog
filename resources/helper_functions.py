import random
import string


class Helpers():
    
    def create_state_token():
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
        return state