package org.broadinstitute.translator.moleprodb.builder;

import java.io.BufferedReader;
import java.io.FileReader;
import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.HashSet;
import java.util.Map;

import org.broadinstitute.translator.moleprodb.db.IdentifierTable;
import org.broadinstitute.translator.moleprodb.db.MoleProDB;

import com.fasterxml.jackson.annotation.JsonProperty;

import apimodels.Element;
import transformer.Config;
import transformer.Transformers;
import transformer.util.HTTP;
import transformer.util.JSON;

public class HierarchyLoader extends Loader {

	private final int BATCH_SIZE = 100;

	private final ListElementLoader listElementLoader;

	private final TransformerRun nodeNormalizer;
	private final int sourceId;

	private final String[] matchFields;


	public HierarchyLoader(MoleProDB db) throws Exception {
		super(db);
		listElementLoader = new ListElementLoader(db);
		Transformers.getTransformers();
		nodeNormalizer = new TransformerRun("SRI node normalizer producer");
		sourceId = db.sourceTable.sourceId(nodeNormalizer.info.getName());
		matchFields = new String[] { "mondo", "hpo", "hp", "disease_ontology", "omim", "umls", "nci_thesaurus", "ncit", "snomed", "snomedct"};
	}


	private TrapiQuery getQuery(final String subjectElementId, final boolean isSubclass) {
		final TrapiQuery query = new TrapiQuery();
		if (isSubclass)
			query.predicates = new String[] { "biolink:subclass_of" };
		else
			query.predicates = new String[] { "biolink:superclass_of" };
		query.node0ids = new String[] { subjectElementId };
		return query;
	}


	private ArrayList<String> getParents(final TrapiQuery query, final String queryId) throws Exception {
		final ArrayList<String> parents = new ArrayList<>();

		String url = Config.getConfig().url().getAutomatHierarchyURL();
		final String json = HTTP.post(new URL(url), query.toJSON());
		final TrapiResponse response = JSON.mapper.readValue(json, TrapiResponse.class);
		for (Result result : response.message.results) {
			String subjectId = result.nodeBindings.get(query.subjectNode)[0].id;
			String subjectQueryId = result.nodeBindings.get(query.subjectNode)[0].qnodeId;
			String objectId = result.nodeBindings.get(query.objectNode)[0].id;
			if (subjectId != null && (subjectId.equals(queryId) || subjectId.equals(subjectQueryId))) {
				parents.add(objectId);
			}
		}
		return parents;
	}


	private HashSet<String> getParents(final String elementId, final boolean isSubclass) throws Exception {
		Date start = new Date();
		final HashSet<String> parents = new HashSet<>();
		parents.add(elementId);
		try {
			final TrapiQuery query = getQuery(elementId, isSubclass);
			for (String parent : getParents(query, elementId)) {
				parents.add(parent);
			}
		}
		catch (Exception e) {
			System.out.println("[error] failed to retrieve hierarchy for " + elementId + ", isSubclass=" + isSubclass);
			System.out.println(e.getMessage());
		}
		profile("getParents", start);
		return parents;
	}


	public void loadHierarchy(final String hierarchyFile) throws Exception {
		final BufferedReader input = new BufferedReader(new FileReader(hierarchyFile));
		HashSet<Long> hierarchyDone = db.elementHierarchyTable.hierarchyDone();
		System.out.println("hierarchy done = " + hierarchyDone.size());
		int i = 0;
		input.readLine(); // header
		for (String line = input.readLine(); line != null; line = input.readLine()) {
			long element = Long.parseLong(line);
			if (!hierarchyDone.contains(element)) {
				loadHierarchy(element, true);
				// loadHierarchy(element, false);
				i = i + 1;
				if (i % 10 == 0) {
					System.out.println("i = " + i + ": ");
					db.commit();
				}
				if (i % 100 == 0) {
					System.out.println("db.reconnect");
					db.reconnect();
					printMemoryStatus();
				}
			}
		}
		db.commit();
		input.close();
	}


	private Iterable<String> getIdentifier(final Map<String,Object> identifiers) {
		for (String field : matchFields) {
			if (identifiers.get(field) != null)
				return IdentifierTable.identifiers(identifiers.get(field));
		}
		return new ArrayList<String>();
	}


