"""
.. module:: merkabah.core.files
   :synopsis: Contains a set of helpers for working with blobs and files

.. moduleauthor:: Blaine Garrett <blaine@blainegarrett.com>

"""

from google.appengine.ext import blobstore

def create_upload_url(url):
    """Grabs the gae_lib_path from the options and inserts it into the first
    index of the sys.path. Then calls GAE's fix_sys_path to get all the proper
    GAE paths included.

    :param url: asdf sd;flksdfl;ksdf sdfds
    """

    return blobstore.create_upload_url(url)

def get_uploads(request, field_name=None, populate_post=False):
    import logging
    from google.appengine.ext import blobstore            
    import cgi
    """Get uploads sent to this handler.
    Args:
      field_name: Only select uploads that were sent as a specific field.
      populate_post: Add the non blob fields to request.POST
    Returns:
      A list of BlobInfo records corresponding to each upload.
      Empty list if there are no blob-info records for field_name.
      http://pastebin.com/9haziPhd
    """
        
    if hasattr(request,'__uploads') == False:
        request.META['wsgi.input'].seek(0)
        fields = cgi.FieldStorage(request.META['wsgi.input'], environ=request.META)

        request.__uploads = {}
        if populate_post:
            request.POST = {}
        
        for key in fields.keys():
            field = fields[key]
            if isinstance(field, cgi.FieldStorage) and 'blob-key' in field.type_options:
                blob_info = blobstore.parse_blob_info(field)
                
                request.__uploads.setdefault(key, []).append(blob_info)
                if populate_post:
                    request.POST[key] = [str(blob_info.key())]
                
            elif populate_post:
                request.POST[key] = []
                if isinstance(field, list):                
                    for item in field:
                        request.POST[key].append(item.value)
                else:
                    request.POST[key] = [field.value]
    
    if field_name:
        try:
            return list(request.__uploads[field_name])
        except KeyError:
            return []
    else:
        results = []
        for uploads in request.__uploads.itervalues():
            results += uploads
        return results

def rescale(img_data, width, height, halign='middle', valign='middle'):
  from google.appengine.api import images
  """Resize then optionally crop a given image.

  Attributes:
    img_data: The image data
    width: The desired width
    height: The desired height
    halign: Acts like photoshop's 'Canvas Size' function, horizontally
            aligning the crop to left, middle or right
    valign: Verticallly aligns the crop to top, middle or bottom

  """

  image = images.Image(img_data)      

  desired_wh_ratio = float(width) / float(height)
  wh_ratio = float(image.width) / float(image.height)

  if desired_wh_ratio > wh_ratio:
    # resize to width, then crop to height
    image.resize(width=width)
    image.execute_transforms()
    trim_y = (float(image.height - height) / 2) / image.height
    if valign == 'top':
      image.crop(0.0, 0.0, 1.0, 1 - (2 * trim_y))
    elif valign == 'bottom':
      image.crop(0.0, (2 * trim_y), 1.0, 1.0)
    else:
      image.crop(0.0, trim_y, 1.0, 1 - trim_y)
  else:
    # resize to height, then crop to width
    image.resize(height=height)
    image.execute_transforms()
    trim_x = (float(image.width - width) / 2) / image.width
    if halign == 'left':
      image.crop(0.0, 0.0, 1 - (2 * trim_x), 1.0)
    elif halign == 'right':
      image.crop((2 * trim_x), 0.0, 1.0, 1.0)
    else:
      image.crop(trim_x, 0.0, 1 - trim_x, 1.0)

  return image.execute_transforms()


def fetch_image(url):
    """
    Method to import and item from a remote source and put it into blobstore
    """
    from google.appengine.ext import blobstore
    from django import http
    from google.appengine.api import files, urlfetch
    from django.core import urlresolvers

    rpc = urlfetch.create_rpc()
    urlfetch.make_fetch_call(rpc, url)

    result = rpc.get_result()
    if result.status_code == 200:
        file_data = result.content
        content_type = result.headers.get('content-type', None)

        # Create the file
        file_name = files.blobstore.create(mime_type=content_type)        


        with files.open(file_name, 'a') as f:
            f.write(file_data)

        # Finalize the file. Do this before attempting to read it.
        files.finalize(file_name)

        # Get the file's blob key
        blob_key = files.blobstore.get_blob_key(file_name)

        return blob_key


'''
def send_blob(request, blob_key_or_info, content_type=None, save_as=None):
    """Send a blob-response based on a blob_key.

    Sets the correct response header for serving a blob.  If BlobInfo
    is provided and no content_type specified, will set request content type
    to BlobInfo's content type.

    Args:
      blob_key_or_info: BlobKey or BlobInfo record to serve.
      content_type: Content-type to override when known.
      save_as: If True, and BlobInfo record is provided, use BlobInfos
        filename to save-as.  If string is provided, use string as filename.
        If None or False, do not send as attachment.

      Raises:
        ValueError on invalid save_as parameter.
    """

    CONTENT_DISPOSITION_FORMAT = 'attachment; filename="%s"'
    if isinstance(blob_key_or_info, blobstore.BlobInfo):
      blob_key = blob_key_or_info.key()
      blob_info = blob_key_or_info
    else:
      blob_key = blob_key_or_info
      blob_info = None

    #logging.debug(blob_info)
    response = HttpResponse()
    response[blobstore.BLOB_KEY_HEADER] = str(blob_key)

    if content_type:
      if isinstance(content_type, unicode):
        content_type = content_type.encode('utf-8')
      response['Content-Type'] = content_type
    else:
      del response['Content-Type']

    def send_attachment(filename):
      if isinstance(filename, unicode):
        filename = filename.encode('utf-8')
      response['Content-Disposition'] = (CONTENT_DISPOSITION_FORMAT % filename)

    if save_as:
      if isinstance(save_as, basestring):
        send_attachment(save_as)
      elif blob_info and save_as is True:
        send_attachment(blob_info.filename)
      else:
        if not blob_info:
          raise ValueError('Expected BlobInfo value for blob_key_or_info.')
        else:
          raise ValueError('Unexpected value for save_as')

    return response
'''
