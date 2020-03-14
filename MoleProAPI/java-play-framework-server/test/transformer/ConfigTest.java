package transformer;

import org.junit.Test;
import static org.junit.Assert.*;

public class ConfigTest {

	@Test
	public void testExpirationTimeParser() {

		long fifteenSec = 15L * 1000;
		assertEquals(fifteenSec, Config.ExpirationTimes.parseTime("15s"));
		long sixMinutes = 6L * 60 * 1000;
		assertEquals(sixMinutes, Config.ExpirationTimes.parseTime("6m"));
		long sevenHours = 7L * 60 * 60 * 1000;
		assertEquals(sevenHours, Config.ExpirationTimes.parseTime("7h"));
		long threeDays = 3L * 24 * 60 * 60 * 1000;
		assertEquals(threeDays, Config.ExpirationTimes.parseTime("3d"));
		long twoWeeks = 14L * 24 * 60 * 60 * 1000;
		assertEquals(twoWeeks, Config.ExpirationTimes.parseTime("2w"));
		long fourMonths = 4L * 365 * 24 * 60 * 60 * 1000 / 12;
		assertEquals(fourMonths, Config.ExpirationTimes.parseTime("4mo"));
		long twoKyears = 2000L * 365 * 24 * 60 * 60 * 1000;
		assertEquals(twoKyears, Config.ExpirationTimes.parseTime("2000y"));
	}


	@Test
	public void testUrls() {
		assertNotNull(Config.config.url().MyGeneInfo().query());
		assertNotNull(Config.config.url().MyGeneInfo().search());
		assertNotNull(Config.config.url().MyChemInfo().query());
		assertNotNull(Config.config.url().PubChem().description());
		assertNotNull(Config.config.url().PubChem().synonyms());
		assertNotNull(Config.config.url().PubChem().smiles());
		assertNotNull(Config.config.url().PubChem().inchi());
	}
	
	@Test
	public void testCuries() {
		assertNotNull(Config.config.getCuries().getCas());
		assertNotNull(Config.config.getCuries().getChebi());
		assertNotNull(Config.config.getCuries().getChembl());
		assertNotNull(Config.config.getCuries().getDrugbank());
		assertNotNull(Config.config.getCuries().getDrugcentral());
		assertNotNull(Config.config.getCuries().getHmdb());
		assertNotNull(Config.config.getCuries().getKegg());
		assertNotNull(Config.config.getCuries().getNbcigene());
		assertNotNull(Config.config.getCuries().getPubchem());
		assertNotNull(Config.config.getCuries().getEnsembl());
	}
	
	@Test
	public void testPriorities() {
		assertEquals(Config.config.getCompoundNamePriority("DrugBank"),2);
	}
}
