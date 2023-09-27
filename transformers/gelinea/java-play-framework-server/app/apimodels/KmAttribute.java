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
 * Description of attribute types provided by this knowledge source.
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class KmAttribute   {
  @JsonProperty("attribute_type_id")
  @NotNull

  private String attributeTypeId;

  @JsonProperty("description")
  
  private String description;

  @JsonProperty("source")
  
  private String source;

  @JsonProperty("names")
  
  private List<String> names = null;

  public KmAttribute attributeTypeId(String attributeTypeId) {
    this.attributeTypeId = attributeTypeId;
    return this;
  }

   /**
   * CURIE of the semantic type of the attribute, from the EDAM ontology if possible. If a suitable identifier does not exist, enter a descriptive phrase here and submit the new type for consideration by the appropriate authority.
   * @return attributeTypeId
  **/
  public String getAttributeTypeId() {
    return attributeTypeId;
  }

  public void setAttributeTypeId(String attributeTypeId) {
    this.attributeTypeId = attributeTypeId;
  }

  public KmAttribute description(String description) {
    this.description = description;
    return this;
  }

   /**
   * Description of the attribute.
   * @return description
  **/
  public String getDescription() {
    return description;
  }

  public void setDescription(String description) {
    this.description = description;
  }

  public KmAttribute source(String source) {
    this.source = source;
    return this;
  }

   /**
   * Source of the attribute, as a CURIE prefix.
   * @return source
  **/
  public String getSource() {
    return source;
  }

  public void setSource(String source) {
    this.source = source;
  }

  public KmAttribute names(List<String> names) {
    this.names = names;
    return this;
  }

  public KmAttribute addNamesItem(String namesItem) {
    if (names == null) {
      names = new ArrayList<>();
    }
    names.add(namesItem);
    return this;
  }

   /**
   * Human-readable names or labels for the attribute for attributes of  given type.
   * @return names
  **/
  public List<String> getNames() {
    return names;
  }

  public void setNames(List<String> names) {
    this.names = names;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    KmAttribute kmAttribute = (KmAttribute) o;
    return Objects.equals(attributeTypeId, kmAttribute.attributeTypeId) &&
        Objects.equals(description, kmAttribute.description) &&
        Objects.equals(source, kmAttribute.source) &&
        Objects.equals(names, kmAttribute.names);
  }

  @Override
  public int hashCode() {
    return Objects.hash(attributeTypeId, description, source, names);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class KmAttribute {\n");
    
    sb.append("    attributeTypeId: ").append(toIndentedString(attributeTypeId)).append("\n");
    sb.append("    description: ").append(toIndentedString(description)).append("\n");
    sb.append("    source: ").append(toIndentedString(source)).append("\n");
    sb.append("    names: ").append(toIndentedString(names)).append("\n");
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

