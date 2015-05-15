import os
import subprocess
import hashlib
import sys
from glob import glob
import urllib.request, json
from urllib.request import urlretrieve
import urllib
import sip

#reporthook for urlretrieve, prints file completion
def report(count, blockSize, totalSize):
    percent = min(int(count*blockSize*100/totalSize),100)
    sys.stdout.write("\r%2d%%" % percent)
    sys.stdout.flush()

class Patcher():

    def __init__(self):
        #This will later be used for JSON building
        self.versionurl = "" #Url to the latest version.json that will be used to diff the files in the current working directory
        self.downloadurl = "url"+"/download?path=" #Link to the url where the files will be downloaded

    #Download the version.json from the server
    #Latest version
    def getVersion(self):
        with urllib.request.urlopen(self.versionurl) as url:
            data = url.read()
        if data: return json.loads(data.decode('utf-8'))

    #This downloads and saves a file to the right place
    #filename needs to be the full route
    #Route also needs to be the same on the request and the server
    def download(self, filename):
        url = "http://"+self.downloadurl+filename
        try:
            dir = os.path.dirname(filename)
            # create directory if it does not exist
            if not os.path.exists(dir):
                os.makedirs(dir)
            # Create blank file if it does not exist
            with open(filename, "w"):
                pass

            u = urllib.request.urlretrieve(url, filename,reporthook=report)
        except:
            e = sys.exc_info()[0]
            raise e

    #This handles the patching logic
    #If a file is different from the servers, or doesn't exists, it downloads it
    #If it's the same, don't download it
    #TODO:
    #   Add support for ini files
    #   Maybe git/perforce/SVN support? Right now it just downloads off a web server
    def initPatcher(self):
        latestversion = self.getVersion()
        with open('version.json') as version:
            myversion = json.load(version)

        for filepath, hashvalue in latestversion.items():
            if filepath in myversion:
                if hashvalue == myversion[filepath]:
                    continue
                else:
                    print(filepath)
                    try:
                        print("\nDownloading: "+filepath+"\n")
                        self.download(filepath)
                    except:
                        e = sys.exc_info()[0]
                        print(e)
                        return False
            else:
                try:
                    print("\nDownloading: "+filepath+"\n")
                    self.download(filepath)
                except:
                    e = sys.exc_info()[0]
                    return False
                    print(e)
        return "Success!"

    #Found md5 hasher on Stackoverflow
    #http://stackoverflow.com/questions/1131220/get-md5-hash-of-big-files-in-python
    def md5_for_file(self, path, block_size=256*128, hr=False):
        '''
        Block size directly depends on the block size of your filesystem
        to avoid performances issues
        Here I have blocks of 4096 octets (Default NTFS)
        '''
        md5 = hashlib.md5()
        with open(path,'rb') as f:
            for chunk in iter(lambda: f.read(block_size), b''):
                 md5.update(chunk)
        if hr:
            return md5.hexdigest()
        return md5.digest()

    #Makes file hashes and writes them to a .json file
    def getHashTable(self):
        files = []
        start_dir = "."
        pattern   = "*"
        hashfiles = {}
        hashseq = []
        banlist = []

        for dir,_,_ in os.walk(start_dir):
            files.extend(glob(os.path.join(dir,pattern)))

        for y in files:
            if os.path.isdir(y):
                continue
            cont = False
            for x in banlist:
                if y == x:
                    cont = True
            if cont:
                continue
            hashseq.extend(tuple(tuple([[y]+[self.md5_for_file(y,256*128,True)]])))
            #print(hashseq)
        hashfiles = dict(hashseq)
        jsonx = json.dumps(hashfiles, sort_keys=True,indent=4)
        with open("version.json","w+") as f:
            f.write(jsonx)



def main():
    main = Patcher()
    main.getHashTable()

def patch():
    main = getFileHash()
    var = main.initPatcher()
    return var

if __name__ == '__main__':
    main()
    patch()
