package apimodels;

import apimodels.Attribute;
import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * CollectionInfo
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaPlayFrameworkCodegen")
@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class CollectionInfo   {
  @JsonProperty("id")
  @NotNull

  private String id;

  @JsonProperty("size")
  @NotNull

  private Integer size;

  @JsonProperty("element_class")
  @NotNull

  private String elementClass;

  @JsonProperty("source")
  @NotNull

  private String source;

  @JsonProperty("url")
  
  private String url;

  @JsonProperty("attributes")
  @Valid

  private List<Attribute> attributes = null;

  public CollectionInfo id(String id) {
    this.id = id;
    return this;
  }

   /**
   * ID of the collection.
   * @return id
  **/
  public String getId() {
    return id;
  }

  public void setId(String id) {
    this.id = id;
  }

  public CollectionInfo size(Integer size) {
    this.size = size;
    return this;
  }

   /**
   * Number of elements in the collection.
   * @return size
  **/
  public Integer getSize() {
    return size;
  }

  public void setSize(Integer size) {
    this.size = size;
  }

  public CollectionInfo elementClass(String elementClass) {
    this.elementClass = elementClass;
    return this;
  }

   /**
   * BioLink-compatible class of elements in this collection.
   * @return elementClass
  **/
  public String getElementClass() {
    return elementClass;
  }

  public void setElementClass(String elementClass) {
    this.elementClass = elementClass;
  }

  public CollectionInfo source(String source) {
    this.source = source;
    return this;
  }

   /**
   * Transformer that produced this collection.
   * @return source
  **/
  public String getSource() {
    return source;
  }

  public void setSource(String source) {
    this.source = source;
  }

  public CollectionInfo url(String url) {
    this.url = url;
    return this;
  }

   /**
   * URL to obtain members of this collection.
   * @return url
  **/
  public String getUrl() {
    return url;
  }

  public void setUrl(String url) {
    this.url = url;
  }

  public CollectionInfo attributes(List<Attribute> attributes) {
    this.attributes = attributes;
    return this;
  }

  public CollectionInfo addAttributesItem(Attribute attributesItem) {
    if (attributes == null) {
      attributes = new ArrayList<>();
    }
    attributes.add(attributesItem);
    return this;
  }

   /**
   * Additional information and provenance about the collection.
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
    CollectionInfo collectionInfo = (CollectionInfo) o;
    return Objects.equals(id, collectionInfo.id) &&
        Objects.equals(size, collectionInfo.size) &&
        Objects.equals(elementClass, collectionInfo.elementClass) &&
        Objects.equals(source, collectionInfo.source) &&
        Objects.equals(url, collectionInfo.url) &&
        Objects.equals(attributes, collectionInfo.attributes);
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, size, elementClass, source, url, attributes);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class CollectionInfo {\n");
    
    sb.append("    id: ").append(toIndentedString(id)).append("\n");
    sb.append("    size: ").append(toIndentedString(size)).append("\n");
    sb.append("    elementClass: ").append(toIndentedString(elementClass)).append("\n");
    sb.append("    source: ").append(toIndentedString(source)).append("\n");
    sb.append("    url: ").append(toIndentedString(url)).append("\n");
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

