import falcon
import json
import hashlib
import sys
from urlparse import urlparse
from bson import ObjectId
from bson.json_util import dumps
from bson import json_util
from datetime import datetime

import subprocess
import multiprocessing

class thugLive:
    def worker(a, analise):
        try:
            res = subprocess.Popen(['python','/home/thug/src/thug.py', '-Fq', analise], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            output, error = res.communicate()

            if output:
                return {'message': 'Analysis In Progress', 'output': str(output)}
            if error:
                return {'message': 'Warning', 'output': str(error.strip()), 'returncode': str(res.returncode)}
        except OSError as e:
            return {'message': 'Error', 'errno': str(e.errno), 'strerror': str(e.strerror), 'filename': str(e.filename)}
        except:
            return {'message': 'Error', 'message': str(sys.exc_info()[0])}

        return True

class ComplexEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class defaultResource:
    def on_get(self, req, resp):
        resp.data = json.dumps({'message': 'Api Thug Ready!'})
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_200

class vtSendResource:

    def on_post(self, req, resp):
         try:
             raw_json = req.stream.read()
         except Exception as ex:
             raise falcon.HTTPError(falcon.HTTP_400,'Error',ex.message)

         try:
            result = json.loads(raw_json, encoding='utf-8')
            analise = result['url']
            response = {'message': 'Analysis In Progress'}

            try:
                p = multiprocessing.Process(target=thugLive().worker, args=(analise, ))
                p.start()
            except:
                response = {'message': 'Error', 'message': str(sys.exc_info()[0])}

            resp.data = json.dumps(response)
            resp.content_type = 'application/json'
            resp.status = falcon.HTTP_200

         except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,'Invalid JSON','Could not decode the request body. The JSON was incorrect.')

class vtReportResource:
    def on_post(self, req, resp):
         try:
             raw_json = req.stream.read()
         except Exception as ex:
             raise falcon.HTTPError(falcon.HTTP_400,'Error',ex.message)

         try:
            result = json.loads(raw_json, encoding='utf-8')

            import pymongo

            status = False
            sample_path = False
            dirPath = False
            data = {}
            analyses = {}
            graphs = {}
            behaviors = []

            con = pymongo.MongoClient("api_thug_mongo", 27017)
            db = con.thug
            url = result['url']
            originUrl = url
            parserUrl = urlparse(url)

            if not parserUrl.scheme:
                url = 'http://' + url

            infoUrl = db.urls.find_one({'url' : url})
            if infoUrl:
                status = True
                data = {
                        'url': infoUrl['url'],
                        'date': str(infoUrl['_id'].generation_time)
                    }

                infoAnalyses = db.analyses.find_one({'url_id' : infoUrl['_id']})
                if infoAnalyses:
                    analyses = {
                        'id': str(infoAnalyses['_id']),
                        'thug': infoAnalyses['thug'],
                        'date': str(infoAnalyses['_id'].generation_time)
                    }
                    dirPath = datetime.strptime(str(infoAnalyses['_id'].generation_time), '%Y-%m-%d %H:%M:%S+00:00').strftime('%Y%m%d%H%M%S')
                    sample_path = str(hashlib.md5(originUrl).hexdigest()) + "/" + str(dirPath)

                infoBehaviors = db.behaviors.find({'analysis_id' : infoAnalyses['_id']})
                if infoBehaviors.count():
                    for beh in infoBehaviors:
                        behaviors.append({
                            'method': beh['method'],
                            'description': beh['description'],
                        })

                infoGraphs = db.graphs.find_one({'analysis_id' : infoAnalyses['_id']})
                if infoGraphs:
                    graphs = json.loads(infoGraphs['graph'])

                infoAnalyses = db.analyses.find_one({'url_id' : infoUrl['_id']})
                if infoAnalyses:
                    analyses = {
                        'id': str(infoAnalyses['_id']),
                        'thug': infoAnalyses['thug'],
                        'date': str(infoAnalyses['_id'].generation_time)
                    }
                data = {
                        'url': infoUrl['url'],
                        'url_id': str(infoUrl['_id']),
                        'sample_path': sample_path,
                        'date': str(infoUrl['_id'].generation_time),
                        'analyses': analyses,
                        'behaviors': behaviors,
                        'graphs': graphs
                    }

            resp.data = json.dumps({'status': status, 'data': data})
            resp.content_type = 'application/json'
            resp.status = falcon.HTTP_200

         except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,'Invalid JSON','Could not decode the request body. The JSON was incorrect.')


api = falcon.API()

vtSend = vtSendResource()
vtReport = vtReportResource()
df = defaultResource()

api.add_route('/', df)
api.add_route('/analise', vtSend)
api.add_route('/report', vtReport)