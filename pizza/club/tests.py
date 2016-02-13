from django.test import TestCase

import json

class BaseTestCase(TestCase):
    fixtures = ['testdb.json']
    def _createUser(self, params):
        response = self.client.post('/club/api/create/',json.dumps(params),
                                    content_type="application/json")
        return json.loads(response.content)

    def _loginUser(self, params):
        response = self.client.post('/club/api/login/',json.dumps(params),
                                    content_type="application/json")
        return json.loads(response.content)

# Create your tests here.
class TestUserView(BaseTestCase):

    def _getInfo(self):
        response = self.client.post('/club/api/info/',{},
                                    content_type="application/json")
        return json.loads(response.content)

    def test_infoUser(self):
        response = self._getInfo()
        self.assertEquals(response['login'],'Anonymous')

        createData = {'login':'test1',
                      'passwd':'pass1',
                      'email':'foo@bar.com'}
        response = self._createUser(createData)
        self.assertTrue(response['result'])
        response = self._loginUser(createData)
        self.assertTrue(response['result'])
        
        response = self._getInfo()
        self.assertEquals(response['login'],'test1')

    def test_createUser(self):
        response = self._createUser({'login':'test1',
                                     'email':'pass1'})
        self.assertFalse(response['result'])
        self.assertEquals(response['message'],
                          'Missing username, password or email')

        createData = {'login':'test1',
                      'passwd':'pass1',
                      'email':'foo@bar.com'}
        response = self._createUser(createData)
        self.assertTrue(response['result'])

        response = self._createUser(createData)
        self.assertFalse(response['result'])
        self.assertEquals(response['message'],'User already exists')

    def test_loginUser(self):
        response = self._loginUser({'email':'pass1'})
        self.assertFalse(response['result'])
        self.assertEquals(response['message'],
                          'Missing username or password')

        createData = {'login':'test1',
                      'passwd':'pass1',
                      'email':'foo@bar.com'}
        response = self._createUser(createData)
        self.assertTrue(response['result'])
        response = self._loginUser(createData)
        self.assertTrue(response['result'])

        response = self._loginUser({'login':'test1',
                                     'passwd':'pass2'})
        self.assertFalse(response['result'])
        self.assertEquals(response['message'],
                          'Invalid username or password')

class TestDataView(BaseTestCase):

    def _bootStrap(self):
        createData = {'login':'test1',
                      'passwd':'pass1',
                      'email':'foo@bar.com'}
        response = self._createUser(createData)
        self.assertTrue(response['result'])
        response = self._loginUser(createData)
        self.assertTrue(response['result'])

    def _getShopList(self):
        response = self.client.post('/club/api/list/',json.dumps({}),
                                     content_type="application/json")
        contents = json.loads(response.content)
        self.assertTrue(contents.get('pizzeria_list') is not None)
        ps = contents['pizzeria_list']

        ids = []
        for p in ps:
            self.assertTrue(p.get('url') is not None)
            self.assertTrue(p.get('name') is not None)
            self.assertTrue(p.get('id') is not None)
            ids.append(p['id'])

        return ids

    def test_getList(self):
        shopIds = self._getShopList()
        self.assertTrue(len(shopIds) == 2)

    def _getDetail(self, data):
        response = self.client.post('/club/api/detail/',
                                    json.dumps(data),
                                    content_type="application/json")
        return json.loads(response.content)

    def _verifyVoteData(self, voteDict, isPresent):
        # but, we don't have any votes, so the vote data shouldn't be there
        self.assertEquals(voteDict.has_key('crust'), isPresent)
        self.assertEquals(voteDict.has_key('sauce'), isPresent)
        self.assertEquals(voteDict.has_key('service'), isPresent)
        self.assertEquals(voteDict.has_key('creativity'), isPresent)
        self.assertEquals(voteDict.has_key('overall'), isPresent)

    def test_getDetail(self):
        firstShop = self._getShopList()[0]
        
        detail = self._getDetail({'id': firstShop})
        self.assertTrue(detail.get('pizzeria') is not None)
        visits = detail.get('visit_list')
        self.assertTrue(len(visits) > 0)
        self._verifyVoteData(visits[0],False)

    def _createVote(self, params):
        response = self.client.post('/club/api/vote/',json.dumps(params),
                                    content_type="application/json")
        return json.loads(response.content)

    def test_createVote(self):
        self._bootStrap()

        detail = self._getDetail({'id': self._getShopList()[0]})
        visit = detail.get('visit_list')[0]
        visitId = visit['id']

        vote = {'crust': 1.0,
                'sauce': 1.0,
                'service': 1.0,
                'creativity': 1.0,
                'overall': 1.0,
                'comment': 'greasy greasy love',
            }
        params = {'visit_id': visitId,
                  'vote': vote}
        response = self._createVote(params)
        self.assertTrue(response['result'])

        # Created the vote.  So, fetch again to see that we now have a vote.
        firstShop = self._getShopList()[0]
        detail = self._getDetail({'id': firstShop})
        visit = detail.get('visit_list')[0]
        self._verifyVoteData(visit,True)
