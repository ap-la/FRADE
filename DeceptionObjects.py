"""
Module to insert deception objects in the HTML string provided as a input
"""
import argparse,os,sys
import lxml.html
from lxml import etree
from copy import deepcopy
from lxml.html import html5parser
import cssutils
from cssselect import GenericTranslator, SelectorError
import cssselect
from PIL import Image
import random
import urlparse
import traceback

def printExceptions(startXPos):
    for line in traceback.format_exc().splitlines():
        print " "*startXPos+line

class FileIdRandGen():
    def __init__(self):
        #gives a random number which can be appended to a file name
        self.randGen = random.Random()
        self.minFileId = 10000
        self.maxFileId = 999999
    def get(self):
        return self.randGen.randint(self.minFileId,self.maxFileId)

class MyCssUtils:
    @staticmethod
    def setXpathForSelectors(xpathForSelectorsDict,parsedStyleSheetList):
        for parsedStyleSheet in parsedStyleSheetList:
            for rule in parsedStyleSheet.cssRules:
                if rule.type == rule.STYLE_RULE:
                    selectorsToBeRemoved = []
                    for selector in rule.selectorList:
                        selectorText = selector.selectorText
                        try:
                            xpathForSelector = GenericTranslator(
                                    ).css_to_xpath(selectorText)

                        except SelectorError as se:
                            if not se.__str__().startswith('Pseudo-elements'):
                                print "FRADEWARNING:","setXpathForSelector::"+\
                                        " parsing selector with pseudo "+\
                                        "elements not supported'"+\
                                        selector.selectorText+"'"
                            selectorsToBeRemoved.append(selector)
                            continue
                        """
                        try:
                            parsedSelectorsList = cssselect.parse(selectorText)
                        except cssselect.SelectorSyntaxError as se:
                            print "FRADEWARNING:","setXpathForSelector::"+\
                                    "invalid selector:'"+\
                                    selector.selectorText+"'"
                            for line in traceback.format_exc().splitlines():
                                print " "*4+line
                            selectorsToBeRemoved.append(selector)
                            continue
                        """
                        """
                        lenght of parsedSelectorsList should be always 1, 
                        as selector from rule.selectorList as already ungrouped
                        """
                        """
                        if len(parsedSelectorsList) > 1:
                            print "FRADEERROR:","setXpathForSelector::"+\
                                    " selector from rule.selectorList "+\
                                    "cannot be a group selector'"+\
                                    selector.selectorText+"'"
                        parsedSelector = parsedSelectorsList[0]
                        try:
                            xpathForSelector = GenericTranslator(
                                    ).selector_to_xpath(parsedSelector)
                        except cssselect.ExpressionError as se:
                            if not se.__str__().startswith('Pseudo-elements'):
                                print "FRADEWARNING:","setXpathForSelector::"+\
                                        " parsing selector with pseudo "+\
                                        "elements not supported:'"+\
                                        selector.selectorText+"'"
                            else:
                                print "FRADEWARNING:","setXpathForSelector::"+\
                                        " unknown/unsupported selector:'"+\
                                        selector.selectorText+"'"
                                for line in traceback.format_exc().splitlines():
                                    print " "*4+line
                            selectorsToBeRemoved.append(selector)
                            continue
                        """
                        keySelector = None
                        #keyselector of type id, class or element
                        basicKeySelector = None
                        xpathForBasicKeySelector = None
                        """"
                        if isinstance(parsedSelector.parsed_tree,
                                cssselect.parser.CombinedSelector):
                            keySelector = parsedSelector.parsed_tree.subselector
                        else:
                            keySelector = parsedSelector.parsed_tree
                        """
                        """
                        print " "*4,"Selector:",selectorText
                        print " "*4,"ParsedSelector:",str(parsedSelector)
                        print " "*4,"KeySelector",str(keySelector)
                        print "\n"
                        """
                        """
                        if isinstance(keySelector, (cssselect.parser.Class,
                            cssselect.parser.Hash, cssselect.parser.Element)):
                            basicKeySelector = cssselect.Selector(keySelector)
                            xpathForBasicKeySelector = GenericTranslator(
                                    ).selector_to_xpath(basicKeySelector)
                        """
                        xpathForSelectorsDict[selectorText] = {
                                'xpathForSelector':xpathForSelector,
                                'xpathForBasicKeySelector':xpathForBasicKeySelector}
                    #remove all un-supported selectors
                    for selector in selectorsToBeRemoved:
                        rule.selectorList.seq.remove(selector)

        
