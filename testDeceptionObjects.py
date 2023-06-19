import argparse,os,sys
#add the parent directory to the python path
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from DeceptionObjects import DeceptionObjects


# parse commandline arguments
def parseCmdArgs():
    desc = "insert deception objects in the input files"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-i", "--htmlFiles", required= True, 
            default=None, nargs = '*',
            help="input html file")
    args = parser.parse_args()
    return args

if __name__ =="__main__":
    #parse commandlist arguments    
    args = parseCmdArgs()
    #iDO.insertObjects("<HTML>HELLO</HTML>","allobjects")
    for htmlFile in args.htmlFiles:
        htmlInStream = None
        try:
            htmlInStream = open(htmlFile,"rb")
        except IOError:
            print "ERROR: Opening input html file: ", htmlFile
            exit(0)
        print "htmlFile:",os.path.dirname(os.path.abspath(htmlFile))
        
        #to tell we are running frade in proxy mode
        isProxyMode = False
        websiteWeAreProtecting = "http://www.isi.edu"
        webServerRootDir = os.path.dirname(os.path.abspath(htmlFile))
        # remove leading / using lstrip, 
        # as join will not correctly join it with first path
        embeddedObjectsDir = os.path.join(webServerRootDir,"embeddedObjects/".lstrip("/"))
        try:
            os.makedirs(embeddedObjectsDir)
        except OSError:
            #directory already exists, we don't have to do anything
            pass

        iDO = DeceptionObjects(isProxyMode,websiteWeAreProtecting,
                webServerRootDir,embeddedObjectsDir)
        outputHtml = iDO.insertObjects(htmlInStream.read(),"allobjects",4)
        """
        outputHtml = iDO.insertObjects(htmlFile,"allobjects",4,
                os.path.dirname(os.path.abspath(htmlFile)))
        """
        #print outputHtml
        outputHtmlFile = os.path.join(webServerRootDir,os.path.basename(htmlFile)+
                ".modified.html")
        try:
            htmlOutStream = open(outputHtmlFile,"wb")
        except IOError:
            print "ERROR: Opening output html file: ", outputHtmlFile
            exit(0)
        htmlOutStream.write(outputHtml)
