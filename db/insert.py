import itertools
from py2neo.cypher import CypherTransaction
from copy import copy


class QueryMeta(type):

    def __init__(cls, name, bases, dct):
        base_node_query = '%s ({id}:{label} {repr})'
        outgoing_relation_query = '%s ({a})-[{r}:{relation} {repr}]->({b})'
        # incoming_relation_query = '%s ({a})<-[{r}:{relation} {repr}]-({b})'
        cls.base_node_query = base_node_query
        query_types = ['MATCH', 'MERGE', 'CREATE']
        cls.node_queries = []
        cls.relation_queries = []
    
        for q_type in query_types:
            name = '{0}_NODE'.format(q_type)
            setattr(cls, name, base_node_query % (q_type,))
            cls.node_queries.append((name, getattr(cls, name)))
            name = '{0}_RELATION'.format(q_type)
            setattr(cls, name, outgoing_relation_query % (q_type,))
            cls.relation_queries.append((name, getattr(cls, name)))
            # do incoming (not sure if this is needed)
        
        cls.CREATE_CONSTRAINT_ON = 'CREATE CONSTRAINT ON ({id}:{label}) ASSERT {id}.{prop} IS UNIQUE'
        cls.CREATE_INDEX_ON  = 'CREATE INDEX ON :{label}({prop})'
        return super(QueryMeta, cls).__init__(name, bases, dct)
        

class Query(object, metaclass=QueryMeta):


    def __init__(self, graph, *args, **kwargs):
        # maybe make a factory function for ideas, refactor later
        self.id = itertools.count()
        self.dct = {}
        self.query = []
        self.graph = graph

    def get_id(self):
        return "n" + str(next(self.id))
        
        
    def base_node_statement(self, s, obj):
        statement_id = self.get_id()
        self.dct[obj.name] = statement_id
        params = {
            'id': statement_id,
            'label': obj.label,
            'repr': str(obj)
        }
        print(s)
        q = s.format(**params)
        self.query.append(q)

    def base_relation_statement(self, s, source, target, relation, attrs):
        rid = self.get_id()
        params = {
            'a': self.dct[source.name],
            'b': self.dct[target.name],
            'r': rid, # might be unnecessary
            'relation': relation,
            'repr': str(attrs) if attrs else "",
        }
        q = s.format(**params)
        self.query.append(q)

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
            cid = self.get_id()
            if not (('label' in dct) and ('prop' in dct)):
                raise ValueError("label and prop are both needed (UniquenessConstraintQuery)")
            dct['id'] = cid
            self.graph.cypher.execute(self.CREATE_CONSTRAINT_ON.format(**dct))


def add_query_functions(cls):
    def node_func_factory(name, query):
        def f(self, obj):
            return self.base_node_statement(query, obj)
        f.__name__ = name.lower()
        return f

    def relation_func_factory(name, query):
        def f(self, source, target, relation, attrs=None):
            return self.base_relation_statement(query, source, target, relation, attrs)
        f.__name__ = name.lower()
        return f
        
    for name, nq in cls.node_queries:
        f = node_func_factory(name, nq)
        setattr(cls, f.__name__, f)

    for name, nq in cls.relation_queries:
        g = relation_func_factory(name, nq)
        setattr(cls, g.__name__, g)

    return cls
    

@add_query_functions
class InsertQuery(Query):
    pass
