package apimodels;

import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * Names
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class Names   {
  @JsonProperty("name")
  
  private String name;

  @JsonProperty("synonyms")
  
  private List<String> synonyms = null;

  @JsonProperty("name_type")
  @NotNull

  private String nameType;

  @JsonProperty("source")
  @NotNull

  private String source;

  @JsonProperty("provided_by")
  @NotNull

  private String providedBy;

  @JsonProperty("language")
  
  private String language;

  public Names name(String name) {
    this.name = name;
    return this;
  }

   /**
   * Name of the compound.
   * @return name
  **/
  public String getName() {
    return name;
  }

  public void setName(String name) {
    this.name = name;
  }

  public Names synonyms(List<String> synonyms) {
    this.synonyms = synonyms;
    return this;
  }

  public Names addSynonymsItem(String synonymsItem) {
    if (synonyms == null) {
      synonyms = new ArrayList<>();
    }
    synonyms.add(synonymsItem);
    return this;
  }

   /**
   * Name of the compound.
   * @return synonyms
  **/
  public List<String> getSynonyms() {
    return synonyms;
  }

  public void setSynonyms(List<String> synonyms) {
    this.synonyms = synonyms;
  }

  public Names nameType(String nameType) {
    this.nameType = nameType;
    return this;
  }

   /**
   * Type of names and synonyms, e.g. inn, trademarked name.
   * @return nameType
  **/
  public String getNameType() {
    return nameType;
  }

  public void setNameType(String nameType) {
    this.nameType = nameType;
  }

  public Names source(String source) {
    this.source = source;
    return this;
  }

   /**
   * Primary source of names and synonyms.
   * @return source
  **/
  public String getSource() {
    return source;
  }

  public void setSource(String source) {
    this.source = source;
  }

  public Names providedBy(String providedBy) {
    this.providedBy = providedBy;
    return this;
  }

   /**
   * Transformer that produced the names and synonyms.
   * @return providedBy
  **/
  public String getProvidedBy() {
    return providedBy;
  }

  public void setProvidedBy(String providedBy) {
    this.providedBy = providedBy;
  }

  public Names language(String language) {
    this.language = language;
    return this;
  }

   /**
   * Language of names and synonyms.
   * @return language
  **/
  public String getLanguage() {
    return language;
  }

  public void setLanguage(String language) {
    this.language = language;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    Names names = (Names) o;
    return Objects.equals(name, names.name) &&
        Objects.equals(synonyms, names.synonyms) &&
        Objects.equals(nameType, names.nameType) &&
        Objects.equals(source, names.source) &&
        Objects.equals(providedBy, names.providedBy) &&
        Objects.equals(language, names.language);
  }

  @Override
  public int hashCode() {
    return Objects.hash(name, synonyms, nameType, source, providedBy, language);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class Names {\n");
    
    sb.append("    name: ").append(toIndentedString(name)).append("\n");
    sb.append("    synonyms: ").append(toIndentedString(synonyms)).append("\n");
    sb.append("    nameType: ").append(toIndentedString(nameType)).append("\n");
    sb.append("    source: ").append(toIndentedString(source)).append("\n");
    sb.append("    providedBy: ").append(toIndentedString(providedBy)).append("\n");
    sb.append("    language: ").append(toIndentedString(language)).append("\n");
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

