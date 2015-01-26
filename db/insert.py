from py2neo.cypher import CypherTransaction


class QueryMeta(type):

    def __init__(cls, name, bases, dct):
        base_query = '%s ({id}:{label} {repr})'
        cls.base_query = base_query
        query_types = ['MATCH', 'MERGE', 'CREATE']
    
        for q_type in query_types:
            setattr(cls, q_type, base_query % (q_type,))
        
        cls.CREATE_CONSTRAINT_ON = 'CREATE CONSTRAINT ON ({id}:{label}) ASSERT {id}.{prop} IS UNIQUE'
        cls.CREATE_INDEX_ON  = 'CREATE INDEX ON :{label}({prop})'
        return super(QueryMeta, cls).__init__(name, bases, dct)
        

class Query(object, metaclass = QueryMeta):


    def __init__(self, graph, *args, **kwargs):
        self.id = 0
        self.dct = {}
        self.query = []
        self.graph = graph
        
    def base_statement(self, s, obj):
        statement_id = "n" + str(self.id)
        self.dct[obj.name] = statement_id
        params = {
            'id': statement_id,
            'label': obj.label,
            'repr': str(obj)
        }
        q = s.format(**params)
        self.query.append(q)
        self.id += 1


    def execute(self):
        return self.graph.cypher.execute("\n".join(self.query))


# Apparently adding a uniqueness constraint creates indexes anyway
# I'll keep this around for now
class IndexQuery(Query):

    def add_indexes_and_execute(self, indexes):
        
        for dct in indexes:
            if not (('label' in dct) and ('prop' in dct)):
                raise ValueError("label and prop are both needed (IndexQuery)")
            self.graph.cypher.execute(self.CREATE_INDEX_ON.format(**dct))


class UniquenessConstraintQuery(Query):

    def add_constraints_and_execute(self, constraints):
        for dct in constraints:
            cid = "n" + str(self.id)
            if not (('label' in dct) and ('prop' in dct)):
                raise ValueError("label and prop are both needed (UniquenessConstraintQuery)")
            dct['id'] = cid
            self.graph.cypher.execute(self.CREATE_CONSTRAINT_ON.format(**dct))
            self.id += 1


class InsertQuery(Query):

    def match_statement(self, obj):
        return self.base_statement(self.MATCH, obj)

    def merge_statement(self, obj):
        return self.base_statement(self.MERGE, obj)


        



