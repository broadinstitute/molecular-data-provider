package apimodels;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * Parameter
 */

@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class Parameter   {
  @JsonProperty("name")
  private String name;

  /**
   * Type of the parameter, one of 'Boolean', 'int', 'double', 'string'.
   */
  public enum TypeEnum {
    BOOLEAN("Boolean"),
    
    INT("int"),
    
    DOUBLE("double"),
    
    STRING("string");

    private final String value;

    TypeEnum(String value) {
      this.value = value;
    }

    @Override
    @JsonValue
    public String toString() {
      return String.valueOf(value);
    }

    @JsonCreator
    public static TypeEnum fromValue(String value) {
      for (TypeEnum b : TypeEnum.values()) {
        if (b.value.equals(value)) {
          return b;
        }
      }
      throw new IllegalArgumentException("Unexpected value '" + value + "'");
    }
  }

  @JsonProperty("type")
  private TypeEnum type;

  @JsonProperty("required")
  private Boolean required;

  @JsonProperty("multivalued")
  private Boolean multivalued;

  @JsonProperty("default")
  private String _default;

  @JsonProperty("example")
  private String example;

  @JsonProperty("allowed_values")
  private List<String> allowedValues = null;

  @JsonProperty("allowed_range")
  private List<BigDecimal> allowedRange = null;

  @JsonProperty("suggested_values")
  private String suggestedValues;

  public Parameter name(String name) {
    this.name = name;
    return this;
  }

   /**
   * Name of the parameter.
   * @return name
  **/
  @NotNull
  public String getName() {
    return name;
  }

  public void setName(String name) {
    this.name = name;
  }

  public Parameter type(TypeEnum type) {
    this.type = type;
    return this;
  }

   /**
   * Type of the parameter, one of 'Boolean', 'int', 'double', 'string'.
   * @return type
  **/
  @NotNull
  public TypeEnum getType() {
    return type;
  }

  public void setType(TypeEnum type) {
    this.type = type;
  }

  public Parameter required(Boolean required) {
    this.required = required;
    return this;
  }

   /**
   * Indicates whether the parameter is required(default true).
   * @return required
  **/
    public Boolean getRequired() {
    return required;
  }

  public void setRequired(Boolean required) {
    this.required = required;
  }

  public Parameter multivalued(Boolean multivalued) {
    this.multivalued = multivalued;
    return this;
  }

   /**
   * Indicates whether multiple occurences of the parameter are allowed (default false).
   * @return multivalued
  **/
    public Boolean getMultivalued() {
    return multivalued;
  }

  public void setMultivalued(Boolean multivalued) {
    this.multivalued = multivalued;
  }

  public Parameter _default(String _default) {
    this._default = _default;
    return this;
  }

   /**
   * Default value of the parameter.
   * @return _default
  **/
    public String getDefault() {
    return _default;
  }

  public void setDefault(String _default) {
    this._default = _default;
  }

  public Parameter example(String example) {
    this.example = example;
    return this;
  }

   /**
   * Example value of the parameter.
   * @return example
  **/
    public String getExample() {
    return example;
  }

  public void setExample(String example) {
    this.example = example;
  }

  public Parameter allowedValues(List<String> allowedValues) {
    this.allowedValues = allowedValues;
    return this;
  }

  public Parameter addAllowedValuesItem(String allowedValuesItem) {
    if (allowedValues == null) {
      allowedValues = new ArrayList<>();
    }
    allowedValues.add(allowedValuesItem);
    return this;
  }

   /**
   * Allowed values for the parameter.
   * @return allowedValues
  **/
    public List<String> getAllowedValues() {
    return allowedValues;
  }

  public void setAllowedValues(List<String> allowedValues) {
    this.allowedValues = allowedValues;
  }

  public Parameter allowedRange(List<BigDecimal> allowedRange) {
    this.allowedRange = allowedRange;
    return this;
  }

  public Parameter addAllowedRangeItem(BigDecimal allowedRangeItem) {
    if (allowedRange == null) {
      allowedRange = new ArrayList<>();
    }
    allowedRange.add(allowedRangeItem);
    return this;
  }

   /**
   * Allowed range for values of the parameter.
   * @return allowedRange
  **/
  @Size(min=2,max=2)
@Valid
  public List<BigDecimal> getAllowedRange() {
    return allowedRange;
  }

  public void setAllowedRange(List<BigDecimal> allowedRange) {
    this.allowedRange = allowedRange;
  }

  public Parameter suggestedValues(String suggestedValues) {
    this.suggestedValues = suggestedValues;
    return this;
  }

   /**
   * Suggested value range for the parameter.
   * @return suggestedValues
  **/
    public String getSuggestedValues() {
    return suggestedValues;
  }

  public void setSuggestedValues(String suggestedValues) {
    this.suggestedValues = suggestedValues;
  }


  @Override
  public boolean equals(java.lang.Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    Parameter parameter = (Parameter) o;
    return Objects.equals(name, parameter.name) &&
        Objects.equals(type, parameter.type) &&
        Objects.equals(required, parameter.required) &&
        Objects.equals(multivalued, parameter.multivalued) &&
        Objects.equals(_default, parameter._default) &&
        Objects.equals(example, parameter.example) &&
        Objects.equals(allowedValues, parameter.allowedValues) &&
        Objects.equals(allowedRange, parameter.allowedRange) &&
        Objects.equals(suggestedValues, parameter.suggestedValues);
  }

  @Override
  public int hashCode() {
    return Objects.hash(name, type, required, multivalued, _default, example, allowedValues, allowedRange, suggestedValues);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class Parameter {\n");
    
    sb.append("    name: ").append(toIndentedString(name)).append("\n");
    sb.append("    type: ").append(toIndentedString(type)).append("\n");
    sb.append("    required: ").append(toIndentedString(required)).append("\n");
    sb.append("    multivalued: ").append(toIndentedString(multivalued)).append("\n");
    sb.append("    _default: ").append(toIndentedString(_default)).append("\n");
    sb.append("    example: ").append(toIndentedString(example)).append("\n");
    sb.append("    allowedValues: ").append(toIndentedString(allowedValues)).append("\n");
    sb.append("    allowedRange: ").append(toIndentedString(allowedRange)).append("\n");
    sb.append("    suggestedValues: ").append(toIndentedString(suggestedValues)).append("\n");
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

