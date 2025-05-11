"""
Module for generating RIDs (Random IDs)
"""

import random
import string



def generate():
    """
    Generates a RID (Random ID)  
    Comprised of 6 simbols (ascii_lowercase + digits)
    """
    return ''.join(random.choices(
        string.ascii_lowercase+string.digits,
        k=6
    ))