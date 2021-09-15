package apimodels;

import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * GeneInfoIdentifiers
 */

@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class GeneInfoIdentifiers   {
  @JsonProperty("entrez")
  private String entrez;

  @JsonProperty("hgnc")
  private String hgnc;

  @JsonProperty("mim")
  private String mim;

  @JsonProperty("ensembl")
  private List<String> ensembl = null;

  @JsonProperty("mygene_info")
  private String mygeneInfo;

  public GeneInfoIdentifiers entrez(String entrez) {
    this.entrez = entrez;
    return this;
  }

   /**
   * Entrez gene id (CURIE).
   * @return entrez
  **/
    public String getEntrez() {
    return entrez;
  }

  public void setEntrez(String entrez) {
    this.entrez = entrez;
  }

  public GeneInfoIdentifiers hgnc(String hgnc) {
    this.hgnc = hgnc;
    return this;
  }

   /**
   * HGNC gene id (CURIE).
   * @return hgnc
  **/
    public String getHgnc() {
    return hgnc;
  }

  public void setHgnc(String hgnc) {
    this.hgnc = hgnc;
  }

  public GeneInfoIdentifiers mim(String mim) {
    this.mim = mim;
    return this;
  }

   /**
   * OMIM gene id (CURIE).
   * @return mim
  **/
    public String getMim() {
    return mim;
  }

  public void setMim(String mim) {
    this.mim = mim;
  }

  public GeneInfoIdentifiers ensembl(List<String> ensembl) {
    this.ensembl = ensembl;
    return this;
  }

  public GeneInfoIdentifiers addEnsemblItem(String ensemblItem) {
    if (ensembl == null) {
      ensembl = new ArrayList<>();
    }
    ensembl.add(ensemblItem);
    return this;
  }

   /**
   * ENSEMBL gene id (CURIE).
   * @return ensembl
  **/
    public List<String> getEnsembl() {
    return ensembl;
  }

  public void setEnsembl(List<String> ensembl) {
    this.ensembl = ensembl;
  }

  public GeneInfoIdentifiers mygeneInfo(String mygeneInfo) {
    this.mygeneInfo = mygeneInfo;
    return this;
  }

   /**
   * myGene.info primary id.
   * @return mygeneInfo
  **/
    public String getMygeneInfo() {
    return mygeneInfo;
  }

  public void setMygeneInfo(String mygeneInfo) {
    this.mygeneInfo = mygeneInfo;
  }


  @Override
  public boolean equals(java.lang.Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    GeneInfoIdentifiers geneInfoIdentifiers = (GeneInfoIdentifiers) o;
    return Objects.equals(entrez, geneInfoIdentifiers.entrez) &&
        Objects.equals(hgnc, geneInfoIdentifiers.hgnc) &&
        Objects.equals(mim, geneInfoIdentifiers.mim) &&
        Objects.equals(ensembl, geneInfoIdentifiers.ensembl) &&
        Objects.equals(mygeneInfo, geneInfoIdentifiers.mygeneInfo);
  }

  @Override
  public int hashCode() {
    return Objects.hash(entrez, hgnc, mim, ensembl, mygeneInfo);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class GeneInfoIdentifiers {\n");
    
    sb.append("    entrez: ").append(toIndentedString(entrez)).append("\n");
    sb.append("    hgnc: ").append(toIndentedString(hgnc)).append("\n");
    sb.append("    mim: ").append(toIndentedString(mim)).append("\n");
    sb.append("    ensembl: ").append(toIndentedString(ensembl)).append("\n");
    sb.append("    mygeneInfo: ").append(toIndentedString(mygeneInfo)).append("\n");
    sb.append("}");
    return sb.toString();
  }

  /**
   * Convert the given object to string with each line indented by 4 spaces
   * (except the first line).
   */
  private String toIndentedString(java.lang.Object o) {
    if (o == null) {
      return "null";
    }
    return o.toString().replace("\n", "\n    ");
  }
}

