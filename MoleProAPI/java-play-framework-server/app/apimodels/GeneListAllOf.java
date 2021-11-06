package apimodels;

import apimodels.GeneInfo;
import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * GeneListAllOf
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class GeneListAllOf   {
  @JsonProperty("elements")
  @Valid

  private List<GeneInfo> elements = null;

  public GeneListAllOf elements(List<GeneInfo> elements) {
    this.elements = elements;
    return this;
  }

  public GeneListAllOf addElementsItem(GeneInfo elementsItem) {
    if (elements == null) {
      elements = new ArrayList<>();
    }
    elements.add(elementsItem);
    return this;
  }

   /**
   * Members of the gene list.
   * @return elements
  **/
  public List<GeneInfo> getElements() {
    return elements;
  }

  public void setElements(List<GeneInfo> elements) {
    this.elements = elements;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    GeneListAllOf geneListAllOf = (GeneListAllOf) o;
    return Objects.equals(elements, geneListAllOf.elements);
  }

  @Override
  public int hashCode() {
    return Objects.hash(elements);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class GeneListAllOf {\n");
    
    sb.append("    elements: ").append(toIndentedString(elements)).append("\n");
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

