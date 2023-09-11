package apimodels;

import apimodels.KmAttribute;
import com.fasterxml.jackson.annotation.JsonTypeName;
import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * Description of semantic types provided by this knowledge source.
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class Node   {
  @JsonProperty("id_prefixes")
  @NotNull

  private List<String> idPrefixes = new ArrayList<>();

  @JsonProperty("count")
  
  private Integer count;

  @JsonProperty("attributes")
  @Valid

  private List<KmAttribute> attributes = null;

  public Node idPrefixes(List<String> idPrefixes) {
    this.idPrefixes = idPrefixes;
    return this;
  }

  public Node addIdPrefixesItem(String idPrefixesItem) {
    idPrefixes.add(idPrefixesItem);
    return this;
  }

   /**
   * List of CURIE prefixes that this knowledge source understands and accepts on the input.
   * @return idPrefixes
  **/
  public List<String> getIdPrefixes() {
    return idPrefixes;
  }

  public void setIdPrefixes(List<String> idPrefixes) {
    this.idPrefixes = idPrefixes;
  }

  public Node count(Integer count) {
    this.count = count;
    return this;
  }

   /**
   * Number of node instances known to this knowledge source
   * @return count
  **/
  public Integer getCount() {
    return count;
  }

  public void setCount(Integer count) {
    this.count = count;
  }

  public Node attributes(List<KmAttribute> attributes) {
    this.attributes = attributes;
    return this;
  }

  public Node addAttributesItem(KmAttribute attributesItem) {
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
    Node node = (Node) o;
    return Objects.equals(idPrefixes, node.idPrefixes) &&
        Objects.equals(count, node.count) &&
        Objects.equals(attributes, node.attributes);
  }

  @Override
  public int hashCode() {
    return Objects.hash(idPrefixes, count, attributes);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class Node {\n");
    
    sb.append("    idPrefixes: ").append(toIndentedString(idPrefixes)).append("\n");
    sb.append("    count: ").append(toIndentedString(count)).append("\n");
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

