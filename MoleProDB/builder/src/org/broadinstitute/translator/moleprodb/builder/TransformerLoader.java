package org.broadinstitute.translator.moleprodb.builder;

import org.broadinstitute.translator.moleprodb.db.MoleProDB;

import apimodels.TransformerInfo;
import transformer.Transformers;

public class TransformerLoader extends Loader {

	public TransformerLoader(MoleProDB db) {
		super(db);
	}


	public void loadTransformers() throws Exception {

		/****************************************************************
		 * Read from the conf/transformers.txt file, iterate through the list of
		 * transformers, and make API request for transformer info from the transformers
		 * themselves
		 * 
		 **/
		for (TransformerInfo transformer : Transformers.getTransformers()) {
			System.out.println(transformer.getName());
			int sourceId = db.sourceTable.sourceId(transformer.getName());
			if (sourceId <= 0) {
				db.sourceTable.insert(
					transformer.getLabel(), transformer.getProperties().getSourceUrl(), transformer.getProperties().getSourceVersion(), 
					transformer.getName(), transformer.getUrl(), transformer.getVersion()
				);
			}
		}

		db.commit();
	}
}
