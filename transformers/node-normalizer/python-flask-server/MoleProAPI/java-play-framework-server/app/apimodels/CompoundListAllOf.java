package apimodels;

import apimodels.CompoundInfo;
import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * CompoundListAllOf
 */

@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class CompoundListAllOf   {
  @JsonProperty("elements")
  private List<CompoundInfo> elements = null;

  public CompoundListAllOf elements(List<CompoundInfo> elements) {
    this.elements = elements;
    return this;
  }

  public CompoundListAllOf addElementsItem(CompoundInfo elementsItem) {
    if (elements == null) {
      elements = new ArrayList<>();
    }
    elements.add(elementsItem);
    return this;
  }

   /**
   * Members of the compound list.
   * @return elements
  **/
  @Valid
  public List<CompoundInfo> getElements() {
    return elements;
  }

  public void setElements(List<CompoundInfo> elements) {
    this.elements = elements;
  }


  @Override
  public boolean equals(java.lang.Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    CompoundListAllOf compoundListAllOf = (CompoundListAllOf) o;
    return Objects.equals(elements, compoundListAllOf.elements);
  }

  @Override
  public int hashCode() {
    return Objects.hash(elements);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class CompoundListAllOf {\n");
    
    sb.append("    elements: ").append(toIndentedString(elements)).append("\n");
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

