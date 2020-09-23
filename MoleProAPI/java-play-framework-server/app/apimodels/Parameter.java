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

  @JsonProperty("default")
  private String _default;

  @JsonProperty("example")
  private String example;

  @JsonProperty("biolink_class")
  private String biolinkClass;

  @JsonProperty("allowed_values")
  private List<String> allowedValues = null;

  @JsonProperty("allowed_range")
  private List<BigDecimal> allowedRange = null;

  @JsonProperty("suggested_values")
  private String suggestedValues;

  @JsonProperty("lookup_url")
  private String lookupUrl;

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

  public Parameter biolinkClass(String biolinkClass) {
    this.biolinkClass = biolinkClass;
    return this;
  }

   /**
   * BioLink class of the parameter. Applicable to producers only and only one parameter can have a BioLink class.
   * @return biolinkClass
  **/
    public String getBiolinkClass() {
    return biolinkClass;
  }

  public void setBiolinkClass(String biolinkClass) {
    this.biolinkClass = biolinkClass;
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

  public Parameter lookupUrl(String lookupUrl) {
    this.lookupUrl = lookupUrl;
    return this;
  }

   /**
   * URL to search for suitable parameter values.
   * @return lookupUrl
  **/
    public String getLookupUrl() {
    return lookupUrl;
  }

  public void setLookupUrl(String lookupUrl) {
    this.lookupUrl = lookupUrl;
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
        Objects.equals(_default, parameter._default) &&
        Objects.equals(example, parameter.example) &&
        Objects.equals(biolinkClass, parameter.biolinkClass) &&
        Objects.equals(allowedValues, parameter.allowedValues) &&
        Objects.equals(allowedRange, parameter.allowedRange) &&
        Objects.equals(suggestedValues, parameter.suggestedValues) &&
        Objects.equals(lookupUrl, parameter.lookupUrl);
  }

  @Override
  public int hashCode() {
    return Objects.hash(name, type, _default, example, biolinkClass, allowedValues, allowedRange, suggestedValues, lookupUrl);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class Parameter {\n");
    
    sb.append("    name: ").append(toIndentedString(name)).append("\n");
    sb.append("    type: ").append(toIndentedString(type)).append("\n");
    sb.append("    _default: ").append(toIndentedString(_default)).append("\n");
    sb.append("    example: ").append(toIndentedString(example)).append("\n");
    sb.append("    biolinkClass: ").append(toIndentedString(biolinkClass)).append("\n");
    sb.append("    allowedValues: ").append(toIndentedString(allowedValues)).append("\n");
    sb.append("    allowedRange: ").append(toIndentedString(allowedRange)).append("\n");
    sb.append("    suggestedValues: ").append(toIndentedString(suggestedValues)).append("\n");
    sb.append("    lookupUrl: ").append(toIndentedString(lookupUrl)).append("\n");
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

