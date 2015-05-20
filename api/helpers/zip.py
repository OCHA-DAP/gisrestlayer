import os
import zipfile


class Unzipper(object):

    def __init__(self, filepath):
        self.relative_zip_dir = '/zip'
        self.filepath = filepath

    def unzip(self):
        basedir = os.path.dirname(self.filepath)
        self.zipdir = basedir + self.relative_zip_dir
        os.makedirs(self.zipdir)
        zip = zipfile.ZipFile(self.filepath)
        zip.extractall(self.zipdir)
        zip.close()

    def find_layer_file(self):
        for (dirpath, dirnames, filenames) in os.walk(self.zipdir):
            for filename in filenames:
                filepath = dirpath + '/' + filename
                extension = os.path.splitext(filename)[1]
                if extension and extension.lower() in ['.json', '.geojson', '.shp']:
                    self.filepath = filepath
                    return self.filepath