class DeceptionObjectsError(Exception):
    pass
class DeceptionObjects():
    def __init__(self,isProxyMode,webSiteWeAreProtecting,webSiteRoot,
            embeddedObjectsDir):
        self.fileIdRandGen = FileIdRandGen()
        self.__fradeCustomIdString = "fradeCustomId"
        self.isProxyMode = isProxyMode
        self.webSiteWeAreProtecting = webSiteWeAreProtecting
        self.webSiteRootDir = webSiteRoot
        self.embeddedObjectsDir = embeddedObjectsDir

    def insertObjects(self,inputHtmlString,insertMethod,ratioOfTotObjsToDecObjs):
        #parse the inputHTML
        #print "inputHTML:",inputHtml
        #parsedInputDoc = html5lib.parse(inputHtml)
        #htmlDomTreeParser = html5lib.HTMLParser(tree=html5lib.getTreeBuilder("dom"))
        #parsedInputDoc =  htmlDomTreeParser.parse(inputHtml)
        try:
            parsedInputDoc =  lxml.html.fromstring(inputHtmlString).getroottree()
            #parsedInputDoc =  lxml.html.parse(inputHtml)
        except lxml.etree.ParseError as e:
            print "Error: insertObjects parsing html document::"+e.__str__()
            raise
        #parsedInputDoc =  lxml.html.parse(StringIO(inputHtml))
        #parsedInputDoc =  html5parser.fromstring(inputHtml)
        #print dir(parsedInputDoc)
        """
        add custom id's to all the html elements
        by setting fradeCustomId attribute
        """
        elementCustomId = 0
        for htmlElement in parsedInputDoc.getroot().iterdescendants(
                tag=etree.Element):
            htmlElement.set(self.__fradeCustomIdString,str(elementCustomId))
            elementCustomId += 1
        """
        create a dictionary of elements from a copy 
        of parsedInputDoc to set styles
        """
        elementsDict = {}
        for htmlElement in deepcopy(parsedInputDoc).getroot().iterdescendants(
                tag=etree.Element):
            elementsDict[htmlElement.get(
                self.__fradeCustomIdString)] = htmlElement
        """
        styleSheetList contains style sheets in LINK tag or inside STYLE tag
        """
        styleSheetList = []
        #data strutucture to store parsed selectors
        xpathForSelectorsDict = {}
        for htmlElement in parsedInputDoc.find('head').iter():
            parsedSS = None
            parsingFunc = None
            parsingFuncArgs = None
            if htmlElement.tag == "link" and htmlElement.get('rel') == "stylesheet":
                hrefValue = htmlElement.get('href')
                if self.isProxyMode:
                    #if relative url, then make it absolute url
                    #TODO:
                    # ideally we should read this value when a corresponding
                    # request arrives, save it and then use it in the 
                    # corresponding response to open the relative files
                    # (for ex: css, images etc)
                    if not bool(urlparse.urlparse(hrefValue).scheme):
                        hrefValue = urlparse.urljoin(
                                self.websiteWeAreProtecting,hrefValue)
                    parsingFunc = getattr(cssutils,"parseUrl")
                    parsingFuncArgs = {'href':hrefValue}
                else:
                    # if css is hosted on other location
                    if bool(urlparse.urlparse(hrefValue).scheme):
                        parsingFunc = getattr(cssutils,"parseUrl")
                        parsingFuncArgs = {'href':hrefValue}
                    else:
                        parsingFunc = getattr(cssutils,"parseFile")
                        cssFile = os.path.join(self.webSiteRootDir,hrefValue)
                        parsingFuncArgs = {'filename':cssFile}
            elif str(htmlElement.tag).lower() == "style":
                #parsedSS = cssutils.parseString(htmlElement.text)
                parsingFunc = getattr(cssutils,"parseString")
                parsingFuncArgs = {'cssText':htmlElement.text}
            else:
                continue
            try:
                parsedSS = parsingFunc(**parsingFuncArgs)
            except IOError, ioe:
                print "FRADEERROR:","CSS file opening error::",str(parsingFuncArgs),"::",str(ioe)
                for line in traceback.format_exc().splitlines():
                    print " "*4+line
                continue
            except:
                print "FRADEERROR:","parsing CSS file::"
                for line in traceback.format_exc().splitlines():
                    print " "*4+line
                continue
            styleSheetList.append(parsedSS)
            #pre compute xpath for selectors
            MyCssUtils.setXpathForSelectors(xpathForSelectorsDict,styleSheetList)
        for htmlElement in parsedInputDoc.getroot().iterdescendants(
                tag=etree.Element):
            countOfObjectsInserted = 0
            if htmlElement.tag == "img":
                print "FRADEINFORMATION:",htmlElement.tag, "inserting images"
                self.insertImageBelowIMG(htmlElement,self.embeddedObjectsDir,
                        styleSheetList,elementsDict,xpathForSelectorsDict)
            countOfObjectsInserted += 1
            if countOfObjectsInserted > 10:
                break
        """
        remove the frade custom id attribute
        """
        lxml.etree.strip_attributes(parsedInputDoc,self.__fradeCustomIdString)
        return lxml.html.tostring(parsedInputDoc,
                method='html',doctype=parsedInputDoc.docinfo.doctype,
                encoding=parsedInputDoc.docinfo.encoding,pretty_print=True)

    "styleDeclaration2 will be added to styleDeclaration1"
    def addStyleDeclarations(self,styleDeclaration1,styleDeclaration2):
        for styleProperty in styleDeclaration2.getProperties():
            styleDeclaration1.setProperty(styleProperty.name,styleProperty.value,
                    replace=True)

    def getStyleDeclarationFromCSSRule(self,inputElement,rule,elementsDict,
            xpathForSelectorsDict):
        for selector in rule.selectorList:
            #selector.selectorText
            xpathForSelector = xpathForSelectorsDict[
                    selector.selectorText]['xpathForSelector']
            xpathForBasicKeySelector = xpathForSelectorsDict[
                    selector.selectorText]['xpathForBasicKeySelector']
            if xpathForBasicKeySelector:
                """
                let's try to match basic key selector first, 
                if it doesn't match, then complete selector 
                won't match for sure, so continue to next selector
                """
                matchedElements = inputElement.xpath(xpathForBasicKeySelector)
                for element in matchedElements:
                    if (element.get(self.__fradeCustomIdString)) == (
                        inputElement.get(self.__fradeCustomIdString)):
                        break;
                #no match, move to next selector
                continue
                

            matchedElements = inputElement.getroottree().xpath(
                    xpathForSelector)
            for element in matchedElements:
                if (element.get(self.__fradeCustomIdString)) == (
                        inputElement.get(self.__fradeCustomIdString)):
                    return rule.style
        #if no matching rule, then return empty style
        return cssutils.css.CSSStyleDeclaration()

    def getElementStyleFromCSS(self,inputElement,parsedStyleSheet,elementsDict,
            xpathForSelectorsDict):
        elementStyle = cssutils.css.CSSStyleDeclaration()
        for rule in parsedStyleSheet.cssRules:
            if rule.type == rule.STYLE_RULE:
                styleDeclaration = self.getStyleDeclarationFromCSSRule(
                        inputElement,rule,elementsDict,xpathForSelectorsDict)
                self.addStyleDeclarations(elementStyle,styleDeclaration)

        return elementStyle

    def getElementStyle(self,inputElement,parsedStyleSheets,elementsDict,
            xpathForSelectorsDict):
        elementStyle = cssutils.css.CSSStyleDeclaration()
        for parsedStyleSheet in parsedStyleSheets:
            curStyle = self.getElementStyleFromCSS(inputElement,
                    parsedStyleSheet,elementsDict,xpathForSelectorsDict)
            self.addStyleDeclarations(elementStyle,curStyle) 
        return elementStyle


    #insert images associated with decoy hyperlink underneath the IMG tags 
    #images can be transparent, same as background color or any other color
    #choose randomly
    def insertImageBelowIMG(self,inputImgTag,embeddedObjectsDir,parsedStyleSheets,
            elementsDict,xpathForSelectorsDict):
        """
        get the style properties of the inputImgTag
        """
        inputImgTagStyle = self.getElementStyle(inputImgTag,parsedStyleSheets,
                elementsDict,xpathForSelectorsDict)
        inputImageLocation = inputImgTag.get("src")
        # TODO: support embedding image on images with absolute urls
        # check if image location is a url, if yes ignore for now
        if bool(urlparse.urlparse(inputImageLocation).scheme):
            return False
        #get the image location of image to be inserted
        outputImageLocation = self.getOutputImageLocation(inputImageLocation)

        inputImageAbsLoc =  os.path.join(self.webSiteRootDir,inputImageLocation)
        outputImageAbsLoc =  os.path.join(embeddedObjectsDir,outputImageLocation)
        
        #create the directory where these images will be stored
        try:
            os.makedirs(os.path.join(self.embeddedObjectsDir,
                os.path.dirname(outputImageLocation)))
        except OSError:
            #directory already exists, we don't have to anything
            pass
        # create the image to be inserted
        # there is possibility that file extension might be changed by 
        # createImageToBeInserted while creating transparent files
        newOutputImageAbsLoc = self.createImageToBeInserted(inputImageAbsLoc,
                None,None,None,outputImageAbsLoc)
        if newOutputImageAbsLoc == None:
            #creation of image to be inserted is failed
            print "FRADEERROR:","insertImageBelowIMG:: "+\
                    "image creation failed for image ",str(inputImgTag.get("src"))
            return False
        if newOutputImageAbsLoc != outputImageAbsLoc:
            outputImageAbsLoc = newOutputImageAbsLoc
            # as only possible change could be change of extension
            # we just need to update the extension
            outputImageLocation = os.path.splitext(outputImageLocation)[0]+\
                    os.path.splitext(newOutputImageAbsLoc)[1]
        # get the decoy hyper link, name should be something similar to the inputImage
        decoyHyperLink = self.getDecoyHyperLink(inputImageLocation)

        divTag = etree.Element("div",id="div1",style="position:relative;")

        parentElement = inputImgTag.getparent()
        isInputImgTagChildOfATag = False
        inputATag = None
        if parentElement.tag.lower() == "a":
            isInputImgTagChildOfATag = True

        if isInputImgTagChildOfATag:
            inputATag = parentElement
            parentElement = inputImgTag.getparent().getparent()
            parentElement.replace(inputATag,divTag)
        else:     
            parentElement.replace(inputImgTag,divTag)
        insertedImgTag = deepcopy(inputImgTag)
        #get an image file with same size as the input
        insertedImgTag.set("src",outputImageLocation)
        #get decoy hyper link element
        decoyATag = etree.Element("a",href=decoyHyperLink)
        #append insertedImgTag to decoyATag
        decoyATag.append(insertedImgTag)
        #append the decoyATag first to the div tag
        #divTag.insert(0,decoyATag)
        divTag.append(decoyATag)
        #place htmlElement on top of insertedImgTag
        styleOfHtmlElement = inputImgTag.get("style")
        styleToBeAdded = "position:absolute;top:0;left:0;"
        floatPropertyValue = inputImgTagStyle.getPropertyCSSValue('float',normalize=True)
        if floatPropertyValue:
            if floatPropertyValue.value== "right":
                styleToBeAdded = "position:absolute;top:0;right:0;" 

        if styleOfHtmlElement:
            inputImgTag.set("style",styleOfHtmlElement+styleToBeAdded)
        else:
            inputImgTag.set("style",styleToBeAdded)

        if isInputImgTagChildOfATag:
            divTag.append(inputATag)
        else:
            #divTag.insert(1,htmlElement)
            divTag.append(inputImgTag)
        
        # create a symlink for the inserted image
        symlink = os.path.join(self.webSiteRootDir,outputImageLocation)
        # if symlink exist exists then just use it
        # though possibliity is very unlikely
        if not os.path.exists(symlink):
            os.symlink(outputImageAbsLoc,symlink)
        print "FRADEINFORMATION:","image inserted:",outputImageLocation
        return True

    #insert transparent images associated with decoy hyperlink above the IMG tags 
    def insertImagesAboveIMG(self,htmlElement):
        pass
    #insert texts associated with docoy hyperlink
    def insertText(self,htmlElement):
        pass
    #get decoyhyper link
    def getDecoyHyperLink(self,inputLocation):
        #site = "index"
        #site = "http://www.isi.edu/"
        # TODO: for now just use same method generate file names for decoy objects
        # inserted objects
        decoyLocation = self.getOutputImageLocation(inputLocation)
        #return site+decoyLocation.lstrip("/")
        return decoyLocation.lstrip("/")

    #get output image location for input image location which looks similar
    def getOutputImageLocation(self,inputImageLocation):
        #TODO: try other methods to acheive 
        #      - more similarity
        #      - absolutely no pattern means naming should be random
        iIL = inputImageLocation
        fileId = self.fileIdRandGen.get()
        return os.path.join(os.path.dirname(iIL),str(fileId)+"_"+
                os.path.basename(iIL))
        
    #create an image with same size as the input image
    def createImageToBeInserted(self,inputImageAbsLoc,size,color,colorMode,
            outputImageAbsLoc):
        inputImage = None
        print "FRADEINFORMATION: createImageToBeInserted: inputImageAbsLoc: "+\
                inputImageAbsLoc+" , outputImageAbsLoc: "+outputImageAbsLoc
        try:
            inputImage = Image.open(inputImageAbsLoc)
        except IOError:
            print "FRADEERROR: createImageToBeInserted: cannot read inputImage "+\
                    inputImageAbsLoc
            return False
        if size == None: size = inputImage.size
        if color == None: color = "red"
        if colorMode == None: colorMode = inputImage.mode
        imageFormat = inputImage.format
        
        #1. This method of checking transparency is incorrect.
        #2. There could be a case that image uses RGBA mode but 
        #    doesn't use transparency at all.but this is a rare possiblity.
        #3. In addition this issue doesn't cause any damage, 
        #    as we can proceed with transparent image 
        #    although we don't need the transparency

        if (colorMode == "RGBA") or ("transparency" in inputImage.info):
            #TODO: support transparent image creation without any ext change
            # create a transparent image, for simplicity only with pn format
            outputImageAbsLoc = os.path.splitext(outputImageAbsLoc)[0]+".png"
            colorMode = "RGBA"
            imageFormat = "PNG"
            color=(0,0,0,0)
        else:
            #for simplicity just fix the  color and format for now
            #colorMode = "RGB"
            #imageFormat = "JPEG"
            pass
        try:
            outputImage = Image.new(colorMode,inputImage.size,color)
            # if file with same absname already exist, then
            # delete that one, though possibility is very unlikely
            # this is done to avoid any file creation issues faced by 
            # outputImage.save() method
            if os.path.exists(outputImageAbsLoc):
                os.remove(outputImageAbsLoc)
            #TODO: not working with jpeg due to library path issue, fix it
            outputImage.save(outputImageAbsLoc,imageFormat)
            return outputImageAbsLoc
        except IOError, ioe:
            print "FRADEERROR: createImageToBeInserted: cannot write outputImage "+\
                    outputImageAbsLoc,"::",str(ioe)
            for line in traceback.format_exc().splitlines():
                print " "*4+line
            return None
        except:
            print "FRADEERROR:createImageToBeInserted:",\
                    "INPUT{'colorMode':"+str(colorMode)+\
                    ",'inputImage.size':"+str(inputImage.size)+\
                    ",'color':"+str(color)+\
                    ",'outputImageAbsLoc':"+str(outputImageAbsLoc)+\
                    ",'imageFormat':"+str(imageFormat)+"}::"
            for line in traceback.format_exc().splitlines():
                print " "*4+line
            return None
        return None
