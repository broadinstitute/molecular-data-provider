package org.broadinstitute.translator.moleprodb.builder;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import org.broadinstitute.translator.moleprodb.db.MoleProDB;

import apimodels.Attribute;
import apimodels.Element;
import apimodels.Names;
import apimodels.Parameter;
import apimodels.Property;
import transformer.Transformer;
import transformer.TransformerQuery;

public class StructureLoader extends Loader {

	public StructureLoader(MoleProDB db) {
		super(db);
	}

	private static final int BATCH_SIZE = 100;


	/*******************************************************
	 * 
	 * 
	 * 
	 * @param db
	 * @param transformerName
	 * @param compoundFile
	 * @throws Exception
	 */
	public void loadStructures(final String[] transformerNames, final String compoundFile) throws Exception {
		Transformer[] transformers = getTransformers(transformerNames);
		String[] batch = new String[BATCH_SIZE];
		int i = 0;
		final BufferedReader input = new BufferedReader(new FileReader(compoundFile));
		try {
			input.readLine(); // header line
			for (String compound = input.readLine(); compound != null; compound = input.readLine()) {
				batch[i % BATCH_SIZE] = compound;
				i = i + 1;
				if (i % BATCH_SIZE == 0) {
					System.out.println(compound + " @"+i);
					loadStructures(transformers, batch);
					db.commit();
					System.out.println();
					batch = new String[BATCH_SIZE];
				}
				if (i % (10 * BATCH_SIZE) == 0) {
					System.out.println("db.reconnect");
					db.reconnect();
				}
			}
			loadStructures(transformers, batch);
			db.commit();
		}
		finally {
			db.rollback();
			input.close();
		}

	}


	/********************************************************
	 * 
	 * 
	 * 
	 * @param db
	 * @param transformers
	 * @param compounds
	 * @throws Exception
	 */
	public void loadStructures(final Transformer[] transformers, final String[] compounds) throws Exception {
		for (Transformer transformer : transformers) {
			try {
				final int sourceId = db.sourceTable.sourceId(transformer.info.getName());
				final List<Property> controls = new ArrayList<>();
				final Parameter parameter = transformer.info.getParameters().get(0);
				if (parameter.getMultivalued() != null && parameter.getMultivalued()) {
					for (String value : compounds) {
						if (value != null)
							controls.add(new Property().name(parameter.getName()).value(value));
					}
				}
				else {
					controls.add(new Property().name(parameter.getName()).value(String.join(";", compounds)));
				}
				if (controls.size() > 0) {
					final TransformerQuery query = new TransformerQuery(controls);
					final Element[] elements = transform(transformer, query);
					for (Element element : elements) {
						if (element != null) {
							save(sourceId, element);
						}
					}
				}
			}

			catch (IOException e) {
				if (compounds.length > 1) {
					System.err.println("INFO: batch load failed, trying single elements");
					final String[] singleton = new String[1];
					for (String compound : compounds) {
						singleton[0] = compound;
						loadStructures(transformers, singleton);
					}
				}
				else {

					System.err.println("WARNING: when processing " + compounds[0] + ", " + transformer.info.getName() + " failed: " + e.getMessage());
					e.printStackTrace();
				}
			}
			catch (Exception e) {
				System.err.println("WARNING: " + transformer.info.getName() + " failed: " + e.getMessage());
				e.printStackTrace();
			}
		}
		printMemoryStatus();
	}


	/***********************************************
	 * 
	 * @param db
	 * @param sourceId
	 * @param element
	 * @throws SQLException
	 */
	void save(final int sourceId, final Element element) throws SQLException {
		if (element.getIdentifiers() == null) {
			return;
		}

		String inchi = (String)element.getIdentifiers().get("inchi");
		String inchikey = (String)element.getIdentifiers().get("inchikey");
		Date start = new Date();
		final long biolinkClassId = biolinkClassId(BiolinkClass.ChemicalStructure);
		long structureId = db.chemStructureTable.getStructureId(inchi, inchikey);
		if (structureId <= 0) {
			structureId = db.chemStructureIdentifierTable.structureId(element.getIdentifiers());
		}
		profile("get structureId", start);
		if (structureId > 0) {
			start = new Date();
			db.chemStructureIdentifierTable.saveIdentifiers(structureId, biolinkClassId, element, sourceId);
			profile("save identifiers", start);
			start = new Date();
			if (element.getNamesSynonyms() != null) {
				for (Names names : element.getNamesSynonyms()) {
					db.chemStructureNameTable.saveNames(structureId, sourceId, names);
				}
			}
			profile("save names", start);
			start = new Date();
			if (element.getAttributes() != null) {
				// Save to the Chem_Structure_Attribute Table, the cross reference between
				// Chem_Structure and Attribute Tables.
				saveChemStructureAttributes(element, structureId, sourceId);
			}
			profile("save attributes", start);
		}
	}


	/************************************************
	 * 
	 * @param db
	 * @param attributes
	 * @throws SQLException
	 */
	private void saveChemStructureAttributes(final Element element, long structureId, int sourceId) throws SQLException {
		for (Attribute attribute : element.getAttributes()) {
			db.chemStructureAttributeTable.insert(structureId, attribute, sourceId);
		}
	}

}
