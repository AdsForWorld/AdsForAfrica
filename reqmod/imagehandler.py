#https://medium.com/@tatianatylosky/uploading-files-with-python-using-digital-ocean-spaces-58c9a57eb05b
from boto3 import session
from botocore.client import Config

ACCESS_ID = 'DO801DYZCT6T8AJPN7PP'
SECRET_KEY = "heEV9Lozh6T7HXkC7OOgLSfuyRC5PuWXiWGes/Wjk4Q"
session = session.Session()
#start session
def startsession():
    client = session.client('s3',
                            region_name='sfo3',
                            endpoint_url='https://adsforafrica.sfo3.digitaloceanspaces.com',
                            aws_access_key_id=ACCESS_ID,
                            aws_secret_access_key=SECRET_KEY)
    return client
def uploadfile(client, filename, bucket, path):
    client.upload_file(filename, bucket, path)

def suploadfile(client, filename, bucket, path):
    """stream the file upload"""
    client.upload_fileobj(filename, bucket, path, ExtraArgs={'ACL': 'public-read'})
#upload
#client.upload_file('filename', 'hello-spaces', 'new-folder/new_file_name.html')
if __name__ == '__main__':
    client = startsession()
    client.upload_file('cat.png', 'ad-images', '3/cat.png')
#https://adsforafrica.sfo3.cdn.digitaloceanspaces.com/{path}
#https://adsforafrica.sfo3.cdn.digitaloceanspaces.com/ad-images/11805/te.html