package apimodels;

import apimodels.Attribute;
import apimodels.GeneInfoIdentifiers;
import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * GeneInfo
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen", date = "2020-02-27T16:03:08.782-05:00[America/New_York]")

@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class GeneInfo   {
  @JsonProperty("gene_id")
  private String geneId;

  @JsonProperty("identifiers")
  private GeneInfoIdentifiers identifiers;

  @JsonProperty("attributes")
  private List<Attribute> attributes = null;

  @JsonProperty("source")
  private String source;

  public GeneInfo geneId(String geneId) {
    this.geneId = geneId;
    return this;
  }

   /**
   * Id of the gene. Preferably HGNC id; can be Entrez or ENSEMBL id if HGNC id is not available.
   * @return geneId
  **/
  @NotNull
  public String getGeneId() {
    return geneId;
  }

  public void setGeneId(String geneId) {
    this.geneId = geneId;
  }

  public GeneInfo identifiers(GeneInfoIdentifiers identifiers) {
    this.identifiers = identifiers;
    return this;
  }

   /**
   * Get identifiers
   * @return identifiers
  **/
  @Valid
  public GeneInfoIdentifiers getIdentifiers() {
    return identifiers;
  }

  public void setIdentifiers(GeneInfoIdentifiers identifiers) {
    this.identifiers = identifiers;
  }

  public GeneInfo attributes(List<Attribute> attributes) {
    this.attributes = attributes;
    return this;
  }

  public GeneInfo addAttributesItem(Attribute attributesItem) {
    if (attributes == null) {
      attributes = new ArrayList<>();
    }
    attributes.add(attributesItem);
    return this;
  }

   /**
   * Additional information about the gene and provenance about gene-list membership.
   * @return attributes
  **/
  @Valid
  public List<Attribute> getAttributes() {
    return attributes;
  }

  public void setAttributes(List<Attribute> attributes) {
    this.attributes = attributes;
  }

  public GeneInfo source(String source) {
    this.source = source;
    return this;
  }

   /**
   * Name of a transformer that added gene to the gene list.
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
    GeneInfo geneInfo = (GeneInfo) o;
    return Objects.equals(geneId, geneInfo.geneId) &&
        Objects.equals(identifiers, geneInfo.identifiers) &&
        Objects.equals(attributes, geneInfo.attributes) &&
        Objects.equals(source, geneInfo.source);
  }

  @Override
  public int hashCode() {
    return Objects.hash(geneId, identifiers, attributes, source);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class GeneInfo {\n");
    
    sb.append("    geneId: ").append(toIndentedString(geneId)).append("\n");
    sb.append("    identifiers: ").append(toIndentedString(identifiers)).append("\n");
    sb.append("    attributes: ").append(toIndentedString(attributes)).append("\n");
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

