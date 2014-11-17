__Note Have a look at https://github.com/pgroth/prov-check__ I switched implementations to just use SPARQL with a small driver program.


prov-constraints-validator-spin
===============================

An implementation of [PROV-Constraints](http://www.w3.org/TR/prov-constraints/) using [SPARQL Inference Notation (SPIN)](http://spinrdf.org).

You can find the actual inferences and constraints in the prov-rules directory. These are expressed in SPARQL following the SPIN style. 

They are organized by whether they are inference or a constraint and what kind of provenance construct they apply to. 
They are named following the convention of the PROV-Constraints document.

* example.ttl - is an example file that causes both inferences and constraints to be started
* nl.vu.krr.CheckConstraints - actually runs the rules in prov-rules against a given input file

TODO
--------
* Implement all rules
* Create a bundled executable 
* Create a service
