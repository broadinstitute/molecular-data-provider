package apimodels;

import apimodels.Node;
import apimodels.Predicate;
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
 * Knowledge-graph representation of the transformer.
 */

@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class KnowledgeMap   {
  @JsonProperty("input_class")
  private String inputClass;

  @JsonProperty("output_class")
  private String outputClass;

  @JsonProperty("nodes")
  private Map<String, Node> nodes = null;

  @JsonProperty("predicates")
  private List<Predicate> predicates = null;

  public KnowledgeMap inputClass(String inputClass) {
    this.inputClass = inputClass;
    return this;
  }

   /**
   * BioLink class for the members of the input list.
   * @return inputClass
  **/
    public String getInputClass() {
    return inputClass;
  }

  public void setInputClass(String inputClass) {
    this.inputClass = inputClass;
  }

  public KnowledgeMap outputClass(String outputClass) {
    this.outputClass = outputClass;
    return this;
  }

   /**
   * BioLink class for the members of the output list.
   * @return outputClass
  **/
    public String getOutputClass() {
    return outputClass;
  }

  public void setOutputClass(String outputClass) {
    this.outputClass = outputClass;
  }

  public KnowledgeMap nodes(Map<String, Node> nodes) {
    this.nodes = nodes;
    return this;
  }

  public KnowledgeMap putNodesItem(String key, Node nodesItem) {
    if (this.nodes == null) {
      this.nodes = new HashMap<>();
    }
    this.nodes.put(key, nodesItem);
    return this;
  }

   /**
   * List of semantic types in the KnowledgeMap.
   * @return nodes
  **/
  @Valid
  public Map<String, Node> getNodes() {
    return nodes;
  }

  public void setNodes(Map<String, Node> nodes) {
    this.nodes = nodes;
  }

  public KnowledgeMap predicates(List<Predicate> predicates) {
    this.predicates = predicates;
    return this;
  }

  public KnowledgeMap addPredicatesItem(Predicate predicatesItem) {
    if (predicates == null) {
      predicates = new ArrayList<>();
    }
    predicates.add(predicatesItem);
    return this;
  }

   /**
   * Predicates describing relationships between subjects and objects.
   * @return predicates
  **/
  @Valid
  public List<Predicate> getPredicates() {
    return predicates;
  }

  public void setPredicates(List<Predicate> predicates) {
    this.predicates = predicates;
  }


  @Override
  public boolean equals(java.lang.Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    KnowledgeMap knowledgeMap = (KnowledgeMap) o;
    return Objects.equals(inputClass, knowledgeMap.inputClass) &&
        Objects.equals(outputClass, knowledgeMap.outputClass) &&
        Objects.equals(nodes, knowledgeMap.nodes) &&
        Objects.equals(predicates, knowledgeMap.predicates);
  }

  @Override
  public int hashCode() {
    return Objects.hash(inputClass, outputClass, nodes, predicates);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class KnowledgeMap {\n");
    
    sb.append("    inputClass: ").append(toIndentedString(inputClass)).append("\n");
    sb.append("    outputClass: ").append(toIndentedString(outputClass)).append("\n");
    sb.append("    nodes: ").append(toIndentedString(nodes)).append("\n");
    sb.append("    predicates: ").append(toIndentedString(predicates)).append("\n");
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

