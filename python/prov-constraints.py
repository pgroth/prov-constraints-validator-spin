import rdflib
from rdflib_sparql.processor import prepareQuery
from rdflib_sparql.processor import processUpdate



#Testing queries
qMakeCycle = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT DATA {
        c:start c:precedes c:two .
        c:two   c:precedes c:three .
        c:three c:strictlyPrecedes c:start .
    }
'''


#Check cycles
qCheckCycle = '''
PREFIX prov: <http://www.w3.org/ns/prov#> 
PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>

select ?x where { ?x (c:precedes|c:strictlyPrecedes+)/c:strictlyPrecedes ?x .}

'''

#Expansion sparql based on event ordering constraints 

## Activity Ordering Constraint Insert

start_precedes_end = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?start c:precedes ?end . 
    }
    where {
        ?act a prov:Activity .
        ?act prov:qualifiedEnd ?end .
        ?act prov:qualifiedStart ?start .
    } 
'''

start_start_ordering = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?start1 c:precedes ?start2 . 
    }
    where {
        ?act a prov:Activity .
        ?act prov:qualifiedStart ?start1 .
        ?act prov:qualifiedStart ?start2 .
    } 

'''

end_end_ordering = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?end1 c:precedes ?end2 . 
    }
    where {
        ?act a prov:Activity .
        ?act prov:qualifiedEnd ?end1 .
        ?act prov:qualifiedEnd ?end2 .
    } 

'''

usage_within_activity1 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?start c:precedes ?use . 
    }
    where {
        ?act a prov:Activity .
        ?act prov:qualifiedStart ?start .
        ?act prov:qualifiedUsage ?use .
    } 

'''

usage_within_activity2 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?use c:precedes ?end . 
    }
    where {
        ?act a prov:Activity .
        ?act prov:qualifiedEnd ?end .
        ?act prov:qualifiedUsage ?use .
    } 

'''

generation_within_activity1 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?start c:precedes ?gen . 
    }
    where {
        ?act a prov:Activity .
        ?act prov:qualifiedStart ?start .
        ?act prov:qualifiedGeneration ?gen .
    } 

'''

generation_within_activity2 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?gen c:precedes ?end . 
    }
    where {
        ?act a prov:Activity .
        ?act prov:qualifiedEnd ?end .
        ?act prov:qualifiedGeneration ?gen .
    } 

'''

wasInformedBy_ordering = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?start c:precedes ?end . 
    }
    where {
        ?act1 prov:qualifiedCommunication ?com.
        ?com prov:activity ?act2.
        ?act1 a prov:Activity .
        ?act2 a prov:Activity .        
        ?act1 prov:qualifiedStart ?start .
        ?act2 prov:qualifiedEnd ?end .
    } 
'''

## Entity Ordering Constraint Insert

generation_precedes_invalidation = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?gen c:precedes ?inv . 
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedGeneration ?gen .
        ?e prov:qualifiedInvalidation ?inv .  
    } 
'''

generation_precedes_usage = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?gen c:precedes ?use . 
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedGeneration ?gen .
        ?e prov:qualifiedUsage ?use .
        
    } 
'''

usage_precedes_invalidation = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?use c:precedes ?inv . 
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedInvalidation ?inv .
        ?e prov:qualifiedUsage ?use .
        
    } 
'''

generation_generation_ordering = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?gen1 c:precedes ?gen2 . 
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedGeneration ?gen1 .
        ?e prov:qualifiedGeneration ?gen2 .
        
    } 
'''

invalidation_invalidation_ordering = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?inv1 c:precedes ?inv2 . 
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedInvalidation ?inv1 .
        ?e prov:qualifiedInvalidation ?inv2 .
        
    } 
'''

derivation_usage_generation_ordering = '''
    #e2 prov:wasDerivedFrom e1
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?use1 c:precedes ?gen2 . 
    }
    where {
        ?e1 a prov:Entity .
        ?e2 a prov:Entity .
        ?e2 prov:qualifiedDerivation ?d .
        ?d prov:entity ?e1 .
        ?d prov:hadGeneration ?gen2 .
        ?d prov:hadUsage ?use1 .
        ?use1 prov:entity ?e1 .
        ?e2 prov:qualifiedGeneration ?gen2 .
        
    } 
'''

derivation_generation_generation_ordering = '''
    #e2 prov:wasDerivedFrom e1
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?gen1 c:strictlyPrecedes ?gen2 . 
    }
    where {
        ?e1 a prov:Entity .
        ?e2 a prov:Entity .
        ?e2 prov:qualifiedDerivation ?d .
        ?d prov:entity ?e1 .
        ?e1 prov:qualifiedGeneration ?gen1 .
        ?e2 prov:qualifiedGeneration ?gen2 .
        
    } 
'''

