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

@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class Names   {
  @JsonProperty("name")
  private String name;

  @JsonProperty("synonyms")
  private List<String> synonyms = null;

  @JsonProperty("source")
  private String source;

  @JsonProperty("url")
  private String url;

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

  public Names source(String source) {
    this.source = source;
    return this;
  }

   /**
   * Source of names and synonyms.
   * @return source
  **/
  @NotNull
  public String getSource() {
    return source;
  }

  public void setSource(String source) {
    this.source = source;
  }

  public Names url(String url) {
    this.url = url;
    return this;
  }

   /**
   * URL for additional information.
   * @return url
  **/
    public String getUrl() {
    return url;
  }

  public void setUrl(String url) {
    this.url = url;
  }


  @Override
  public boolean equals(java.lang.Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    Names names = (Names) o;
    return Objects.equals(name, names.name) &&
        Objects.equals(synonyms, names.synonyms) &&
        Objects.equals(source, names.source) &&
        Objects.equals(url, names.url);
  }

  @Override
  public int hashCode() {
    return Objects.hash(name, synonyms, source, url);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class Names {\n");
    
    sb.append("    name: ").append(toIndentedString(name)).append("\n");
    sb.append("    synonyms: ").append(toIndentedString(synonyms)).append("\n");
    sb.append("    source: ").append(toIndentedString(source)).append("\n");
    sb.append("    url: ").append(toIndentedString(url)).append("\n");
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

