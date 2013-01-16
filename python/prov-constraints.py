import rdflib
import os
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

select ?x where { ?x (c:precedes+|c:strictlyPrecedes+)/c:strictlyPrecedes ?x .}

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

## Agent Ordering Constraints

wasAssociatedWith_ordering1 = '''
    #agent as entity
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
        ?start c:precedes ?inv .
    }
    where {
        ?ag a prov:Agent .
        ?act a prov:Activity .
        ?act prov:qualifiedAssociation ?assoc .
        ?assoc prov:agent ?ag .
        ?act prov:qualifiedStart ?start .
        ?ag prov:qualifiedInvalidation ?inv .
            
    } 
'''

wasAssociatedWith_ordering2 = '''
    #agent as entity
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
        ?gen c:precedes ?end .
    }
    where {
        ?ag a prov:Agent .
        ?act a prov:Activity .
        ?act prov:qualifiedAssociation ?assoc .
        ?assoc prov:agent ?ag .
        ?ag prov:qualifiedGeneration ?gen .
        ?act prov:qualifiedEnd ?end .
        
    } 
'''

wasAssociatedWith_ordering3 = '''
    # agent as an activity
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
        ?start c:precedes ?end .
    }
    where {
        ?ag a prov:Agent . 
        ?act a prov:Activity .
        ?act prov:qualifiedAssociation ?assoc .
        ?assoc prov:agent ?ag .
        ?act prov:qualifiedStart ?start .
        ?ag prov:qualifiedEnd ?end .
        
    } 
'''

wasAssociatedWith_ordering4 = '''
    #activity as agent
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
        ?start c:precedes ?end .
    }
    where {
        ?ag a prov:Agent .
        ?act a prov:Activity .
        ?act prov:qualifiedAssociation ?assoc .
        ?assoc prov:agent ?ag .
        ?ag prov:qualifiedStart ?start .
        ?act prov:qualifiedEnd ?end .
        
    } 
'''

wasAttributedTo_ordering1 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
       ?gen1 c:precedes ?gen2 .
    }
    where {
        ?ag a prov:Agent .
        ?e a prov:Entity .
        ?e prov:qualifiedAttribution ?attr .
        ?attr prov:agent ?ag .
        ?ag prov:qualifiedGeneration ?gen1 .
        ?e prov:qualifiedGeneration ?gen2 .      
    } 
'''

wasAttributedTo_ordering2 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
       ?start c:precedes ?gen .
    }
    where {
        ?ag a prov:Agent .
        ?e a prov:Entity .
        ?e prov:qualifiedAttribution ?attr .
        ?attr prov:agent ?ag .
        ?ag prov:qualifiedStart ?start .
        ?e prov:qualifiedGeneration ?gen .
    } 
'''

actedOnBehalfOf_ordering1 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
       ?gen c:precedes ?inv .
    }
    where {
        ?ag1 a prov:Agent .
        ?ag2 a prov:Agent .
        ?ag2 prov:qualifiedDelegation ?del .
        ?del prov:agent ?ag1 .
        ?ag1 prov:qualifiedGeneration ?gen .
        ?ag2 prov:qualifiedInvalidation ?inv .
    } 
'''

actedOnBehalfOf_ordering2 = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    INSERT {
       ?start c:precedes ?end .
    }
    where {
        ?ag1 a prov:Agent .
        ?ag2 a prov:Agent .
        ?ag2 prov:qualifiedDelegation ?del .
        ?del prov:agent ?ag1 .
        ?ag1 prov:qualifiedStart ?start .
        ?ag2 prov:qualifiedEnd ?end .
    } 
'''

### Uniqueness Constraints

unique_generation = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    select ?e where {
        ?e prov:qualifiedGeneration ?gen1 .
        ?gen1 prov:activity ?act .
        ?e prov:qualifiedGeneration ?gen2 .
        ?gen2 prov:activity ?act .    
        FILTER (?gen1 != ?gen2)
    }
'''

unique_invalidation = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    select ?e where {
        ?e prov:qualifiedInvalidation ?inv1 .
        ?gen1 prov:activity ?act .
        ?e prov:qualifiedInvalidation ?inv2 .
        ?gen2 prov:activity ?act .    
        FILTER (?inv1 != ?inv2)
    }
'''

unique_wasStartedBy = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    select ?a where {
        ?a prov:qualifiedStart ?start1 .
        ?a prov:qualifiedStart ?start2 .
        ?a prov:wasStartedBy ?a2.
        FILTER (?start1 != ?start2)
    }
'''

unique_wasEndedBy = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    select ?a where {
        ?a prov:qualifiedEnd ?end1 .
        ?a prov:qualifiedEnd ?end2 .
        ?a prov:wasEndedBy ?a2 .
        FILTER (?end1 != ?end2)
    }
'''