wasStartedBy_ordering1 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?gen c:precedes ?start . 
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedGeneration ?gen1 .
        ?a prov:qualifiedStart ?start .
        ?start prov:entity ?e .
    } 
'''

wasStartedBy_ordering2 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?start c:precedes ?inv . 
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedInvalidation ?inv .
        ?a prov:qualifiedStart ?start .
        ?start prov:entity ?e .
    } 
'''

wasEndedBy_ordering1 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?gen c:precedes ?end . 
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedGeneration ?gen1 .
        ?a prov:qualifiedEnd ?end .
        ?end prov:entity ?e .
    } 
'''

wasEndedBy_ordering2 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?end c:precedes ?inv . 
    }
    where {
        ?e a prov:Entity .
        ?e prov:qualifiedInvalidation ?inv .
        ?a prov:qualifiedEnd ?end .
        ?end prov:entity ?e .
    } 
'''

specialization_generation_ordering = '''
    #e2 prov:specializationOf e1
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?gen1 c:strictlyPrecedes ?gen2 . 
    }
    where {
        ?e1 a prov:Entity .
        ?e2 a prov:Entity .
        ?e2 prov:specializationOf ?e1 .
        ?e1 prov:qualifiedGeneration ?gen1 .
        ?e2 prov:qualifiedGeneration ?gen2 .
        
    } 
'''

specialization_invalidation_ordering = '''
    #e1 prov:specializationOf e2
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
         ?inv1 c:strictlyPrecedes ?inv2 .
    }
    where {
        ?e1 a prov:Entity .
        ?e2 a prov:Entity .
        ?e1 prov:specializationOf ?e2 .
        ?e1 prov:qualifiedInvalidation ?inv1 .
        ?e2 prov:qualifiedInvalidation ?inv2 .
        
    } 
'''

def orderingConstraints(g):
    processUpdate(g, start_precedes_end)
    processUpdate(g, start_start_ordering)
    processUpdate(g, end_end_ordering)
    processUpdate(g, usage_within_activity1)
    processUpdate(g, usage_within_activity2)
    processUpdate(g, generation_within_activity1)
    processUpdate(g, generation_within_activity2)
    processUpdate(g, wasInformedBy_ordering)
    processUpdate(g, generation_precedes_invalidation)
    processUpdate(g, generation_precedes_usage)
    processUpdate(g, usage_precedes_invalidation)
    processUpdate(g, generation_generation_ordering)
    processUpdate(g, invalidation_invalidation_ordering)
    processUpdate(g, derivation_usage_generation_ordering)
    processUpdate(g, derivation_generation_generation_ordering)
    processUpdate(g, wasStartedBy_ordering1)
    processUpdate(g, wasStartedBy_ordering2)
    processUpdate(g, wasEndedBy_ordering1)
    processUpdate(g, wasEndedBy_ordering2)
    processUpdate(g, specialization_generation_ordering)
    processUpdate(g,specialization_invalidation_ordering)
    return g


def checkCycle (g):
    bindings = g.query(qCheckCycle)
    if len(bindings) > 0:
        #print g.serialize(format='turtle')
        return "fail"
    else:
        return "true"


def validate(filename):
    g = rdflib.Graph()
    g.parse(filename, format='turtle')
    #print g.serialize(format='turtle')
    g = orderingConstraints(g)
    print filename + ' ' + checkCycle(g)
    #print g.serialize(format='turtle')

def testCycleDetection():
    g = rdflib.Graph()
    processUpdate(g, qMakeCycle)
    print checkCycle(g)

testCycleDetection()

validate('./constraints/ordering-activity1-PASS-c30.ttl')
validate('./constraints/ordering-activity2-PASS-c33.ttl')
validate('./constraints/ordering-activity3-PASS-c34.ttl')
validate('./constraints/ordering-activity4-PASS-c31.ttl')
validate('./constraints/ordering-activity5-PASS-c32.ttl')
validate('./constraints/ordering-communication-PASS-c35.ttl')
validate('./constraints/ordering-entity1-PASS-c36-c37-c38.ttl')
validate('./constraints/ordering-entity2-PASS-c36.ttl')
validate('./constraints/ordering-entity3-PASS-c39.ttl')
validate('./constraints/ordering-entity4-PASS-c40.ttl')
validate('./constraints/ordering-derivation3-PASS-c41-c42.ttl')
validate('./constraints/ordering-derivation1-PASS-c42.ttl')
validate('./constraints/ordering-derivation2-FAIL-c42.ttl')
validate('./constraints/ordering-starts1-PASS-c43.ttl')
validate('./constraints/ordering-ends1-PASS-c44.ttl')
validate('./constraints/ordering-specialization1-PASS-c45.ttl')
validate('./constraints/ordering-specialization2-PASS-c46.ttl')
validate('./constraints/ordering-specialization3-PASS-c42-c45.ttl')
validate('./constraints/ordering-specialization4-FAIL-c42-c45.ttl')






    
    

