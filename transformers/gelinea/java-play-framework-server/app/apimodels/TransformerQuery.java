package apimodels;

import apimodels.Element;
import apimodels.Property;
import com.fasterxml.jackson.annotation.JsonTypeName;
import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * TransformerQuery
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class TransformerQuery   {
  @JsonProperty("collection")
  @Valid

  private List<Element> collection = null;

  @JsonProperty("controls")
  @NotNull
@Valid

  private List<Property> controls = new ArrayList<>();

  public TransformerQuery collection(List<Element> collection) {
    this.collection = collection;
    return this;
  }

  public TransformerQuery addCollectionItem(Element collectionItem) {
    if (collection == null) {
      collection = new ArrayList<>();
    }
    collection.add(collectionItem);
    return this;
  }

   /**
   * List of elements that will be transformed. Required for all transformers except producers.
   * @return collection
  **/
  public List<Element> getCollection() {
    return collection;
  }

  public void setCollection(List<Element> collection) {
    this.collection = collection;
  }

  public TransformerQuery controls(List<Property> controls) {
    this.controls = controls;
    return this;
  }

  public TransformerQuery addControlsItem(Property controlsItem) {
    controls.add(controlsItem);
    return this;
  }

   /**
   * Values that control the behavior of the transformer. Names of the controls must match the names specified in the transformer's definition and values must match types (and possibly  allowed_values) specified in the transformer's definition.
   * @return controls
  **/
  public List<Property> getControls() {
    return controls;
  }

  public void setControls(List<Property> controls) {
    this.controls = controls;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    TransformerQuery transformerQuery = (TransformerQuery) o;
    return Objects.equals(collection, transformerQuery.collection) &&
        Objects.equals(controls, transformerQuery.controls);
  }

  @Override
  public int hashCode() {
    return Objects.hash(collection, controls);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class TransformerQuery {\n");
    
    sb.append("    collection: ").append(toIndentedString(collection)).append("\n");
    sb.append("    controls: ").append(toIndentedString(controls)).append("\n");
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

