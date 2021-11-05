package apimodels;

import apimodels.Attribute;
import apimodels.CompoundInfoIdentifiers;
import apimodels.CompoundInfoStructure;
import apimodels.Names;
import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * CompoundInfo
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class CompoundInfo   {
  @JsonProperty("compound_id")
  @NotNull

  private String compoundId;

  @JsonProperty("identifiers")
  @Valid

  private CompoundInfoIdentifiers identifiers;

  @JsonProperty("names_synonyms")
  @Valid

  private List<Names> namesSynonyms = null;

  @JsonProperty("structure")
  @Valid

  private CompoundInfoStructure structure;

  @JsonProperty("attributes")
  @Valid

  private List<Attribute> attributes = null;

  @JsonProperty("source")
  
  private String source;

  public CompoundInfo compoundId(String compoundId) {
    this.compoundId = compoundId;
    return this;
  }

   /**
   * Ids of the compound.
   * @return compoundId
  **/
  public String getCompoundId() {
    return compoundId;
  }

  public void setCompoundId(String compoundId) {
    this.compoundId = compoundId;
  }

  public CompoundInfo identifiers(CompoundInfoIdentifiers identifiers) {
    this.identifiers = identifiers;
    return this;
  }

   /**
   * Get identifiers
   * @return identifiers
  **/
  public CompoundInfoIdentifiers getIdentifiers() {
    return identifiers;
  }

  public void setIdentifiers(CompoundInfoIdentifiers identifiers) {
    this.identifiers = identifiers;
  }

  public CompoundInfo namesSynonyms(List<Names> namesSynonyms) {
    this.namesSynonyms = namesSynonyms;
    return this;
  }

  public CompoundInfo addNamesSynonymsItem(Names namesSynonymsItem) {
    if (namesSynonyms == null) {
      namesSynonyms = new ArrayList<>();
    }
    namesSynonyms.add(namesSynonymsItem);
    return this;
  }

   /**
   * Compound names and synonyms.
   * @return namesSynonyms
  **/
  public List<Names> getNamesSynonyms() {
    return namesSynonyms;
  }

  public void setNamesSynonyms(List<Names> namesSynonyms) {
    this.namesSynonyms = namesSynonyms;
  }

  public CompoundInfo structure(CompoundInfoStructure structure) {
    this.structure = structure;
    return this;
  }

   /**
   * Get structure
   * @return structure
  **/
  public CompoundInfoStructure getStructure() {
    return structure;
  }

  public void setStructure(CompoundInfoStructure structure) {
    this.structure = structure;
  }

  public CompoundInfo attributes(List<Attribute> attributes) {
    this.attributes = attributes;
    return this;
  }

  public CompoundInfo addAttributesItem(Attribute attributesItem) {
    if (attributes == null) {
      attributes = new ArrayList<>();
    }
    attributes.add(attributesItem);
    return this;
  }

   /**
   * Additional information about the compound and provenance about compound-list membership.
   * @return attributes
  **/
  public List<Attribute> getAttributes() {
    return attributes;
  }

  public void setAttributes(List<Attribute> attributes) {
    this.attributes = attributes;
  }

  public CompoundInfo source(String source) {
    this.source = source;
    return this;
  }

   /**
   * Name of a transformer that added compound to the compound list.
   * @return source
  **/
  public String getSource() {
    return source;
  }

  public void setSource(String source) {
    this.source = source;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    CompoundInfo compoundInfo = (CompoundInfo) o;
    return Objects.equals(compoundId, compoundInfo.compoundId) &&
        Objects.equals(identifiers, compoundInfo.identifiers) &&
        Objects.equals(namesSynonyms, compoundInfo.namesSynonyms) &&
        Objects.equals(structure, compoundInfo.structure) &&
        Objects.equals(attributes, compoundInfo.attributes) &&
        Objects.equals(source, compoundInfo.source);
  }

  @Override
  public int hashCode() {
    return Objects.hash(compoundId, identifiers, namesSynonyms, structure, attributes, source);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class CompoundInfo {\n");
    
    sb.append("    compoundId: ").append(toIndentedString(compoundId)).append("\n");
    sb.append("    identifiers: ").append(toIndentedString(identifiers)).append("\n");
    sb.append("    namesSynonyms: ").append(toIndentedString(namesSynonyms)).append("\n");
    sb.append("    structure: ").append(toIndentedString(structure)).append("\n");
    sb.append("    attributes: ").append(toIndentedString(attributes)).append("\n");
    sb.append("    source: ").append(toIndentedString(source)).append("\n");
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

