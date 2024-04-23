package apimodels;

import apimodels.KnowledgeMap;
import apimodels.Parameter;
import apimodels.TransformerInfoProperties;
import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * Definition of the transformer.
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen", date = "2020-02-27T16:03:08.782-05:00[America/New_York]")

@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class TransformerInfo   {
  @JsonProperty("name")
  private String name;

  @JsonProperty("label")
  private String label;

  @JsonProperty("description")
  private String description;

  @JsonProperty("version")
  private String version;

  /**
   * Function of the transformer, one of 'producer', 'expander', 'filter', 'transformer', 'exporter', or 'aggregator'.
   */
  public enum FunctionEnum {
    PRODUCER("producer"),
    
    EXPANDER("expander"),
    
    FILTER("filter"),
    
    TRANSFORMER("transformer"),
    
    EXPORTER("exporter"),
    
    AGGREGATOR("aggregator");

    private final String value;

    FunctionEnum(String value) {
      this.value = value;
    }

    @Override
    @JsonValue
    public String toString() {
      return String.valueOf(value);
    }

    @JsonCreator
    public static FunctionEnum fromValue(String value) {
      for (FunctionEnum b : FunctionEnum.values()) {
        if (b.value.equals(value)) {
          return b;
        }
      }
      throw new IllegalArgumentException("Unexpected value '" + value + "'");
    }
  }

  @JsonProperty("function")
  private FunctionEnum function;

  @JsonProperty("knowledge_map")
  private KnowledgeMap knowledgeMap;

  @JsonProperty("properties")
  private TransformerInfoProperties properties;

  @JsonProperty("parameters")
  private List<Parameter> parameters = null;

  public TransformerInfo name(String name) {
    this.name = name;
    return this;
  }

   /**
   * Name of the transformer.
   * @return name
  **/
  @NotNull
  public String getName() {
    return name;
  }

  public void setName(String name) {
    this.name = name;
  }

  public TransformerInfo label(String label) {
    this.label = label;
    return this;
  }

   /**
   * Short label for GUI display.
   * @return label
  **/
    public String getLabel() {
    return label;
  }

  public void setLabel(String label) {
    this.label = label;
  }

  public TransformerInfo description(String description) {
    this.description = description;
    return this;
  }

   /**
   * Description of the transformer.
   * @return description
  **/
    public String getDescription() {
    return description;
  }

  public void setDescription(String description) {
    this.description = description;
  }

  public TransformerInfo version(String version) {
    this.version = version;
    return this;
  }

   /**
   * Transformer's version.
   * @return version
  **/
    public String getVersion() {
    return version;
  }

  public void setVersion(String version) {
    this.version = version;
  }

  public TransformerInfo function(FunctionEnum function) {
    this.function = function;
    return this;
  }

   /**
   * Function of the transformer, one of 'producer', 'expander', 'filter', 'transformer', 'exporter', or 'aggregator'.
   * @return function
  **/
  @NotNull
  public FunctionEnum getFunction() {
    return function;
  }

  public void setFunction(FunctionEnum function) {
    this.function = function;
  }

  public TransformerInfo knowledgeMap(KnowledgeMap knowledgeMap) {
    this.knowledgeMap = knowledgeMap;
    return this;
  }

   /**
   * Get knowledgeMap
   * @return knowledgeMap
  **/
  @Valid
  public KnowledgeMap getKnowledgeMap() {
    return knowledgeMap;
  }

  public void setKnowledgeMap(KnowledgeMap knowledgeMap) {
    this.knowledgeMap = knowledgeMap;
  }

  public TransformerInfo properties(TransformerInfoProperties properties) {
    this.properties = properties;
    return this;
  }

   /**
   * Get properties
   * @return properties
  **/
  @Valid
  public TransformerInfoProperties getProperties() {
    return properties;
  }

  public void setProperties(TransformerInfoProperties properties) {
    this.properties = properties;
  }

  public TransformerInfo parameters(List<Parameter> parameters) {
    this.parameters = parameters;
    return this;
  }

  public TransformerInfo addParametersItem(Parameter parametersItem) {
    if (parameters == null) {
      parameters = new ArrayList<>();
    }
    parameters.add(parametersItem);
    return this;
  }

   /**
   * Parameters used to control the transformer.
   * @return parameters
  **/
  @Valid
  public List<Parameter> getParameters() {
    return parameters;
  }

  public void setParameters(List<Parameter> parameters) {
    this.parameters = parameters;
  }


  @Override
  public boolean equals(java.lang.Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    TransformerInfo transformerInfo = (TransformerInfo) o;
    return Objects.equals(name, transformerInfo.name) &&
        Objects.equals(label, transformerInfo.label) &&
        Objects.equals(description, transformerInfo.description) &&
        Objects.equals(version, transformerInfo.version) &&
        Objects.equals(function, transformerInfo.function) &&
        Objects.equals(knowledgeMap, transformerInfo.knowledgeMap) &&
        Objects.equals(properties, transformerInfo.properties) &&
        Objects.equals(parameters, transformerInfo.parameters);
  }

  @Override
  public int hashCode() {
    return Objects.hash(name, label, description, version, function, knowledgeMap, properties, parameters);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class TransformerInfo {\n");
    
    sb.append("    name: ").append(toIndentedString(name)).append("\n");
    sb.append("    label: ").append(toIndentedString(label)).append("\n");
    sb.append("    description: ").append(toIndentedString(description)).append("\n");
    sb.append("    version: ").append(toIndentedString(version)).append("\n");
    sb.append("    function: ").append(toIndentedString(function)).append("\n");
    sb.append("    knowledgeMap: ").append(toIndentedString(knowledgeMap)).append("\n");
    sb.append("    properties: ").append(toIndentedString(properties)).append("\n");
    sb.append("    parameters: ").append(toIndentedString(parameters)).append("\n");
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

