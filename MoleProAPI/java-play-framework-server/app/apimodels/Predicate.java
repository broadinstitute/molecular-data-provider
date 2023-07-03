package apimodels;

import apimodels.KmAttribute;
import apimodels.KmQualifier;
import com.fasterxml.jackson.annotation.JsonTypeName;
import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * Predicate describing relationship between a subject and an object.
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class Predicate   {
  @JsonProperty("subject")
  @NotNull

  private String subject;

  @JsonProperty("predicate")
  @NotNull

  private String predicate;

  @JsonProperty("inverse_predicate")
  @NotNull

  private String inversePredicate;

  @JsonProperty("object")
  @NotNull

  private String _object;

  @JsonProperty("source")
  
  private String source;

  @JsonProperty("relations")
  
  private List<String> relations = null;

  @JsonProperty("inverse_relations")
  
  private List<String> inverseRelations = null;

  @JsonProperty("count")
  
  private Integer count;

  @JsonProperty("knowledge_level")
  
  private String knowledgeLevel;

  @JsonProperty("agent_type")
  
  private String agentType;

  @JsonProperty("qualifiers")
  @Valid

  private List<KmQualifier> qualifiers = null;

  @JsonProperty("attributes")
  @Valid

  private List<KmAttribute> attributes = null;

  public Predicate subject(String subject) {
    this.subject = subject;
    return this;
  }

   /**
   * Get subject
   * @return subject
  **/
  public String getSubject() {
    return subject;
  }

  public void setSubject(String subject) {
    this.subject = subject;
  }

  public Predicate predicate(String predicate) {
    this.predicate = predicate;
    return this;
  }

   /**
   * Get predicate
   * @return predicate
  **/
  public String getPredicate() {
    return predicate;
  }

  public void setPredicate(String predicate) {
    this.predicate = predicate;
  }

  public Predicate inversePredicate(String inversePredicate) {
    this.inversePredicate = inversePredicate;
    return this;
  }

   /**
   * Get inversePredicate
   * @return inversePredicate
  **/
  public String getInversePredicate() {
    return inversePredicate;
  }

  public void setInversePredicate(String inversePredicate) {
    this.inversePredicate = inversePredicate;
  }

  public Predicate _object(String _object) {
    this._object = _object;
    return this;
  }

   /**
   * Get _object
   * @return _object
  **/
  public String getObject() {
    return _object;
  }

  public void setObject(String _object) {
    this._object = _object;
  }

  public Predicate source(String source) {
    this.source = source;
    return this;
  }

   /**
   * Source of the relationship.
   * @return source
  **/
  public String getSource() {
    return source;
  }

  public void setSource(String source) {
    this.source = source;
  }

  public Predicate relations(List<String> relations) {
    this.relations = relations;
    return this;
  }

  public Predicate addRelationsItem(String relationsItem) {
    if (relations == null) {
      relations = new ArrayList<>();
    }
    relations.add(relationsItem);
    return this;
  }

   /**
   * Low-level relations from the underlying source.
   * @return relations
  **/
  public List<String> getRelations() {
    return relations;
  }

  public void setRelations(List<String> relations) {
    this.relations = relations;
  }

  public Predicate inverseRelations(List<String> inverseRelations) {
    this.inverseRelations = inverseRelations;
    return this;
  }

  public Predicate addInverseRelationsItem(String inverseRelationsItem) {
    if (inverseRelations == null) {
      inverseRelations = new ArrayList<>();
    }
    inverseRelations.add(inverseRelationsItem);
    return this;
  }

   /**
   * Inverse low-level relations from the underlying source.
   * @return inverseRelations
  **/
  public List<String> getInverseRelations() {
    return inverseRelations;
  }

  public void setInverseRelations(List<String> inverseRelations) {
    this.inverseRelations = inverseRelations;
  }

  public Predicate count(Integer count) {
    this.count = count;
    return this;
  }

   /**
   * Number of edge instances known to this knowledge source
   * @return count
  **/
  public Integer getCount() {
    return count;
  }

  public void setCount(Integer count) {
    this.count = count;
  }

  public Predicate knowledgeLevel(String knowledgeLevel) {
    this.knowledgeLevel = knowledgeLevel;
    return this;
  }

   /**
   * the level/type of knowledge that is reported in an edge,  based on how the knowledge was produced, the strength of  evidence supporting it, or our confidence in its validity.  (e.g. ‘knowledge assertion’, ‘logical entailment, ‘prediction’, ‘statistical association’, etc.)
   * @return knowledgeLevel
  **/
  public String getKnowledgeLevel() {
    return knowledgeLevel;
  }

  public void setKnowledgeLevel(String knowledgeLevel) {
    this.knowledgeLevel = knowledgeLevel;
  }

  public Predicate agentType(String agentType) {
    this.agentType = agentType;
    return this;
  }

   /**
   * the type of agent that generated the statement expressed in an edge  (e.g. 'manual agent', 'automated agent', 'computational model',  'text-mining agent', etc.)
   * @return agentType
  **/
  public String getAgentType() {
    return agentType;
  }

  public void setAgentType(String agentType) {
    this.agentType = agentType;
  }

  public Predicate qualifiers(List<KmQualifier> qualifiers) {
    this.qualifiers = qualifiers;
    return this;
  }

  public Predicate addQualifiersItem(KmQualifier qualifiersItem) {
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
  public List<KmQualifier> getQualifiers() {
    return qualifiers;
  }

  public void setQualifiers(List<KmQualifier> qualifiers) {
    this.qualifiers = qualifiers;
  }

  public Predicate attributes(List<KmAttribute> attributes) {
    this.attributes = attributes;
    return this;
  }

  public Predicate addAttributesItem(KmAttribute attributesItem) {
    if (attributes == null) {
      attributes = new ArrayList<>();
    }
    attributes.add(attributesItem);
    return this;
  }

   /**
   * Get attributes
   * @return attributes
  **/
  public List<KmAttribute> getAttributes() {
    return attributes;
  }

  public void setAttributes(List<KmAttribute> attributes) {
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
    Predicate predicate = (Predicate) o;
    return Objects.equals(subject, predicate.subject) &&
        Objects.equals(predicate, predicate.predicate) &&
        Objects.equals(inversePredicate, predicate.inversePredicate) &&
        Objects.equals(_object, predicate._object) &&
        Objects.equals(source, predicate.source) &&
        Objects.equals(relations, predicate.relations) &&
        Objects.equals(inverseRelations, predicate.inverseRelations) &&
        Objects.equals(count, predicate.count) &&
        Objects.equals(knowledgeLevel, predicate.knowledgeLevel) &&
        Objects.equals(agentType, predicate.agentType) &&
        Objects.equals(qualifiers, predicate.qualifiers) &&
        Objects.equals(attributes, predicate.attributes);
  }

  @Override
  public int hashCode() {
    return Objects.hash(subject, predicate, inversePredicate, _object, source, relations, inverseRelations, count, knowledgeLevel, agentType, qualifiers, attributes);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class Predicate {\n");
    
    sb.append("    subject: ").append(toIndentedString(subject)).append("\n");
    sb.append("    predicate: ").append(toIndentedString(predicate)).append("\n");
    sb.append("    inversePredicate: ").append(toIndentedString(inversePredicate)).append("\n");
    sb.append("    _object: ").append(toIndentedString(_object)).append("\n");
    sb.append("    source: ").append(toIndentedString(source)).append("\n");
    sb.append("    relations: ").append(toIndentedString(relations)).append("\n");
    sb.append("    inverseRelations: ").append(toIndentedString(inverseRelations)).append("\n");
    sb.append("    count: ").append(toIndentedString(count)).append("\n");
    sb.append("    knowledgeLevel: ").append(toIndentedString(knowledgeLevel)).append("\n");
    sb.append("    agentType: ").append(toIndentedString(agentType)).append("\n");
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