	private void loadHierarchy(long elementId, final boolean isSubclass) throws Exception {
		final Element element = listElementLoader.element(elementId);
		final HashSet<Long> parentElementIds = new HashSet<>();
		for (String elementIdentifier : getIdentifier(element.getIdentifiers())) {
			ArrayList<String> batch = new ArrayList<>();
			for (String parentId : getParents(elementIdentifier, isSubclass)) {
				final ArrayList<Long> dbElementIds = db.listElementIdentifierTable.findParentIds(parentId, sourceId);
				if (dbElementIds.size() == 0) {
					batch.add(parentId);
					if (batch.size() >= BATCH_SIZE) {
						for (long parentElementId : listElementLoader.loadElements(nodeNormalizer, batch, matchFields)) {
							parentElementIds.add(parentElementId);
						}
						batch = new ArrayList<>();
					}
				}
				else {
					for (long parentElementId : dbElementIds) {
						parentElementIds.add(parentElementId);
					}
				}
			}

			if (batch.size() > 0) {
				for (long parentElementId : listElementLoader.loadElements(nodeNormalizer, batch, matchFields)) {
					parentElementIds.add(parentElementId);
				}
			}
		}
		Date start = new Date();
		final String hierarchyType = (isSubclass) ? "biolink:subclass_of" : "biolink:superclass_of";
		for (long parentElementId : parentElementIds) {
			db.elementHierarchyTable.saveHierarchy(elementId, parentElementId, hierarchyType);
		}
		if (parentElementIds.size() > 100) {
			System.out.println("elementId: " + elementId + " " + hierarchyType + " size " + parentElementIds.size());
		}
		profile("save hierarchy", start);
	}


	static class TrapiQuery {

		private String[] node0ids;
		private String[] predicates;
		private String[] node1ids;
		final String subjectNode = "n0";
		final String objectNode = "n1";


		String toJSON() {
			return object(message());
		}


		private String message() {
			return field("message") + object(queryGraph());
		}


		private String queryGraph() {
			return field("query_graph") + object(nodes(), edges());
		}


		private String edges() {
			return field("edges") + object(edge());
		}


		private String edge() {
			return field("e0") + object(field("subject", subjectNode), field("object", objectNode), predicates());
		}


		private String predicates() {
			return field("predicates", predicates);
		}


		private String nodes() {
			return field("nodes") + object(node(subjectNode, node0ids), node(objectNode, node1ids));
		}


		private String node(String id, String[] nodeIds) {
			String categories = field("categories", new String[] { "biolink:Disease" });
			String fields = (nodeIds == null) ? object(categories) : object(categories, field("ids", nodeIds));
			return field(id) + fields;
		}


		private String field(String fieldName) {
			return "" + '"' + fieldName + '"' + ": ";
		}


		private String field(String fieldName, String value) {
			return field(fieldName) + '"' + value + '"';
		}


		private String field(String fieldName, String[] array) {
			return field(fieldName) + array(array);
		}


		private String array(String[] array) {
			return "[\"" + String.join("\", \"", array) + "\"]";
		}


		private String object(String... fields) {
			return "{\n" + String.join(",\n", Arrays.asList(fields)) + "\n}";
		}
	}


	static class TrapiResponse {
		private TrapiMessage message;


		public void setMessage(TrapiMessage message) {
			this.message = message;
		}
	}


	static class TrapiMessage {
		@SuppressWarnings("unused")
		private KnowledgeGraph knowledgeGraph;
		@SuppressWarnings("unused")
		private Object queryGraph;
		private Result[] results;


		@JsonProperty("knowledge_graph")
		public void setKnowledgeGraph(KnowledgeGraph knowledgeGraph) {

			this.knowledgeGraph = knowledgeGraph;
		}


		public void setQueryGraph(Object queryGraph) {
			this.queryGraph = queryGraph;
		}


		public void setResults(Result[] results) {
			// System.out.println("setting results " + results);
			this.results = results;
		}
	}


	static class KnowledgeGraph {
		@SuppressWarnings("unused")
		private Map<String,Node> nodes;
		@SuppressWarnings("unused")
		private Map<String,Edge> edges;


		@JsonProperty("nodes")
		public void setNodes(Map<String,Node> nodes) {
			// System.out.println("setting nodes" + nodes);
			this.nodes = nodes;
		}


		public void setEdges(Map<String,Edge> edges) {
			this.edges = edges;
		}

	}


	static class Node {
		@SuppressWarnings("unused")
		private String name;
		@SuppressWarnings("unused")
		private String[] categories;


		public void setName(String name) {

			this.name = name;
		}


		public void setCategories(String[] categories) {
			this.categories = categories;
		}
	}


	static class Edge {
		@SuppressWarnings("unused")
		private String subject;
		@SuppressWarnings("unused")
		private String predicate;
		@SuppressWarnings("unused")
		private String object;


		public void setSubject(String subject) {
			this.subject = subject;
		}


		public void setPredicate(String predicate) {
			this.predicate = predicate;
		}


		public void setObject(String object) {
			this.object = object;
		}
	}


	static class Result {
		private Map<String,ID[]> nodeBindings;


		@JsonProperty("node_bindings")
		public void setNodeBindings(Map<String,ID[]> nodeBindings) {
			this.nodeBindings = nodeBindings;
		}

	}


	static class Analysis {
		@SuppressWarnings("unused")
		private Map<String,ID[]> edgeBindings;


		@JsonProperty("edge_bindings")
		public void setEdgeBindings(Map<String,ID[]> edgeBindings) {
			this.edgeBindings = edgeBindings;
		}

	}


	static class ID {
		private String id;
		private String qnodeId;


		public void setId(String id) {
			this.id = id;
		}


		@JsonProperty("query_id")
		public void setQnodeId(String qnodeId) {
			this.qnodeId = qnodeId;
		}
	}

}
