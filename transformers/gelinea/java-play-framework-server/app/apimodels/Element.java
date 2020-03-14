package apimodels;

import apimodels.Attribute;
import apimodels.Names;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * Element
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen", date = "2020-02-27T16:03:08.782-05:00[America/New_York]")

@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class Element   {
  @JsonProperty("id")
  private String id;

  @JsonProperty("biolink_class")
  private String biolinkClass;

  @JsonProperty("identifiers")
  private Map<String, Object> identifiers = null;

  @JsonProperty("names_synonyms")
  private List<Names> namesSynonyms = null;

  @JsonProperty("attributes")
  private List<Attribute> attributes = null;

  @JsonProperty("source")
  private String source;

  public Element id(String id) {
    this.id = id;
    return this;
  }

   /**
   * Id of the gene.
   * @return id
  **/
  @NotNull
  public String getId() {
    return id;
  }

  public void setId(String id) {
    this.id = id;
  }

  public Element biolinkClass(String biolinkClass) {
    this.biolinkClass = biolinkClass;
    return this;
  }

   /**
   * BioLink class of the element.
   * @return biolinkClass
  **/
    public String getBiolinkClass() {
    return biolinkClass;
  }

  public void setBiolinkClass(String biolinkClass) {
    this.biolinkClass = biolinkClass;
  }

  public Element identifiers(Map<String, Object> identifiers) {
    this.identifiers = identifiers;
    return this;
  }

  public Element putIdentifiersItem(String key, Object identifiersItem) {
    if (this.identifiers == null) {
      this.identifiers = new HashMap<>();
    }
    this.identifiers.put(key, identifiersItem);
    return this;
  }

   /**
   * Get identifiers
   * @return identifiers
  **/
    public Map<String, Object> getIdentifiers() {
    return identifiers;
  }

  public void setIdentifiers(Map<String, Object> identifiers) {
    this.identifiers = identifiers;
  }

  public Element namesSynonyms(List<Names> namesSynonyms) {
    this.namesSynonyms = namesSynonyms;
    return this;
  }

  public Element addNamesSynonymsItem(Names namesSynonymsItem) {
    if (namesSynonyms == null) {
      namesSynonyms = new ArrayList<>();
    }
    namesSynonyms.add(namesSynonymsItem);
    return this;
  }

   /**
   * Names and synonyms of the element.
   * @return namesSynonyms
  **/
  @Valid
  public List<Names> getNamesSynonyms() {
    return namesSynonyms;
  }

  public void setNamesSynonyms(List<Names> namesSynonyms) {
    this.namesSynonyms = namesSynonyms;
  }

  public Element attributes(List<Attribute> attributes) {
    this.attributes = attributes;
    return this;
  }

  public Element addAttributesItem(Attribute attributesItem) {
    if (attributes == null) {
      attributes = new ArrayList<>();
    }
    attributes.add(attributesItem);
    return this;
  }

   /**
   * Additional information about the element and provenance about collection membership.
   * @return attributes
  **/
  @Valid
  public List<Attribute> getAttributes() {
    return attributes;
  }

  public void setAttributes(List<Attribute> attributes) {
    this.attributes = attributes;
  }

  public Element source(String source) {
    this.source = source;
    return this;
  }

   /**
   * Name of a transformer that added the element to the collection.
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
    Element element = (Element) o;
    return Objects.equals(id, element.id) &&
        Objects.equals(biolinkClass, element.biolinkClass) &&
        Objects.equals(identifiers, element.identifiers) &&
        Objects.equals(namesSynonyms, element.namesSynonyms) &&
        Objects.equals(attributes, element.attributes) &&
        Objects.equals(source, element.source);
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, biolinkClass, identifiers, namesSynonyms, attributes, source);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class Element {\n");
    
    sb.append("    id: ").append(toIndentedString(id)).append("\n");
    sb.append("    biolinkClass: ").append(toIndentedString(biolinkClass)).append("\n");
    sb.append("    identifiers: ").append(toIndentedString(identifiers)).append("\n");
    sb.append("    namesSynonyms: ").append(toIndentedString(namesSynonyms)).append("\n");
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

