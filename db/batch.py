from py2neo import Graph
from py2neo import Node, Relationship
from py2neo.cypher import CreateStatement


class QueryBuilder(object):
    baseq = """MERGE ({id}:{label} {props}) RETURN {id}"""

    def __init__(self):
        self.dct = {}
        self.ids = 0
        self.query = ""

    def merge_one(self, node):
        self.ids += 1
        nodeid = self.ids
        self.dct[node] = id
        kwargs = {
            "id": nodeid,
            "label" = 
        }
        self.query += type(self).baseq.format(

    def


def merge_statement(query, node):
    query += "MERGE "
    global dct
        query += "({0}:Person {{name:{1}, age:{2}}}), ".format(id, node.properties["name"], node.properties["age"])
        dct[node] = id
    return query, dct


def merge_one(node):
    global dct
    global counter
    

def return_statement(query, *args):
    query += "RETURN "
    query += ", ".join(args)
    return query

graph = Graph()

tx = graph.cypher.begin()



nodes = (Node("Person", name="Sally", age=22), Node("Person", name="Tom", age=22))

query, dct = merge_statement("", nodes)
query = return_statement(query, *[dct[node] for node in nodes])

tx.append(query)
print(tx.commit())

    



# n = 
# r = Relationship(
# statement.create(n)
# print(statement.string)

# res = statement.execute()

# print(res)





# results = g.cypher.execute("MATCH (n) RETURN n")
# print(results)



