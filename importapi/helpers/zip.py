import os
import zipfile

from builtins import str as text


class Unzipper(object):

    def __init__(self, filepath):
        self.relative_zip_dir = '/zip'
        self.filepath = filepath

    def unzip(self):
        basedir = os.path.dirname(self.filepath)
        self.zipdir = basedir + self.relative_zip_dir
        os.makedirs(self.zipdir)
        zip = zipfile.ZipFile(self.filepath)
        infolist = zip.infolist()
        for info in infolist:
            info.filename = ''.join(i if i.isalnum() or i == '.' else '_' for i in info.filename)
            zip.extract(info, text(self.zipdir))
        #zip.extractall(self.zipdir)
        # zip.extractall(self.zipdir)
        zip.close()

    def find_layer_file(self):
        for (dirpath, dirnames, filenames) in os.walk(self.zipdir):
            for filename in filenames:
                filepath = dirpath + '/' + filename
                extension = os.path.splitext(filename)[1]
                if extension and extension.lower() in ['.json', '.geojson', '.shp']:
                    self.filepath = filepath
                    return self.filepath
