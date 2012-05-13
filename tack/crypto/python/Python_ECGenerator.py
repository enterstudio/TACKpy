import os
from .cryptomath import numberToBytes, bytesToNumber
from .ecdsa import generator_256
from .Python_ECPublicKey import Python_ECPublicKey
from .Python_ECPrivateKey import Python_ECPrivateKey

class Python_ECGenerator:
    
    @staticmethod
    def generateECKeyPair():
        # ECDSA key generation per FIPS 186-3 B.4.1
        # (except we use 32 extra random bytes instead of 8 before reduction,
        #  to be slightly paranoid in case there's an os.urandom bias)
        # Random bytes taken from os.urandom
        # REVIEW THIS CAREFULLY!  CHANGE AT YOUR PERIL!
        
        # Reduce a 64-byte value from os.urandom to a 32-byte secret key
        c = bytesToNumber(bytearray(os.urandom(64))) 
        n = generator_256.order()
        d = (c % (n-1))+1        
        rawPrivateKey = numberToBytes(d, 32)
        publicKeyPoint = generator_256 * d        
        rawPublicKey = (numberToBytes(publicKeyPoint.x(), 32) + 
                        numberToBytes(publicKeyPoint.y(), 32))
        return (Python_ECPublicKey(rawPublicKey), 
                Python_ECPrivateKey(rawPrivateKey, rawPublicKey))