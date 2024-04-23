package apimodels;

import apimodels.Attribute;
import apimodels.Qualifier;
import com.fasterxml.jackson.annotation.JsonTypeName;
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
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class Connection   {
  @JsonProperty("uuid")
  
  private String uuid;

  @JsonProperty("source_element_id")
  @NotNull

  private String sourceElementId;

  @JsonProperty("biolink_predicate")
  @NotNull

  private String biolinkPredicate;

  @JsonProperty("inverse_predicate")
  @NotNull

  private String inversePredicate;

  @JsonProperty("relation")
  
  private String relation;

  @JsonProperty("inverse_relation")
  
  private String inverseRelation;

  @JsonProperty("source")
  @NotNull

  private String source;

  @JsonProperty("provided_by")
  @NotNull

  private String providedBy;

  @JsonProperty("qualifiers")
  @Valid

  private List<Qualifier> qualifiers = null;

  @JsonProperty("attributes")
  @Valid

  private List<Attribute> attributes = null;

  public Connection uuid(String uuid) {
    this.uuid = uuid;
    return this;
  }

   /**
   * UUID of the connection.
   * @return uuid
  **/
  public String getUuid() {
    return uuid;
  }

  public void setUuid(String uuid) {
    this.uuid = uuid;
  }

  public Connection sourceElementId(String sourceElementId) {
    this.sourceElementId = sourceElementId;
    return this;
  }

   /**
   * Id (CURIE) of the connected query node.
   * @return sourceElementId
  **/
  public String getSourceElementId() {
    return sourceElementId;
  }

  public void setSourceElementId(String sourceElementId) {
    this.sourceElementId = sourceElementId;
  }

  public Connection biolinkPredicate(String biolinkPredicate) {
    this.biolinkPredicate = biolinkPredicate;
    return this;
  }

   /**
   * Biolink predicate.
   * @return biolinkPredicate
  **/
  public String getBiolinkPredicate() {
    return biolinkPredicate;
  }

  public void setBiolinkPredicate(String biolinkPredicate) {
    this.biolinkPredicate = biolinkPredicate;
  }

  public void setType(String type) {
	  this.biolinkPredicate = type;
  }

  public Connection inversePredicate(String inversePredicate) {
    this.inversePredicate = inversePredicate;
    return this;
  }

   /**
   * Inverse Biolink predicate.
   * @return inversePredicate
  **/
  public String getInversePredicate() {
    return inversePredicate;
  }

  public void setInversePredicate(String inversePredicate) {
    this.inversePredicate = inversePredicate;
  }

  public Connection relation(String relation) {
    this.relation = relation;
    return this;
  }

   /**
   * Lower-level relationship type of this connection.
   * @return relation
  **/
  public String getRelation() {
    return relation;
  }

  public void setRelation(String relation) {
    this.relation = relation;
  }

  public Connection inverseRelation(String inverseRelation) {
    this.inverseRelation = inverseRelation;
    return this;
  }

   /**
   * Inverse lower-level relationship type of this connection.
   * @return inverseRelation
  **/
  public String getInverseRelation() {
    return inverseRelation;
  }

  public void setInverseRelation(String inverseRelation) {
    this.inverseRelation = inverseRelation;
  }

  public Connection source(String source) {
    this.source = source;
    return this;
  }

   /**
   * Source of the connection, as a CURIE prefix.
   * @return source
  **/
  public String getSource() {
    return source;
  }

  public void setSource(String source) {
    this.source = source;
  }

  public Connection providedBy(String providedBy) {
    this.providedBy = providedBy;
    return this;
  }

   /**
   * Transformer that produced the connection.
   * @return providedBy
  **/
  public String getProvidedBy() {
    return providedBy;
  }

  public void setProvidedBy(String providedBy) {
    this.providedBy = providedBy;
  }

  public Connection qualifiers(List<Qualifier> qualifiers) {
    this.qualifiers = qualifiers;
    return this;
  }

  public Connection addQualifiersItem(Qualifier qualifiersItem) {
    if (qualifiers == null) {
      qualifiers = new ArrayList<>();
    }
    qualifiers.add(qualifiersItem);
    return this;
  }

   /**
   * An additional nuance attached to the connection.
   * @return qualifiers
  **/
  public List<Qualifier> getQualifiers() {
    return qualifiers;
  }

  public void setQualifiers(List<Qualifier> qualifiers) {
    this.qualifiers = qualifiers;
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
   * Additional information and provenance about the connection.
   * @return attributes
  **/
  public List<Attribute> getAttributes() {
    return attributes;
  }

  public void setAttributes(List<Attribute> attributes) {
    this.attributes = attributes;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    Connection connection = (Connection) o;
    return Objects.equals(uuid, connection.uuid) &&
        Objects.equals(sourceElementId, connection.sourceElementId) &&
        Objects.equals(biolinkPredicate, connection.biolinkPredicate) &&
        Objects.equals(inversePredicate, connection.inversePredicate) &&
        Objects.equals(relation, connection.relation) &&
        Objects.equals(inverseRelation, connection.inverseRelation) &&
        Objects.equals(source, connection.source) &&
        Objects.equals(providedBy, connection.providedBy) &&
        Objects.equals(qualifiers, connection.qualifiers) &&
        Objects.equals(attributes, connection.attributes);
  }

  @Override
  public int hashCode() {
    return Objects.hash(uuid, sourceElementId, biolinkPredicate, inversePredicate, relation, inverseRelation, source, providedBy, qualifiers, attributes);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class Connection {\n");
    
    sb.append("    uuid: ").append(toIndentedString(uuid)).append("\n");
    sb.append("    sourceElementId: ").append(toIndentedString(sourceElementId)).append("\n");
    sb.append("    biolinkPredicate: ").append(toIndentedString(biolinkPredicate)).append("\n");
    sb.append("    inversePredicate: ").append(toIndentedString(inversePredicate)).append("\n");
    sb.append("    relation: ").append(toIndentedString(relation)).append("\n");
    sb.append("    inverseRelation: ").append(toIndentedString(inverseRelation)).append("\n");
    sb.append("    source: ").append(toIndentedString(source)).append("\n");
    sb.append("    providedBy: ").append(toIndentedString(providedBy)).append("\n");
    sb.append("    qualifiers: ").append(toIndentedString(qualifiers)).append("\n");
    sb.append("    attributes: ").append(toIndentedString(attributes)).append("\n");
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

