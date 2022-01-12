from collections import defaultdict
# import json
# from json import JSONEncoder
# import jsonpickle

# Jens Luebeck (jluebeck [a] ucsd.edu]

# # required to help serialize the data for the web app
# class WordleDataEncoder(JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, WordleData):
#             return obj.to_json()
#
#         return json.JSONEncoder.default(self, obj)

# class to store various feedback and data
class WordleData:
    def __init__(self, poss_ans, to_check, k=5, cbw="SOARE"):
        self.k = k
        self.cbw = cbw
        self.poss_ans = poss_ans
        self.to_check = to_check
        self.bad_letters = set()
        self.unpos_req_letters = defaultdict(set)
        self.pos_letters = dict()
        self.lower_counts = defaultdict(int)
        self.upper_counts = defaultdict(int)
        self.gnum = 1

    def reset(self, poss_ans, to_check, k=5, cbw="SOARE"):
        self.__init__(poss_ans, to_check, k=k, cbw=cbw)

    # def to_json(self):
    #     return jsonpickle.encode(self)
    # #
    # def toJSON(self):
    #     return json.dumps(self, default=lambda o: o.__dict__)
