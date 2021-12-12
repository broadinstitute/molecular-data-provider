package org.broadinstitute.translator.moleprodb.builder;

import java.net.URL;
import java.sql.SQLException;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

import org.broadinstitute.translator.moleprodb.db.MoleProDB;

import apimodels.CollectionInfo;
import apimodels.CompoundInfo;
import apimodels.Element;
import apimodels.TransformerInfo;
import transformer.InternalTransformer;
import transformer.Transformer;
import transformer.Transformers;
import transformer.classes.Other;
import transformer.Transformer.Query;
import transformer.collection.CollectionElement.CompoundElement;
import transformer.collection.CollectionsEntry;
import transformer.exception.NotFoundException;
import transformer.mapping.MappedBiolinkClass;
import transformer.util.HTTP;
import transformer.util.JSON;

public abstract class Loader {

	protected static class BiolinkClass {
		public static String ChemicalSubstance = "SmallMolecule";
	}

	protected final MoleProDB db;

	public static final HashMap<String,Long> profile = new HashMap<>();


	public Loader(MoleProDB db) {
		super();
		this.db = db;
	}


	final protected Element[] transform(final Transformer transformer, final Query query) throws Exception {
		final Element[] elements = callTransformer(transformer, query);
		for (Element element : elements) {
			if (element != null) {
				Other.mapElement(transformer.info, element);
			}
		}
		return elements;
	}


	protected long biolinkClassId(String biolinkClass) throws SQLException {
		return db.biolinkClassTable.biolinkClassId(MappedBiolinkClass.map(biolinkClass));
	}


	/*******************************************************
	 * 
	 * 
	 * 
	 * @param transformerNames
	 * @throws NotFoundException
	 */
	protected static Transformer[] getTransformers(final String[] transformerNames) throws NotFoundException {
		Transformers.getTransformers();
		Transformer[] transformers = new Transformer[transformerNames.length];
		for (int i = 0; i < transformers.length; i++) {
			transformers[i] = Transformers.getTransformer(transformerNames[i]);
		}
		return transformers;
	}


	/*********************************************************************
	 * 
	 * 
	 * 
	 * @param transformer
	 * @param query
	 * @return
	 * @throws Exception
	 */
	private static Element[] callTransformer(final Transformer transformer, final Query query) throws Exception {
		TransformerInfo info = transformer.info;
		if (transformer instanceof InternalTransformer || info.getUrl().length() == 0) {
			return callInternalTransformer(transformer, query);
		}
		final URL url = new URL(info.getUrl() + "/transform");
		final String json = JSON.mapper.writeValueAsString(query);
		final Date start = new Date();
		final String response = HTTP.post(url, json);
		profile(transformer.info.getName(), start);
		if (info.getVersion().startsWith("1.") || info.getVersion().startsWith("2.0.")) {
			final CompoundInfo[] compounds = JSON.mapper.readValue(response, CompoundInfo[].class);
			Element[] elements = new Element[compounds.length];
			for (int i = 0; i < compounds.length; i++) {
				elements[i] = new CompoundElement(compounds[i]).getElement();
			}
			return elements;
		}
		else {
			return JSON.mapper.readValue(response, Element[].class);
		}
	}


	private static Element[] callInternalTransformer(final Transformer transformer, final Query query) throws Exception {
		final Date start = new Date();
		final CollectionsEntry response = transformer.transform(query, new CollectionInfo());
		profile(transformer.info.getName() + " (internal)", start);
		Element[] elements = new Element[response.getElements().length];
		for (int i = 0; i < elements.length; i++) {
			elements[i] = response.getElements()[i].getElement();
		}
		return elements;
	}


	public static void printMemoryStatus() {
		printMemoryStatus("");
	}


	public static void printMemoryStatus(String prefix) {
		StringBuilder status = new StringBuilder(prefix);
		status.append("free memory:" + Runtime.getRuntime().freeMemory() / 1000000);
		status.append("/" + Runtime.getRuntime().totalMemory() / 1000000);
		System.out.println(status.toString());
	}


	public static void profile(String transformerName, Date start) {
		final long responseTime = (new Date()).getTime() - start.getTime();
		long sumTime = profile.getOrDefault(transformerName, 0L);
		profile.put(transformerName, sumTime + responseTime);
	}


	public static void profileReport() {
		System.out.println();
		for (Map.Entry<String,Long> entry : profile.entrySet()) {
			final String transformer = entry.getKey();
			final long responseTime = entry.getValue();
			System.out.println(transformer + "\t" + responseTime);
		}
	}
}
