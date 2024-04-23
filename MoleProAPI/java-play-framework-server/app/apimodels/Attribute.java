package apimodels;

import com.fasterxml.jackson.annotation.JsonTypeName;
import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * Generic attribute for a node or an edge that expands the key-value pair concept by including fields for additional metadata. These fields can be used to describe the source of the statement made in key-value pair of the attribute object, or describe the attribute&#39;s value itself including its semantic type, or a url providing additional information about it.
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class Attribute   {
  @JsonProperty("attribute_type_id")
  @NotNull

  private String attributeTypeId;

  @JsonProperty("original_attribute_name")
  @NotNull

  private String originalAttributeName;

  @JsonProperty("value")
  @NotNull

  private Object value = null;

  @JsonProperty("value_type_id")
  
  private String valueTypeId;

  @JsonProperty("attribute_source")
  @NotNull

  private String attributeSource;

  @JsonProperty("value_url")
  
  private String valueUrl;

  @JsonProperty("description")
  
  private String description;

  @JsonProperty("attributes")
  @Valid

  private List<Attribute> attributes = null;

  @JsonProperty("provided_by")
  
  private String providedBy;

  public Attribute attributeTypeId(String attributeTypeId) {
    this.attributeTypeId = attributeTypeId;
    return this;
  }

   /**
   * The 'key' of the attribute object, holding a CURIE of an ontology property defining the attribute (preferably the CURIE of a Biolink association slot). This property captures the relationship asserted to hold between the value of the attribute, and the node or edge from  which it hangs. For example, that a value of '0.000153' represents a p-value supporting an edge, or that a value of 'ChEMBL' represents the original source of the knowledge expressed in the edge.
   * @return attributeTypeId
  **/
  public String getAttributeTypeId() {
    return attributeTypeId;
  }

  public void setAttributeTypeId(String attributeTypeId) {
    this.attributeTypeId = attributeTypeId;
  }

  public void setType(String type) {
    this.attributeTypeId = type;
  }

  public Attribute originalAttributeName(String originalAttributeName) {
    this.originalAttributeName = originalAttributeName;
    return this;
  }

   /**
   * The term used by the original source of an attribute to describe the meaning or significance of the value it captures. This may be a column name in a source tsv file, or a key in a source json document for the field in the data that held the attribute's value. Capturing this information  where possible lets us preserve what the original source said. Note that the data type is string' but the contents of the field could also be a CURIE of a third party ontology term.
   * @return originalAttributeName
  **/
  public String getOriginalAttributeName() {
    return originalAttributeName;
  }

  public void setOriginalAttributeName(String originalAttributeName) {
    this.originalAttributeName = originalAttributeName;
  }

  public void setName(String name) {
    this.originalAttributeName = name;
  }

  public Attribute value(Object value) {
    this.value = value;
    return this;
  }

   /**
   * Value of the attribute. May be any data type, including a list.
   * @return value
  **/
  public Object getValue() {
    return value;
  }

  public void setValue(Object value) {
    this.value = value;
  }

  public Attribute valueTypeId(String valueTypeId) {
    this.valueTypeId = valueTypeId;
    return this;
  }

   /**
   * CURIE describing the semantic type of an  attribute's value. Use a Biolink class if possible, otherwise a term from an external ontology. If a suitable CURIE/identifier does not exist, enter a descriptive phrase here and submit the new type for consideration by the appropriate authority.
   * @return valueTypeId
  **/
  public String getValueTypeId() {
    return valueTypeId;
  }

  public void setValueTypeId(String valueTypeId) {
    this.valueTypeId = valueTypeId;
  }

  public Attribute attributeSource(String attributeSource) {
    this.attributeSource = attributeSource;
    return this;
  }

   /**
   * The source of the core assertion made by the key-value pair of an attribute object. Use a CURIE or namespace designator for this resource where possible.
   * @return attributeSource
  **/
  public String getAttributeSource() {
    return attributeSource;
  }

  public void setAttributeSource(String attributeSource) {
    this.attributeSource = attributeSource;
  }

  public void setSource(String source) {
	this.attributeSource = source;
  }

  public Attribute valueUrl(String valueUrl) {
    this.valueUrl = valueUrl;
    return this;
  }

   /**
   * Human-consumable URL linking to a web document that provides additional information about an  attribute's value (not the node or the edge fom which it hangs).
   * @return valueUrl
  **/
  public String getValueUrl() {
    return valueUrl;
  }

  public void setValueUrl(String valueUrl) {
    this.valueUrl = valueUrl;
  }

  public void setUrl(String url) {
    this.valueUrl = url;
  }
  
  public Attribute description(String description) {
    this.description = description;
    return this;
  }

   /**
   * Human-readable description for the attribute and its value.
   * @return description
  **/
  public String getDescription() {
    return description;
  }

  public void setDescription(String description) {
    this.description = description;
  }

  public Attribute attributes(List<Attribute> attributes) {
    this.attributes = attributes;
    return this;
  }

  public Attribute addAttributesItem(Attribute attributesItem) {
    if (attributes == null) {
      attributes = new ArrayList<>();
    }
    attributes.add(attributesItem);
    return this;
  }

   /**
   * A list of attributes providing further information about the parent attribute. 
   * @return attributes
  **/
  public List<Attribute> getAttributes() {
    return attributes;
  }

  public void setAttributes(List<Attribute> attributes) {
    this.attributes = attributes;
  }

  public Attribute providedBy(String providedBy) {
    this.providedBy = providedBy;
    return this;
  }

   /**
   * Transformer that produced the attribute's value.
   * @return providedBy
  **/
  public String getProvidedBy() {
    return providedBy;
  }

  public void setProvidedBy(String providedBy) {
    this.providedBy = providedBy;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    Attribute attribute = (Attribute) o;
    return Objects.equals(attributeTypeId, attribute.attributeTypeId) &&
        Objects.equals(originalAttributeName, attribute.originalAttributeName) &&
        Objects.equals(value, attribute.value) &&
        Objects.equals(valueTypeId, attribute.valueTypeId) &&
        Objects.equals(attributeSource, attribute.attributeSource) &&
        Objects.equals(valueUrl, attribute.valueUrl) &&
        Objects.equals(description, attribute.description) &&
        Objects.equals(attributes, attribute.attributes) &&
        Objects.equals(providedBy, attribute.providedBy);
  }

  @Override
  public int hashCode() {
    return Objects.hash(attributeTypeId, originalAttributeName, value, valueTypeId, attributeSource, valueUrl, description, attributes, providedBy);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class Attribute {\n");
    
    sb.append("    attributeTypeId: ").append(toIndentedString(attributeTypeId)).append("\n");
    sb.append("    originalAttributeName: ").append(toIndentedString(originalAttributeName)).append("\n");
    sb.append("    value: ").append(toIndentedString(value)).append("\n");
    sb.append("    valueTypeId: ").append(toIndentedString(valueTypeId)).append("\n");
    sb.append("    attributeSource: ").append(toIndentedString(attributeSource)).append("\n");
    sb.append("    valueUrl: ").append(toIndentedString(valueUrl)).append("\n");
    sb.append("    description: ").append(toIndentedString(description)).append("\n");
    sb.append("    attributes: ").append(toIndentedString(attributes)).append("\n");
    sb.append("    providedBy: ").append(toIndentedString(providedBy)).append("\n");
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

