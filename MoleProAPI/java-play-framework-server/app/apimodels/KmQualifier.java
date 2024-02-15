package apimodels;

import com.fasterxml.jackson.annotation.JsonTypeName;
import java.util.ArrayList;
import java.util.List;
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
public class KmQualifier   {
  @JsonProperty("qualifier_type_id")
  @NotNull

  private String qualifierTypeId;

  @JsonProperty("applicable_values")
  
  private List<String> applicableValues = null;

  public KmQualifier qualifierTypeId(String qualifierTypeId) {
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

  public KmQualifier applicableValues(List<String> applicableValues) {
    this.applicableValues = applicableValues;
    return this;
  }

  public KmQualifier addApplicableValuesItem(String applicableValuesItem) {
    if (applicableValues == null) {
      applicableValues = new ArrayList<>();
    }
    applicableValues.add(applicableValuesItem);
    return this;
  }

   /**
   * Values associated with the type of the qualifier, drawn from a set of controlled values by the type as specified in the Biolink model (e.g. 'expression' or 'abundance' for the qualifier type 'subject_aspect', etc).
   * @return applicableValues
  **/
  public List<String> getApplicableValues() {
    return applicableValues;
  }

  public void setApplicableValues(List<String> applicableValues) {
    this.applicableValues = applicableValues;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    KmQualifier kmQualifier = (KmQualifier) o;
    return Objects.equals(qualifierTypeId, kmQualifier.qualifierTypeId) &&
        Objects.equals(applicableValues, kmQualifier.applicableValues);
  }

  @Override
  public int hashCode() {
    return Objects.hash(qualifierTypeId, applicableValues);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class KmQualifier {\n");
    
    sb.append("    qualifierTypeId: ").append(toIndentedString(qualifierTypeId)).append("\n");
    sb.append("    applicableValues: ").append(toIndentedString(applicableValues)).append("\n");
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

