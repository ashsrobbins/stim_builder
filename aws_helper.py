import boto3
import boto3.session
import braingeneers


# endpoint 'https://s3-west.nrp-nautilus.io'

def save_to_s3(filename, text):
    '''Saves text to s3 bucket in s3://braingeneers/asrobbin/patterns/[filename]'''
    key = 'asrobbin/patterns/' + filename
    sess = boto3.session.Session(profile_name='default')
    s3 = sess.resource('s3', endpoint_url=braingeneers.get_default_endpoint())

    # If object already exists, return false
    try:
        s3.Object('braingeneersdev', key).load()
        print('Object already exists')
        return False
    except:
        pass


    s3.Bucket('braingeneersdev').put_object(Key=key, Body=text)

    print('Saved to s3://' + key)
    return True


if __name__ == '__main__':
    filename = 'test2.txt'
    text = 'Hello World!'
    
    # Print whether or not the file was saved
    print(save_to_s3(filename, text))