

class MoleproEdgeModel():
    ''' class to encapsulate the web query object values '''
    def __init__(self, edge_key, source_key, target_key, source_id, target_id, edge_type, source_type, target_type, target_constraints, edge_constraints, transformer_chain_list):
        self.edge_key = edge_key
        self.source_key = source_key
        self.target_key = target_key 
        self.source_id = source_id
        self.target_id = target_id
        self.target_constraints = target_constraints if target_constraints is not None else []
        self.edge_constraints = edge_constraints if edge_constraints is not None else []
        self.edge_type = edge_type
        self.source_type = source_type
        self.target_type = target_type 
        self.transformer_chain_list = transformer_chain_list

    def __str__(self):
        return "edge: {}[{}], source: {}-{}, target: {}-{}[{}]".format(self.edge_type, len(self.edge_constraints), self.source_id, self.source_type, self.target_id, self.target_type, len(self.target_constraints))

    __repr__ = __str__
        
    def __eq__(self, other): 
        if not isinstance(other, MoleproEdgeModel):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.edge_key == other.edge_key and self.source_key == other.source_key and self.target_key == other.target_key \
            and self.edge_type == other.edge_type and self.source_type == other.source_type and self.target_type == other.target_type


