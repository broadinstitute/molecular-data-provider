package apimodels;

import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * CompoundInfoStructure
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen", date = "2020-03-04T17:03:22.330-05:00[America/New_York]")

@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class CompoundInfoStructure   {
  @JsonProperty("smiles")
  private String smiles;

  @JsonProperty("inchi")
  private String inchi;

  @JsonProperty("inchikey")
  private String inchikey;

  @JsonProperty("source")
  private String source;

  public CompoundInfoStructure smiles(String smiles) {
    this.smiles = smiles;
    return this;
  }

   /**
   * SMILES representation of the compound's structure.
   * @return smiles
  **/
    public String getSmiles() {
    return smiles;
  }

  public void setSmiles(String smiles) {
    this.smiles = smiles;
  }

  public CompoundInfoStructure inchi(String inchi) {
    this.inchi = inchi;
    return this;
  }

   /**
   * InChI representation of the compound's structure.
   * @return inchi
  **/
    public String getInchi() {
    return inchi;
  }

  public void setInchi(String inchi) {
    this.inchi = inchi;
  }

  public CompoundInfoStructure inchikey(String inchikey) {
    this.inchikey = inchikey;
    return this;
  }

   /**
   * InChI key representation of the compound's structure.
   * @return inchikey
  **/
    public String getInchikey() {
    return inchikey;
  }

  public void setInchikey(String inchikey) {
    this.inchikey = inchikey;
  }

  public CompoundInfoStructure source(String source) {
    this.source = source;
    return this;
  }

   /**
   * Source of the compound's structure.
   * @return source
  **/
    public String getSource() {
    return source;
  }

  public void setSource(String source) {
    this.source = source;
  }


  @Override
  public boolean equals(java.lang.Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    CompoundInfoStructure compoundInfoStructure = (CompoundInfoStructure) o;
    return Objects.equals(smiles, compoundInfoStructure.smiles) &&
        Objects.equals(inchi, compoundInfoStructure.inchi) &&
        Objects.equals(inchikey, compoundInfoStructure.inchikey) &&
        Objects.equals(source, compoundInfoStructure.source);
  }

  @Override
  public int hashCode() {
    return Objects.hash(smiles, inchi, inchikey, source);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class CompoundInfoStructure {\n");
    
    sb.append("    smiles: ").append(toIndentedString(smiles)).append("\n");
    sb.append("    inchi: ").append(toIndentedString(inchi)).append("\n");
    sb.append("    inchikey: ").append(toIndentedString(inchikey)).append("\n");
    sb.append("    source: ").append(toIndentedString(source)).append("\n");
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

