package apimodels;

import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * Additional metadata for the transformer.
 */

@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class TransformerInfoProperties   {
  @JsonProperty("list_predicate")
  private String listPredicate;

  @JsonProperty("member_predicate")
  private String memberPredicate;

  @JsonProperty("source_url")
  private String sourceUrl;

  @JsonProperty("terms_of_service")
  private String termsOfService;

  @JsonProperty("method")
  private String method;

  public TransformerInfoProperties listPredicate(String listPredicate) {
    this.listPredicate = listPredicate;
    return this;
  }

   /**
   * BioLink model predicate describing relationship between input and output gene lists.
   * @return listPredicate
  **/
    public String getListPredicate() {
    return listPredicate;
  }

  public void setListPredicate(String listPredicate) {
    this.listPredicate = listPredicate;
  }

  public TransformerInfoProperties memberPredicate(String memberPredicate) {
    this.memberPredicate = memberPredicate;
    return this;
  }

   /**
   * BioLink model predicate describing relationship between input and output genes.
   * @return memberPredicate
  **/
    public String getMemberPredicate() {
    return memberPredicate;
  }

  public void setMemberPredicate(String memberPredicate) {
    this.memberPredicate = memberPredicate;
  }

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
   * A method used to generate output gene lists.
   * @return method
  **/
    public String getMethod() {
    return method;
  }

  public void setMethod(String method) {
    this.method = method;
  }


  @Override
  public boolean equals(java.lang.Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    TransformerInfoProperties transformerInfoProperties = (TransformerInfoProperties) o;
    return Objects.equals(listPredicate, transformerInfoProperties.listPredicate) &&
        Objects.equals(memberPredicate, transformerInfoProperties.memberPredicate) &&
        Objects.equals(sourceUrl, transformerInfoProperties.sourceUrl) &&
        Objects.equals(termsOfService, transformerInfoProperties.termsOfService) &&
        Objects.equals(method, transformerInfoProperties.method);
  }

  @Override
  public int hashCode() {
    return Objects.hash(listPredicate, memberPredicate, sourceUrl, termsOfService, method);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class TransformerInfoProperties {\n");
    
    sb.append("    listPredicate: ").append(toIndentedString(listPredicate)).append("\n");
    sb.append("    memberPredicate: ").append(toIndentedString(memberPredicate)).append("\n");
    sb.append("    sourceUrl: ").append(toIndentedString(sourceUrl)).append("\n");
    sb.append("    termsOfService: ").append(toIndentedString(termsOfService)).append("\n");
    sb.append("    method: ").append(toIndentedString(method)).append("\n");
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

