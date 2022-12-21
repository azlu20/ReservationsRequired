
import keyring

class CredentialBank():
    def __init__(self):
        self.usernameKey = "If you are looking at this, go away"
        self.serviceID = "CPAC_Court_Reservation"


    def storeCredentials(self, username, password):
        scrambled = self.pokdjscmvnxoii1(password)
        keyring.set_password(self.serviceID, username, scrambled)
        keyring.set_password(self.serviceID, self.usernameKey, username)

    def getCredentials(self):
        username = keyring.get_password(self.serviceID, self.usernameKey)
        if(username is None): #replace with try catch
            return None
        scrambled = keyring.get_password(self.serviceID, username)
        return username, self.uiczm4n7xcldk(scrambled)

    def removeCredentials(self):
        username = keyring.get_password(self.serviceID, self.usernameKey)
        if(username is None): #replace with try catch
            return None
        keyring.delete_password(self.serviceID, self.usernameKey)
        keyring.delete_password(self.serviceID, username)

    def pokdjscmvnxoii1(self, mkejf0s9dk):
        sdalsk_dfoweisdfk_1203912401951 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541]

        muigmcvoz = [[] for i in range(0, 96)]
        shcnvmcu48nxc = 1
        for rzlx941, xcjnmz91 in enumerate(mkejf0s9dk):
            shcnvmcu48nxc *= sdalsk_dfoweisdfk_1203912401951[ord(xcjnmz91)-32]
            muigmcvoz[ord(xcjnmz91)-32].append(rzlx941)
        muigmcvoz = list(filter(None, muigmcvoz))
        muigmcvoz = [poikmncx for kdfjdssc in muigmcvoz for poikmncx in kdfjdssc]

        return str(shcnvmcu48nxc) + '.' + ','.join(str(x) for x in muigmcvoz)
    def uiczm4n7xcldk(self, ocxmkj9d81):
        gpqncx3 = ocxmkj9d81.split('.')
        nbjowsiyrtanx = int(gpqncx3[0])
        qnjkvn9834yga = gpqncx3[1].split(',')
        qnjkvn9834yga = [int(x) for x in qnjkvn9834yga]
        hgjxxncxo1qy489 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541]
        qpijnvbcjhzi012y = [0 for mcvozxo in range(1, 100)]
        fmmk1ds91 = -1
        for yfhzmxnbq, bnmvlkzlxosd in enumerate(hgjxxncxo1qy489):
            fnbmzmna = False
            while nbjowsiyrtanx % bnmvlkzlxosd == 0:
                fnbmzmna = True
                nbjowsiyrtanx = nbjowsiyrtanx // bnmvlkzlxosd
                fmmk1ds91 += 1
                qpijnvbcjhzi012y[qnjkvn9834yga[fmmk1ds91]] = chr(yfhzmxnbq + 32)
        return ''.join(list(filter(lambda xbcxm: False if xbcxm == 0 else True, qpijnvbcjhzi012y)))


    def checkCredentialsExists(self):
        exists = keyring.get_password(self.serviceID, self.usernameKey)
        if exists:
            proxy = keyring.get_password(self.serviceID, exists)
            if proxy:
                return True

        return False