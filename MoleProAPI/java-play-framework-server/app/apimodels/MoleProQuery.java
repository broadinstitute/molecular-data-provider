package apimodels;

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
 * MoleProQuery
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class MoleProQuery   {
  @JsonProperty("name")
  @NotNull

  private String name;

  @JsonProperty("collection_id")
  
  private String collectionId;

  @JsonProperty("controls")
  @NotNull
@Valid

  private List<Property> controls = new ArrayList<>();

  public MoleProQuery name(String name) {
    this.name = name;
    return this;
  }

   /**
   * Name of the transformer that will be executed.
   * @return name
  **/
  public String getName() {
    return name;
  }

  public void setName(String name) {
    this.name = name;
  }

  public MoleProQuery collectionId(String collectionId) {
    this.collectionId = collectionId;
    return this;
  }

   /**
   * Id of the gene list that will be transformed. Required for all transformers except producers.
   * @return collectionId
  **/
  public String getCollectionId() {
    return collectionId;
  }

  public void setCollectionId(String collectionId) {
    this.collectionId = collectionId;
  }

  public MoleProQuery controls(List<Property> controls) {
    this.controls = controls;
    return this;
  }

  public MoleProQuery addControlsItem(Property controlsItem) {
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
    MoleProQuery moleProQuery = (MoleProQuery) o;
    return Objects.equals(name, moleProQuery.name) &&
        Objects.equals(collectionId, moleProQuery.collectionId) &&
        Objects.equals(controls, moleProQuery.controls);
  }

  @Override
  public int hashCode() {
    return Objects.hash(name, collectionId, controls);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class MoleProQuery {\n");
    
    sb.append("    name: ").append(toIndentedString(name)).append("\n");
    sb.append("    collectionId: ").append(toIndentedString(collectionId)).append("\n");
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

