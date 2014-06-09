from flask import Flask, request, make_response
from flask.ext.cache import Cache
from flask_cors import cross_origin
from datetime import date, datetime, timedelta
import json
import boto
from boto.exception import S3ResponseError
import os
from operator import itemgetter
from itertools import groupby

app = Flask(__name__)
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True

AWS_KEY = os.environ['AWS_ACCESS_KEY']
AWS_SECRET = os.environ['AWS_SECRET_KEY']

# ROUTES
@app.route('/')
@cross_origin(methods=['GET'])
# @cache.cached(timeout=60*10) # cache for 10 min
def index():
    response = {
        'status':'OK',
        'message': 'List of all public buckets',
        'objects': []
    }
    status_code = 200
    conn = boto.connect_s3(aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET)
    buckets = conn.get_all_buckets()
    public_buckets = []
    for bucket in buckets:
        grants = bucket.list_grants()
        for grant in grants:
            if grant.permission == 'READ':
                public_buckets.append(bucket.name)
    response['objects'] = list(set(public_buckets))
    resp = make_response(json.dumps(response), status_code)
    resp.headers['Content-Type'] = 'application/json'
    return resp

@app.route('/<bucket_name>/')
@cross_origin(methods=['GET'])
def list_bucket(bucket_name):
    resp = {
        'status': 'OK',
        'message': 'Listing of keys within %s' % bucket_name,
        'objects': [],
        'meta': "Add a 'meta.json' file to the bucket to populate this key",
    }
    status_code = 200
    conn = boto.connect_s3(aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET)
    try:
        bucket = conn.get_bucket(bucket_name)
    except S3ResponseError:
        bucket = None
        resp['status'] = 'ERROR'
        resp['message'] = '%s is not a valid bucket name' % bucket_name
        status_code = 404
    if bucket is not None:
        grants = [g.permission for g in bucket.list_grants()]
        if 'READ' in grants:
            prefix = request.args.get('prefix')
            if prefix:
                bucket_list = bucket.list(prefix)
                resp['message'] = "%s with prefix '%s'" % (resp['message'], prefix)
            else:
                bucket_list = bucket.list()
            if bucket.get_key('meta.json'):
                meta = bucket.get_key('meta.json').get_contents_as_string()
                resp['meta'] = json.loads(meta)
            paths = [{'dir': os.path.split(k.key)[0], 'body': k} for k in bucket_list]
            paths = sorted(paths, key=itemgetter('dir'))
            structure = {'root': []}
            for k,g in groupby(paths, key=itemgetter('dir')):
                listing = [{
                    'name': i['body'].name.encode('utf-8'), 
                    'size': sizeof_fmt(i['body'].size),
                    'last_modified': format_datetime(i['body'].last_modified)} 
                    for i in list(g) if i['body'].size > 0]
                if not k:
                    structure['root'].extend(listing)
                elif structure.get(k):
                    structure[k].extend(listing)
                else:
                    structure[k] = listing
            resp['objects'] = structure
        else:
            resp['status'] = 'ERROR'
            resp['message'] = "'%s' is not a public bucket" % bucket_name
            status_code = 401
    resp = make_response(json.dumps(resp), status_code)
    resp.headers['Content-Type'] = 'application/json'
    return resp

def format_datetime(str):
    return datetime.strptime(str, "%Y-%m-%dT%H:%M:%S.000Z").strftime("%b %e, %Y %I:%M %p")

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

# INIT
if __name__ == "__main__":
    app.run(debug=True, port=9999)
