import falcon
#from waitress import serve
from falcon_multipart.middleware import MultipartMiddleware
import os
import sys

class ImageResource(object):
    #def on_get(self, req, resp):
     #   resp.status = falcon.HTTP_200
     #   resp.body = "hello world"
    def on_post(self, req, resp):
        """
        POST METHOD
        """
        # Retrieve input_file
        input_file = req.get_param('file')
        
        # Test if the file was uploaded
        if input_file.filename:
            # Retrieve filename
            filename = input_file.filename

            # Define file_path
            file_path = os.path.join("images", filename)

            # Write to a temporary file to prevent incomplete files
            # from being used.
            temp_file_path = file_path + '~'

            open(temp_file_path, 'wb').write(input_file.file.read())

            # Now that we know the file has been fully saved to disk
            # move it into place.
            os.rename(temp_file_path, file_path)

            resp.status = falcon.HTTP_201
            resp.body = "hello world"

#app = falcon.API()
app = falcon.API(middleware=[MultipartMiddleware()])
app.req_options.auto_parse_form_urlencoded=True

things = ImageResource()

app.add_route('/api/upload', things)
#serve(app, listen='*:8080')