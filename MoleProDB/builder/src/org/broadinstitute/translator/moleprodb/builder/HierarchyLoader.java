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
import transformer.Transformer;
import transformer.Transformers;
import transformer.util.HTTP;
import transformer.util.JSON;

public class HierarchyLoader extends Loader {

	private final int BATCH_SIZE = 100;

	private final ListElementLoader listElementLoader;

	private final Transformer nodeNormalizer;
	private final int sourceId;

	private final String[] matchFields;


	public HierarchyLoader(MoleProDB db) throws Exception {
		super(db);
		listElementLoader = new ListElementLoader(db);
		Transformers.getTransformers();
		nodeNormalizer = Transformers.getTransformer("SRI node normalizer producer");
		sourceId = db.sourceTable.sourceId(nodeNormalizer.info.getName());
		matchFields = new String[] { "mondo", "hpo", "hp" };
	}


	private ArrayList<String> getParents(final String subjectElementId, final String objectElementId) throws Exception {
		final ArrayList<String> parents = new ArrayList<>();
		final TrapiQuery query = new TrapiQuery();
		String nodeId = "n1";
		query.predicates = new String[] { "biolink:subclass_of" };
		if (subjectElementId != null) {
			query.node0ids = new String[] { subjectElementId };
			nodeId = "n1";
		}
		if (objectElementId != null) {
			query.node1ids = new String[] { objectElementId };
			nodeId = "n0";
		}
		try {
			final String json = HTTP.post(new URL("https://automat.transltr.io/ontological-hierarchy/1.3/query"), query.toJSON());
			final TrapiResponse response = JSON.mapper.readValue(json, TrapiResponse.class);
			for (Result result : response.message.results) {
				String objectId = result.nodeBindings.get(nodeId)[0].id;
				parents.add(objectId);
			}
		}
		catch (Exception e) {
			System.out.println("[error] failed to retrieve hierarchy for " + subjectElementId + "/" + objectElementId);
			System.out.println(e.getMessage());
		}
		return parents;
	}


	private HashSet<String> getParents(final String elementId, final boolean isSubclass) throws Exception {
		Date start = new Date();
		final HashSet<String> parents = new HashSet<>();
		parents.add(elementId);
		if (isSubclass)
			for (String parent : getParents(elementId, null)) {
				parents.add(parent);
			}
		else
			for (String parent : getParents(null, elementId)) {
				parents.add(parent);
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
				loadHierarchy(element, false);
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


	private void loadHierarchy(long elementId, final boolean isSubclass) throws Exception {
		final Element element = listElementLoader.element(elementId);
		final HashSet<Long> parentElementIds = new HashSet<>();
		for (String mondoId : IdentifierTable.identifiers(element.getIdentifiers().get("mondo"))) {
			ArrayList<String> batch = new ArrayList<>();
			for (String parentId : getParents(mondoId, isSubclass)) {
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
			return field("e0") + object(field("subject", "n0"), field("object", "n1"), predicates());
		}


		private String predicates() {
			return field("predicates", predicates);
		}


		private String nodes() {
			return field("nodes") + object(node("n0", node0ids), node("n1", node1ids));
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
		@SuppressWarnings("unused")
		private Map<String,ID[]> edgeBindings;


		@JsonProperty("node_bindings")
		public void setNodeBindings(Map<String,ID[]> nodeBindings) {
			this.nodeBindings = nodeBindings;
		}


		@JsonProperty("edge_bindings")
		public void setEdgeBindings(Map<String,ID[]> edgeBindings) {
			this.edgeBindings = edgeBindings;
		}

	}


	static class ID {
		private String id;


		public void setId(String id) {
			this.id = id;
		}
	}

}
