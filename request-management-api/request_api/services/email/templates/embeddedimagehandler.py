
from bs4 import BeautifulSoup
import base64

"""
This class is leveraged to handle the embedded images in mail body.
    
"""
class embeddedimagehandler:

    """
    This function can be enhanced to store the image in S3 & re-use (if required)
    Please note; in case of storing in S3. This function should be invoked before persisting to DB. 
    """
    def formatembeddedimage(self, content):
        soup = BeautifulSoup(content, "html.parser")
        img_nodes = soup.find_all("img")
        embeddedimages = []
        for img in img_nodes:
            if 'base64' in img['src']:
                imgsrc = img['src']
                imagename = "image"+str(len(embeddedimages))
                img['src'] = "cid:"+imagename
                img['style'] = "width:180px;height:50px;"
                imgbytes = imgsrc.split("base64,")[1]
                embeddedimages.append({"cid": imagename, "bytes": base64.b64decode(str(imgbytes)), 'type': self.__getmimetype(imgsrc)})
        return soup.prettify(), embeddedimages


    def __suportedmimetypes(self):
        return [
        { "prefix": "/9j/", "mimetype" : "image/jpg", "extension": "jpg"},
        { "prefix": "iVBORw0KGgo", "mimetype" : "image/png", "extension": "png"}
        ]


    def __getmimetype(self, b64):
        for entry in self.__suportedmimetypes():
            if entry['prefix'] in b64:
                return entry['extension'] 
