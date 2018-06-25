#coding:utf-8
# write  by  zhou


from Crypto.Cipher import  AES
import  sys
import  base64
if sys.getdefaultencoding()!="utf8":
    reload(sys)
    sys.setdefaultencoding("utf8")
def aes_encrypt(key,string):
    aes=AES.new(key)
    string+="Gc654321"
    string+=(32-len(string))*" "
    _u=aes.encrypt(string)
    return  base64.b64encode(_u)

def aes_decrypt(key,string):
    _u=base64.b64decode(string)
    aes=AES.new(key)
    _u=aes.decrypt(_u)
    assert  _u.count("Gc654321")==1
    return  _u.strip().replace("Gc654321","")

if __name__=="__main__":
    a=aes_encrypt("1111111111111111","1111111111")
    print a
    print aes_decrypt("1111111111111111",a)
    key="1"*32
    key="bxapp"+key[15:]
    print aes_encrypt("1111111111111111",key)