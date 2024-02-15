package apimodels;

import apimodels.Attribute;
import com.fasterxml.jackson.annotation.JsonTypeName;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * ComparisonInfo
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class ComparisonInfo   {
  @JsonProperty("operation")
  @NotNull

  private String operation;

  @JsonProperty("score")
  @NotNull
@Valid

  private BigDecimal score;

  @JsonProperty("attributes")
  @Valid

  private List<Attribute> attributes = null;

  public ComparisonInfo operation(String operation) {
    this.operation = operation;
    return this;
  }

   /**
   * Comparison operation.
   * @return operation
  **/
  public String getOperation() {
    return operation;
  }

  public void setOperation(String operation) {
    this.operation = operation;
  }

  public ComparisonInfo score(BigDecimal score) {
    this.score = score;
    return this;
  }

   /**
   * Score of the comparison operation.
   * @return score
  **/
  public BigDecimal getScore() {
    return score;
  }

  public void setScore(BigDecimal score) {
    this.score = score;
  }

  public ComparisonInfo attributes(List<Attribute> attributes) {
    this.attributes = attributes;
    return this;
  }

  public ComparisonInfo addAttributesItem(Attribute attributesItem) {
    if (attributes == null) {
      attributes = new ArrayList<>();
    }
    attributes.add(attributesItem);
    return this;
  }

   /**
   * Additional information about the comparison.
   * @return attributes
  **/
  public List<Attribute> getAttributes() {
    return attributes;
  }

  public void setAttributes(List<Attribute> attributes) {
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
    ComparisonInfo comparisonInfo = (ComparisonInfo) o;
    return Objects.equals(operation, comparisonInfo.operation) &&
        Objects.equals(score, comparisonInfo.score) &&
        Objects.equals(attributes, comparisonInfo.attributes);
  }

  @Override
  public int hashCode() {
    return Objects.hash(operation, score, attributes);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class ComparisonInfo {\n");
    
    sb.append("    operation: ").append(toIndentedString(operation)).append("\n");
    sb.append("    score: ").append(toIndentedString(score)).append("\n");
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

