package apimodels;

import apimodels.Node;
import apimodels.Predicate;
import com.fasterxml.jackson.annotation.JsonTypeName;
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
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class KnowledgeMap   {
  @JsonProperty("input_class")
  @NotNull

  private String inputClass;

  @JsonProperty("output_class")
  @NotNull

  private String outputClass;

  @JsonProperty("nodes")
  @Valid

  private Map<String, Node> nodes = null;

  @JsonProperty("edges")
  @Valid

  private List<Predicate> edges = null;

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
  public Map<String, Node> getNodes() {
    return nodes;
  }

  public void setNodes(Map<String, Node> nodes) {
    this.nodes = nodes;
  }

  public KnowledgeMap edges(List<Predicate> edges) {
    this.edges = edges;
    return this;
  }

  public KnowledgeMap addEdgesItem(Predicate edgesItem) {
    if (edges == null) {
      edges = new ArrayList<>();
    }
    edges.add(edgesItem);
    return this;
  }

   /**
   * Predicates describing relationships between subjects and objects.
   * @return edges
  **/
  public List<Predicate> getEdges() {
    return edges;
  }

  public void setEdges(List<Predicate> edges) {
    this.edges = edges;
  }


  @Override
  public boolean equals(Object o) {
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
        Objects.equals(edges, knowledgeMap.edges);
  }

  @Override
  public int hashCode() {
    return Objects.hash(inputClass, outputClass, nodes, edges);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class KnowledgeMap {\n");
    
    sb.append("    inputClass: ").append(toIndentedString(inputClass)).append("\n");
    sb.append("    outputClass: ").append(toIndentedString(outputClass)).append("\n");
    sb.append("    nodes: ").append(toIndentedString(nodes)).append("\n");
    sb.append("    edges: ").append(toIndentedString(edges)).append("\n");
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

