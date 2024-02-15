package apimodels;

import com.fasterxml.jackson.annotation.JsonTypeName;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * An additional nuance attached to a connection
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class Qualifier   {
  @JsonProperty("qualifier_type_id")
  @NotNull

  private String qualifierTypeId;

  @JsonProperty("qualifier_value")
  @NotNull

  private String qualifierValue;

  public Qualifier qualifierTypeId(String qualifierTypeId) {
    this.qualifierTypeId = qualifierTypeId;
    return this;
  }

   /**
   * The category of the qualifier, drawn from a hierarchy of qualifier slots in the Biolink model (e.g. subject_aspect, subject_direction, object_aspect, object_direction, etc).
   * @return qualifierTypeId
  **/
  public String getQualifierTypeId() {
    return qualifierTypeId;
  }

  public void setQualifierTypeId(String qualifierTypeId) {
    this.qualifierTypeId = qualifierTypeId;
  }

  public Qualifier qualifierValue(String qualifierValue) {
    this.qualifierValue = qualifierValue;
    return this;
  }

   /**
   * The value associated with the type of the qualifier, drawn from a set of controlled values by the type as specified in the Biolink model (e.g. 'expression' or 'abundance' for the qualifier type 'subject_aspect', etc).
   * @return qualifierValue
  **/
  public String getQualifierValue() {
    return qualifierValue;
  }

  public void setQualifierValue(String qualifierValue) {
    this.qualifierValue = qualifierValue;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    Qualifier qualifier = (Qualifier) o;
    return Objects.equals(qualifierTypeId, qualifier.qualifierTypeId) &&
        Objects.equals(qualifierValue, qualifier.qualifierValue);
  }

  @Override
  public int hashCode() {
    return Objects.hash(qualifierTypeId, qualifierValue);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class Qualifier {\n");
    
    sb.append("    qualifierTypeId: ").append(toIndentedString(qualifierTypeId)).append("\n");
    sb.append("    qualifierValue: ").append(toIndentedString(qualifierValue)).append("\n");
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

