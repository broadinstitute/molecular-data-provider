package apimodels;

import apimodels.Attribute;
import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * Connection
 */

@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class Connection   {
  @JsonProperty("source_element_id")
  private String sourceElementId;

  @JsonProperty("type")
  private String type;

  @JsonProperty("evidence_type")
  private String evidenceType;

  @JsonProperty("attributes")
  private List<Attribute> attributes = null;

  public Connection sourceElementId(String sourceElementId) {
    this.sourceElementId = sourceElementId;
    return this;
  }

   /**
   * id (CURIE) of the connected query node
   * @return sourceElementId
  **/
    public String getSourceElementId() {
    return sourceElementId;
  }

  public void setSourceElementId(String sourceElementId) {
    this.sourceElementId = sourceElementId;
  }

  public Connection type(String type) {
    this.type = type;
    return this;
  }

   /**
   * Biolink predicate
   * @return type
  **/
    public String getType() {
    return type;
  }

  public void setType(String type) {
    this.type = type;
  }

  public Connection evidenceType(String evidenceType) {
    this.evidenceType = evidenceType;
    return this;
  }

   /**
   * evidence supporting the statement from the ECO ontology
   * @return evidenceType
  **/
    public String getEvidenceType() {
    return evidenceType;
  }

  public void setEvidenceType(String evidenceType) {
    this.evidenceType = evidenceType;
  }

  public Connection attributes(List<Attribute> attributes) {
    this.attributes = attributes;
    return this;
  }

  public Connection addAttributesItem(Attribute attributesItem) {
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


  @Override
  public boolean equals(java.lang.Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    Connection connection = (Connection) o;
    return Objects.equals(sourceElementId, connection.sourceElementId) &&
        Objects.equals(type, connection.type) &&
        Objects.equals(evidenceType, connection.evidenceType) &&
        Objects.equals(attributes, connection.attributes);
  }

  @Override
  public int hashCode() {
    return Objects.hash(sourceElementId, type, evidenceType, attributes);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class Connection {\n");
    
    sb.append("    sourceElementId: ").append(toIndentedString(sourceElementId)).append("\n");
    sb.append("    type: ").append(toIndentedString(type)).append("\n");
    sb.append("    evidenceType: ").append(toIndentedString(evidenceType)).append("\n");
    sb.append("    attributes: ").append(toIndentedString(attributes)).append("\n");
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