unique_startTime = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    select ?a where {
        ?a prov:qualifiedStart ?start .
        ?start prov:atTime ?t1 .
        ?a prov:startedAtTime ?t2 .
        FILTER (?t1 != ?t2)
    }
'''

unique_endTime = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    select ?a where {
        ?a prov:qualifiedEnd ?end .
        ?end prov:atTime ?t1 .
        ?a prov:endedAtTime ?t2 .
        FILTER (?t1 != ?t2)
    }
'''

##Impossibility Constraints

impossible_unspecified_derivation_generation_use = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    select ?d where {
        { ?d a prov:Derivation .
        ?d prov:hadGeneration ?g .
        FILTER NOT EXISTS { ?d prov:hadActivity ?a . }
        } 
        UNION {
        ?d a prov:Derivation .
        ?d prov:hadUsage ?u .
        FILTER NOT EXISTS { ?d prov:hadActivity ?a . }
        }
        UNION {
        ?d a prov:Derivation .
        ?d prov:hadUsage ?u .
        ?d prov:hadGeneration ?g .
        FILTER NOT EXISTS { ?d prov:hadActivity ?a . }
        }       
    }
'''

impossible_specializaton_reflexive = '''
 PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    select ?e where {
        ?e prov:specializationOf ?e .
    }
'''

impossible_property_overlap = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    select ?x where {
        ?x a ?class1 .
        ?x a ?class2 .
        FILTER ( ?class1 != ?class2 &&
                ?class1 IN (prov:Usage,
                            prov:Generation, 
                            prov:Invalidation, 
                            prov:Start,
                            prov:End,
                            prov:Communication,
                            prov:Attribution,
                            prov:Association,
                            prov:Delegation,
                            prov:Derivation) &&
                ?class2 IN (prov:Usage,
                            prov:Generation, 
                            prov:Invalidation, 
                            prov:Start,
                            prov:End,
                            prov:Communication,
                            prov:Attribution,
                            prov:Association,
                            prov:Delegation,
                            prov:Derivation) )
        
    }
'''

impossible_object_property_overlap = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    select ?x where {
        ?x a ?class1 .
        ?x a ?class2 .
        FILTER ( ?class1 != ?class2 &&
                ?class1 IN (prov:Entity, prov:Activity, prov:Agent) &&
                ?class2 IN (prov:Usage,
                            prov:Generation, 
                            prov:Invalidation, 
                            prov:Start,
                            prov:End,
                            prov:Communication,
                            prov:Attribution,
                            prov:Association,
                            prov:Delegation,
                            prov:Derivation) )
        
    }
'''

entity_activity_disjoint = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    select ?e where {
        ?e a prov:Entity, prov:Activity .
    }
'''

