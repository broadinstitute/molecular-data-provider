package apimodels;

import com.fasterxml.jackson.annotation.JsonTypeName;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * Additional metadata for the transformer.
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class TransformerInfoProperties   {
  @JsonProperty("source_url")
  
  private String sourceUrl;

  @JsonProperty("source_version")
  
  private String sourceVersion;

  @JsonProperty("source_date")
  
  private String sourceDate;

  @JsonProperty("terms_of_service")
  
  private String termsOfService;

  @JsonProperty("method")
  
  private String method;

  @JsonProperty("method_url")
  
  private String methodUrl;

  public TransformerInfoProperties sourceUrl(String sourceUrl) {
    this.sourceUrl = sourceUrl;
    return this;
  }

   /**
   * URL for underlying data or a wrapped service.
   * @return sourceUrl
  **/
  public String getSourceUrl() {
    return sourceUrl;
  }

  public void setSourceUrl(String sourceUrl) {
    this.sourceUrl = sourceUrl;
  }

  public TransformerInfoProperties sourceVersion(String sourceVersion) {
    this.sourceVersion = sourceVersion;
    return this;
  }

   /**
   * Version of the underlying source or data.
   * @return sourceVersion
  **/
  public String getSourceVersion() {
    return sourceVersion;
  }

  public void setSourceVersion(String sourceVersion) {
    this.sourceVersion = sourceVersion;
  }

  public TransformerInfoProperties sourceDate(String sourceDate) {
    this.sourceDate = sourceDate;
    return this;
  }

   /**
   * Date of injest of underlying data or a wrapped service.
   * @return sourceDate
  **/
  public String getSourceDate() {
    return sourceDate;
  }

  public void setSourceDate(String sourceDate) {
    this.sourceDate = sourceDate;
  }

  public TransformerInfoProperties termsOfService(String termsOfService) {
    this.termsOfService = termsOfService;
    return this;
  }

   /**
   * Link to the page that describes the terms of service for the transformer.
   * @return termsOfService
  **/
  public String getTermsOfService() {
    return termsOfService;
  }

  public void setTermsOfService(String termsOfService) {
    this.termsOfService = termsOfService;
  }

  public TransformerInfoProperties method(String method) {
    this.method = method;
    return this;
  }

   /**
   * A method used to generate output lists.
   * @return method
  **/
  public String getMethod() {
    return method;
  }

  public void setMethod(String method) {
    this.method = method;
  }

  public TransformerInfoProperties methodUrl(String methodUrl) {
    this.methodUrl = methodUrl;
    return this;
  }

   /**
   * Link to a description of a method used to generate output lists.
   * @return methodUrl
  **/
  public String getMethodUrl() {
    return methodUrl;
  }

  public void setMethodUrl(String methodUrl) {
    this.methodUrl = methodUrl;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    TransformerInfoProperties transformerInfoProperties = (TransformerInfoProperties) o;
    return Objects.equals(sourceUrl, transformerInfoProperties.sourceUrl) &&
        Objects.equals(sourceVersion, transformerInfoProperties.sourceVersion) &&
        Objects.equals(sourceDate, transformerInfoProperties.sourceDate) &&
        Objects.equals(termsOfService, transformerInfoProperties.termsOfService) &&
        Objects.equals(method, transformerInfoProperties.method) &&
        Objects.equals(methodUrl, transformerInfoProperties.methodUrl);
  }

  @Override
  public int hashCode() {
    return Objects.hash(sourceUrl, sourceVersion, sourceDate, termsOfService, method, methodUrl);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class TransformerInfoProperties {\n");
    
    sb.append("    sourceUrl: ").append(toIndentedString(sourceUrl)).append("\n");
    sb.append("    sourceVersion: ").append(toIndentedString(sourceVersion)).append("\n");
    sb.append("    sourceDate: ").append(toIndentedString(sourceDate)).append("\n");
    sb.append("    termsOfService: ").append(toIndentedString(termsOfService)).append("\n");
    sb.append("    method: ").append(toIndentedString(method)).append("\n");
    sb.append("    methodUrl: ").append(toIndentedString(methodUrl)).append("\n");
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

