package apimodels;

import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * CompoundInfoIdentifiers
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class CompoundInfoIdentifiers   {
  @JsonProperty("chebi")
  
  private String chebi;

  @JsonProperty("chembl")
  
  private String chembl;

  @JsonProperty("drugbank")
  
  private String drugbank;

  @JsonProperty("pubchem")
  
  private String pubchem;

  @JsonProperty("mesh")
  
  private String mesh;

  @JsonProperty("hmdb")
  
  private String hmdb;

  @JsonProperty("unii")
  
  private String unii;

  @JsonProperty("kegg")
  
  private String kegg;

  @JsonProperty("gtopdb")
  
  private String gtopdb;

  @JsonProperty("chembank")
  
  private String chembank;

  @JsonProperty("drugcentral")
  
  private String drugcentral;

  @JsonProperty("cas")
  
  private String cas;

  @JsonProperty("mychem_info")
  
  private String mychemInfo;

  public CompoundInfoIdentifiers chebi(String chebi) {
    this.chebi = chebi;
    return this;
  }

   /**
   * ChEBI id of the compound (CURIE).
   * @return chebi
  **/
  public String getChebi() {
    return chebi;
  }

  public void setChebi(String chebi) {
    this.chebi = chebi;
  }

  public CompoundInfoIdentifiers chembl(String chembl) {
    this.chembl = chembl;
    return this;
  }

   /**
   * ChEMBL id of the compound (CURIE).
   * @return chembl
  **/
  public String getChembl() {
    return chembl;
  }

  public void setChembl(String chembl) {
    this.chembl = chembl;
  }

  public CompoundInfoIdentifiers drugbank(String drugbank) {
    this.drugbank = drugbank;
    return this;
  }

   /**
   * DrugBank id of the compound (CURIE).
   * @return drugbank
  **/
  public String getDrugbank() {
    return drugbank;
  }

  public void setDrugbank(String drugbank) {
    this.drugbank = drugbank;
  }

  public CompoundInfoIdentifiers pubchem(String pubchem) {
    this.pubchem = pubchem;
    return this;
  }

   /**
   * PubChem CID of the compound (CURIE).
   * @return pubchem
  **/
  public String getPubchem() {
    return pubchem;
  }

  public void setPubchem(String pubchem) {
    this.pubchem = pubchem;
  }

  public CompoundInfoIdentifiers mesh(String mesh) {
    this.mesh = mesh;
    return this;
  }

   /**
   * MeSH id of the compound (CURIE).
   * @return mesh
  **/
  public String getMesh() {
    return mesh;
  }

  public void setMesh(String mesh) {
    this.mesh = mesh;
  }

  public CompoundInfoIdentifiers hmdb(String hmdb) {
    this.hmdb = hmdb;
    return this;
  }

   /**
   * HMDB id of the compound (CURIE).
   * @return hmdb
  **/
  public String getHmdb() {
    return hmdb;
  }

  public void setHmdb(String hmdb) {
    this.hmdb = hmdb;
  }

  public CompoundInfoIdentifiers unii(String unii) {
    this.unii = unii;
    return this;
  }

   /**
   * UNII id of the compound (CURIE).
   * @return unii
  **/
  public String getUnii() {
    return unii;
  }

  public void setUnii(String unii) {
    this.unii = unii;
  }

  public CompoundInfoIdentifiers kegg(String kegg) {
    this.kegg = kegg;
    return this;
  }

   /**
   * KEGG id of the compound (CURIE).
   * @return kegg
  **/
  public String getKegg() {
    return kegg;
  }

  public void setKegg(String kegg) {
    this.kegg = kegg;
  }

  public CompoundInfoIdentifiers gtopdb(String gtopdb) {
    this.gtopdb = gtopdb;
    return this;
  }

   /**
   * Guide to PHARMACOLOGY id of the compound (CURIE).
   * @return gtopdb
  **/
  public String getGtopdb() {
    return gtopdb;
  }

  public void setGtopdb(String gtopdb) {
    this.gtopdb = gtopdb;
  }

  public CompoundInfoIdentifiers chembank(String chembank) {
    this.chembank = chembank;
    return this;
  }

   /**
   * ChemBank id of the compound (CURIE).
   * @return chembank
  **/
  public String getChembank() {
    return chembank;
  }

  public void setChembank(String chembank) {
    this.chembank = chembank;
  }

  public CompoundInfoIdentifiers drugcentral(String drugcentral) {
    this.drugcentral = drugcentral;
    return this;
  }

   /**
   * DrugCentral id of the compound (CURIE).
   * @return drugcentral
  **/
  public String getDrugcentral() {
    return drugcentral;
  }

  public void setDrugcentral(String drugcentral) {
    this.drugcentral = drugcentral;
  }

  public CompoundInfoIdentifiers cas(String cas) {
    this.cas = cas;
    return this;
  }

   /**
   * CAS id of the compound (CURIE).
   * @return cas
  **/
  public String getCas() {
    return cas;
  }

  public void setCas(String cas) {
    this.cas = cas;
  }

  public CompoundInfoIdentifiers mychemInfo(String mychemInfo) {
    this.mychemInfo = mychemInfo;
    return this;
  }

   /**
   * myChem.info id of the compound.
   * @return mychemInfo
  **/
  public String getMychemInfo() {
    return mychemInfo;
  }

  public void setMychemInfo(String mychemInfo) {
    this.mychemInfo = mychemInfo;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    CompoundInfoIdentifiers compoundInfoIdentifiers = (CompoundInfoIdentifiers) o;
    return Objects.equals(chebi, compoundInfoIdentifiers.chebi) &&
        Objects.equals(chembl, compoundInfoIdentifiers.chembl) &&
        Objects.equals(drugbank, compoundInfoIdentifiers.drugbank) &&
        Objects.equals(pubchem, compoundInfoIdentifiers.pubchem) &&
        Objects.equals(mesh, compoundInfoIdentifiers.mesh) &&
        Objects.equals(hmdb, compoundInfoIdentifiers.hmdb) &&
        Objects.equals(unii, compoundInfoIdentifiers.unii) &&
        Objects.equals(kegg, compoundInfoIdentifiers.kegg) &&
        Objects.equals(gtopdb, compoundInfoIdentifiers.gtopdb) &&
        Objects.equals(chembank, compoundInfoIdentifiers.chembank) &&
        Objects.equals(drugcentral, compoundInfoIdentifiers.drugcentral) &&
        Objects.equals(cas, compoundInfoIdentifiers.cas) &&
        Objects.equals(mychemInfo, compoundInfoIdentifiers.mychemInfo);
  }

  @Override
  public int hashCode() {
    return Objects.hash(chebi, chembl, drugbank, pubchem, mesh, hmdb, unii, kegg, gtopdb, chembank, drugcentral, cas, mychemInfo);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class CompoundInfoIdentifiers {\n");
    
    sb.append("    chebi: ").append(toIndentedString(chebi)).append("\n");
    sb.append("    chembl: ").append(toIndentedString(chembl)).append("\n");
    sb.append("    drugbank: ").append(toIndentedString(drugbank)).append("\n");
    sb.append("    pubchem: ").append(toIndentedString(pubchem)).append("\n");
    sb.append("    mesh: ").append(toIndentedString(mesh)).append("\n");
    sb.append("    hmdb: ").append(toIndentedString(hmdb)).append("\n");
    sb.append("    unii: ").append(toIndentedString(unii)).append("\n");
    sb.append("    kegg: ").append(toIndentedString(kegg)).append("\n");
    sb.append("    gtopdb: ").append(toIndentedString(gtopdb)).append("\n");
    sb.append("    chembank: ").append(toIndentedString(chembank)).append("\n");
    sb.append("    drugcentral: ").append(toIndentedString(drugcentral)).append("\n");
    sb.append("    cas: ").append(toIndentedString(cas)).append("\n");
    sb.append("    mychemInfo: ").append(toIndentedString(mychemInfo)).append("\n");
    sb.append("}");
    return sb.toString();
  }

  /**
   * Convert the given object to string with each line indented by 4 spaces
   * (except the first line).
   */
  private String toIndentedString(Object o) {
    if (o == null) {
      return "null";
    }
    return o.toString().replace("\n", "\n    ");
  }
}

