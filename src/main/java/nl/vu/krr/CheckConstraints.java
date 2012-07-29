package nl.vu.krr;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.Iterator;
import java.util.List;

import org.topbraid.spin.arq.ARQ2SPIN;
import org.topbraid.spin.arq.ARQFactory;
import org.topbraid.spin.constraints.ConstraintViolation;
import org.topbraid.spin.constraints.SPINConstraints;
import org.topbraid.spin.inference.SPINInferences;
import org.topbraid.spin.model.Construct;
import org.topbraid.spin.model.Function;
import org.topbraid.spin.model.Query;
import org.topbraid.spin.model.SPINFactory;
import org.topbraid.spin.model.Template;
import org.topbraid.spin.system.SPINModuleRegistry;
import org.topbraid.spin.vocabulary.SPIN;

import com.hp.hpl.jena.ontology.OntModel;
import com.hp.hpl.jena.ontology.OntModelSpec;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.shared.ReificationStyle;
import com.hp.hpl.jena.util.FileUtils;
import com.hp.hpl.jena.vocabulary.RDFS;

/**
 * A stand-alone constraint checker callable from the command line. modifications for prov
 * prov:wasDerivedFrom org.topbraid.spin.tools.CheckConstraints
 * 
 * @author Paul Groth
 */
public class CheckConstraints {

	
	private static String ACTIVITY_CONSTRAINTS_DIR = "prov-rules/constraints/activity/";
	private static String ENTITY_CONSTRAINTS_DIR = "prov-rules/constraints/entity/";
	
	private static String ACTIVITY_INFERENCE_DIR = "prov-rules/inference/activity/";
	private static String ENTITY_INFERENCE_DIR = "prov-rules/inference/entity/";
	
	/**
	 * The command line entry point.
	 * @param args 
	 * 		[0]: the base URI/physical URL of the file
	 * 		[1]: the name of a local RDF file contains the base URI (the file to check)
	 */
	public static void main(String[] args) throws Exception {
		
		// Initialize system functions and templates
		SPINModuleRegistry.get().init();
		
		String baseURI = args[0];
		Model baseModel = ModelFactory.createDefaultModel(ReificationStyle.Minimal);
		
		System.out.println("new base model");
		
		String fileName = args[1];
		File file = new File(fileName);
		InputStream is = new FileInputStream(file);
		String lang = FileUtils.guessLang(fileName);
		baseModel.read(is, baseURI, lang);
		
		baseModel  = CheckConstraints.addConstraints(baseModel);
		baseModel = CheckConstraints.addInferences(baseModel);
		
		System.out.println("Loaded all constraints and inferences");
		
		// Create OntModel with imports
		OntModel ontModel = ModelFactory.createOntologyModel(OntModelSpec.OWL_MEM, baseModel);

		System.out.println("Created the ontology model");
		
		//System.out.println(q.toString());
		SPINModuleRegistry.get().init();
		
		SPINModuleRegistry.get().registerAll(ontModel, null);
		
		Model newTriples = ModelFactory.createDefaultModel(ReificationStyle.Minimal);
		ontModel.addSubModel(newTriples);
		
	
		SPINInferences.run(ontModel, newTriples, null, null, true, null);
		System.out.println("Inferred triples: " + newTriples.size());
		
		newTriples.write(System.out, FileUtils.langTurtle);

		
		
		// Perform constraint checking
		List<ConstraintViolation> cvs = SPINConstraints.check(ontModel, null);
		System.out.println(cvs.size());
		
		// Create results model
		Model results = ModelFactory.createDefaultModel();
		results.setNsPrefix(SPIN.PREFIX, SPIN.NS);
		results.setNsPrefix("rdfs", RDFS.getURI());
		SPINConstraints.addConstraintViolationsRDF(cvs, results, false);

		// Output results in Turtle
		results.write(System.out, FileUtils.langTurtle);
	}
	
	public static Model addInferences(Model baseModel) throws Exception
	{
		File activity_rules_dir = new File(ACTIVITY_INFERENCE_DIR);
		
		File[] activity_rules = activity_rules_dir.listFiles();
		for (int i = 0; i < activity_rules.length; i++) {
			if (activity_rules[i].getName().endsWith(".txt")){
				FileInputStream fis = new FileInputStream(activity_rules[i]); 
				BufferedReader in = new BufferedReader(new InputStreamReader(fis, "UTF-8"));
				String queryStr = "";
				String line = "";
	
				while (( line = in.readLine()) != null) {
					queryStr = queryStr + line;
				}
				
				fis.close();
				
				Query q = ARQ2SPIN.parseQuery(queryStr, baseModel);
				
				baseModel.add(baseModel.getResource("http://www.w3.org/ns/prov#Activity"), 
						baseModel.getProperty("http://spinrdf.org/spin#rule"), q.asResource());
			}
		}
		
		File entity_rules_dir = new File(ENTITY_INFERENCE_DIR);
		
		File[] entity_rules = entity_rules_dir.listFiles();
		for (int i = 0; i < entity_rules.length; i++) {
			if (entity_rules[i].getName().endsWith(".txt")){
				FileInputStream fis = new FileInputStream(entity_rules[i]); 
				BufferedReader in = new BufferedReader(new InputStreamReader(fis, "UTF-8"));
				String queryStr = "";
				String line = "";
	
				while (( line = in.readLine()) != null) {
					queryStr = queryStr + line;
				}
				
				fis.close();
				
				Query q = ARQ2SPIN.parseQuery(queryStr, baseModel);
				
				baseModel.add(baseModel.getResource("http://www.w3.org/ns/prov#Entity"), 
						baseModel.getProperty("http://spinrdf.org/spin#rule"), q.asResource());
			}
			
		}
	
		
		return baseModel;
			
	}
	
	
	
	public static Model addConstraints(Model baseModel) throws Exception
	{
		File activity_rules_dir = new File(ACTIVITY_CONSTRAINTS_DIR);
		
		File[] activity_rules = activity_rules_dir.listFiles();
		for (int i = 0; i < activity_rules.length; i++) {
			if (activity_rules[i].getName().endsWith(".txt")){
				FileInputStream fis = new FileInputStream(activity_rules[i]); 
				BufferedReader in = new BufferedReader(new InputStreamReader(fis, "UTF-8"));
				String queryStr = "";
				String line = "";
	
				while (( line = in.readLine()) != null) {
					queryStr = queryStr + line;
				}
				
				fis.close();
				
				Query q = ARQ2SPIN.parseQuery(queryStr, baseModel);
				
				baseModel.add(baseModel.getResource("http://www.w3.org/ns/prov#Activity"), 
						baseModel.getProperty("http://spinrdf.org/spin#constraint"), q.asResource());
			}
			
		}
		
		File entity_rules_dir = new File(ENTITY_CONSTRAINTS_DIR);
		
		File[] entity_rules = entity_rules_dir.listFiles();
		for (int i = 0; i < entity_rules.length; i++) {
			if (entity_rules[i].getName().endsWith(".txt")){
				FileInputStream fis = new FileInputStream(entity_rules[i]); 
				BufferedReader in = new BufferedReader(new InputStreamReader(fis, "UTF-8"));
				String queryStr = "";
				String line = "";
	
				while (( line = in.readLine()) != null) {
					queryStr = queryStr + line;
				}
				
				fis.close();
				
				Query q = ARQ2SPIN.parseQuery(queryStr, baseModel);
				
				baseModel.add(baseModel.getResource("http://www.w3.org/ns/prov#Entity"), 
						baseModel.getProperty("http://spinrdf.org/spin#constraint"), q.asResource());
			}
			
		}
		
		return baseModel;

	}
}