membership_empty_collection = '''
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX c: <http://www.few.vu.nl/pgroth/provconstraints#>
    
    select ?c where {
        ?c prov:hadMember ?m .
        ?c a prov:EmptyCollection .
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
    processUpdate(g, specialization_invalidation_ordering)
    processUpdate(g, wasAssociatedWith_ordering1)
    processUpdate(g, wasAssociatedWith_ordering2)
    processUpdate(g, wasAssociatedWith_ordering3)
    processUpdate(g, wasAssociatedWith_ordering4)
    processUpdate(g, wasAttributedTo_ordering1)
    processUpdate(g, wasAttributedTo_ordering2)
    processUpdate(g, actedOnBehalfOf_ordering1)
    processUpdate(g, actedOnBehalfOf_ordering2)
    return g

def checkUniqueness (g):
    queries = [unique_generation, 
               unique_invalidation, 
               unique_wasStartedBy,
               unique_wasEndedBy,
               unique_startTime,
               unique_endTime]
    for q in queries:
        if not check(g,q) : 
            #print q
            print 'uniqueness'
            return False
        
    return True
    
def checkImpossibility (g):
    queries = [impossible_unspecified_derivation_generation_use,
               impossible_specializaton_reflexive,
               impossible_property_overlap,
               impossible_object_property_overlap,
               entity_activity_disjoint,
               membership_empty_collection]
    for q in queries:
        if not check(g,q) : 
            print 'impossibility'
            return False
        
    return True
    
    
def check(g, q):
    bindings = g.query(q)
    if len(bindings) > 0:
        return False
    else:
        return True

def checkCycle (g):
    g1 = orderingConstraints(g)
    res = check(g1, qCheckCycle)
    if not res :
        print 'cycle'
    return res


def validate(filename):
    g = rdflib.Graph()
    g.parse(filename, format='turtle')
    #print g.serialize(format='turtle')

    result = checkCycle(g) and checkUniqueness(g) and checkImpossibility(g)
    print filename + ' ' + str(result)
    if result == True :
        return 'PASS'
    else :
        return 'FAIL'

    
    #print g.serialize(format='turtle')

def testCycleDetection():
    g = rdflib.Graph()
    processUpdate(g, qMakeCycle)
    print g.serialize(format='turtle')
    print checkCycle(g)

def testAllConstraints():
    dir = os.listdir('./constraints/')
    notcorrect = 0
    for f in dir:
        if f.endswith('.ttl'):
            res = validate('./constraints/' + f)
            if not (res in f):
                print "Not correct"
                notcorrect = notcorrect + 1
    print notcorrect
                
                
    

testCycleDetection()
testAllConstraints()
#validate('./constraints/ordering-entity4-PASS-c40.ttl')




# validate('./constraints/ordering-activity1-PASS-c30.ttl')
# validate('./constraints/ordering-activity2-PASS-c33.ttl')
# validate('./constraints/ordering-activity3-PASS-c34.ttl')
#validate('./constraints/ordering-activity4-PASS-c31.ttl')
# validate('./constraints/ordering-activity5-PASS-c32.ttl')
# validate('./constraints/ordering-communication-PASS-c35.ttl')
# validate('./constraints/ordering-entity1-PASS-c36-c37-c38.ttl')
# validate('./constraints/ordering-entity2-PASS-c36.ttl')
# validate('./constraints/ordering-entity3-PASS-c39.ttl')
# validate('./constraints/ordering-entity4-PASS-c40.ttl')
# validate('./constraints/ordering-derivation1-PASS-c42.ttl')
# validate('./constraints/ordering-derivation2-FAIL-c42.ttl')
# validate('./constraints/ordering-derivation3-PASS-c41-c42.ttl')
# validate('./constraints/ordering-starts1-PASS-c43.ttl')
# validate('./constraints/ordering-ends1-PASS-c44.ttl')
# validate('./constraints/ordering-specialization1-PASS-c45.ttl')
# validate('./constraints/ordering-specialization2-PASS-c46.ttl')
# validate('./constraints/ordering-specialization3-PASS-c42-c45.ttl')
# validate('./constraints/ordering-specialization4-FAIL-c42-c45.ttl')
# validate('./constraints/ordering-association1-PASS-c47.ttl')
# validate('./constraints/ordering-association2-PASS-c47.ttl')
# validate('./constraints/ordering-attribution1-PASS-c48.ttl')
# validate('./constraints/ordering-attribution2-PASS-c48.ttl')
# validate('./constraints/ordering-delegation1-PASS-c49.ttl')
# validate('./constraints/ordering-delegation2-PASS-c49.ttl')
# validate('./constraints/unification-generation-f1-FAIL-c24.ttl')
# validate('./constraints/unification-generation-s3-PASS-c24.ttl')
# validate('./constraints/unification-invalidation-f1-FAIL-c25.ttl')
# validate('./constraints/unification-invalidation-s3-PASS-c25.ttl')
# validate('./constraints/unification-start-f4-FAIL-c26.ttl')
# validate('./constraints/unification-start-s1-PASS-c26.ttl')
# validate('./constraints/unification-start-s2-PASS-c26.ttl')
# validate('./constraints/unification-start-s3-PASS-c26.ttl')
# validate('./constraints/unification-start-s4-PASS-c26.ttl')
# validate('./constraints/unification-end-f4-FAIL-c27.ttl')
# validate('./constraints/unification-end-s1-PASS-c27.ttl')
# validate('./constraints/unification-end-s2-PASS-c27.ttl')
# validate('./constraints/unification-end-s3-PASS-c27.ttl')
# validate('./constraints/unification-end-s4-PASS-c27.ttl')
# validate('./constraints/unification-activity-end-f1-FAIL-c29.ttl')
# validate('./constraints/unification-activity-end-s1-PASS-c29.ttl')
# validate('./constraints/unification-activity-start-f1-FAIL-c28.ttl')
# validate('./constraints/unification-activity-start-s1-PASS-c28.ttl')
# validate('./constraints/prov-o-property-hadGeneration-FAIL-c51-DM.ttl')
# validate('./constraints/prov-o-property-hadUsage-FAIL-c51-DM.ttl')
# validate('./constraints/unification-specialization-f3-FAIL-c52.ttl')
# validate('./constraints/unification-specialization-f4-FAIL-c52.ttl')
# validate('./constraints/type-f4-FAIL-c53.ttl')
# validate('./constraints/type-f3-FAIL-c54.ttl')
# validate('./constraints/type-s1-PASS-c50-c55.ttl')
# validate('./constraints/type-s2-PASS-c50-c55.ttl')
# validate('./constraints/type-f1-FAIL-c50-c55.ttl')
# validate('./constraints/type-f2-FAIL-c50-c55.ttl')
# validate('./constraints/type-collection-FAIL-c56.ttl')

    
    

