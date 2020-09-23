package apimodels;

import apimodels.Attribute;
import apimodels.CollectionInfo;
import apimodels.CompoundInfo;
import apimodels.CompoundListAllOf;
import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * CompoundList
 */

@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class CompoundList   {
  @JsonProperty("id")
  private String id;

  @JsonProperty("size")
  private Integer size;

  @JsonProperty("element_class")
  private String elementClass;

  @JsonProperty("source")
  private String source;

  @JsonProperty("url")
  private String url;

  @JsonProperty("attributes")
  private List<Attribute> attributes = null;

  @JsonProperty("elements")
  private List<CompoundInfo> elements = null;

  public CompoundList id(String id) {
    this.id = id;
    return this;
  }

   /**
   * ID of the collection.
   * @return id
  **/
  @NotNull
  public String getId() {
    return id;
  }

  public void setId(String id) {
    this.id = id;
  }

  public CompoundList size(Integer size) {
    this.size = size;
    return this;
  }

   /**
   * Number of elements in the collection.
   * @return size
  **/
  @NotNull
  public Integer getSize() {
    return size;
  }

  public void setSize(Integer size) {
    this.size = size;
  }

  public CompoundList elementClass(String elementClass) {
    this.elementClass = elementClass;
    return this;
  }

   /**
   * BioLink-compatible class of elements in this collection.
   * @return elementClass
  **/
  @NotNull
  public String getElementClass() {
    return elementClass;
  }

  public void setElementClass(String elementClass) {
    this.elementClass = elementClass;
  }

  public CompoundList source(String source) {
    this.source = source;
    return this;
  }

   /**
   * Transformer that produced this collection.
   * @return source
  **/
  @NotNull
  public String getSource() {
    return source;
  }

  public void setSource(String source) {
    this.source = source;
  }

  public CompoundList url(String url) {
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

  public CompoundList attributes(List<Attribute> attributes) {
    this.attributes = attributes;
    return this;
  }

  public CompoundList addAttributesItem(Attribute attributesItem) {
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
  @Valid
  public List<Attribute> getAttributes() {
    return attributes;
  }

  public void setAttributes(List<Attribute> attributes) {
    this.attributes = attributes;
  }

  public CompoundList elements(List<CompoundInfo> elements) {
    this.elements = elements;
    return this;
  }

  public CompoundList addElementsItem(CompoundInfo elementsItem) {
    if (elements == null) {
      elements = new ArrayList<>();
    }
    elements.add(elementsItem);
    return this;
  }

   /**
   * Members of the compound list.
   * @return elements
  **/
  @Valid
  public List<CompoundInfo> getElements() {
    return elements;
  }

  public void setElements(List<CompoundInfo> elements) {
    this.elements = elements;
  }


  @Override
  public boolean equals(java.lang.Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    CompoundList compoundList = (CompoundList) o;
    return Objects.equals(id, compoundList.id) &&
        Objects.equals(size, compoundList.size) &&
        Objects.equals(elementClass, compoundList.elementClass) &&
        Objects.equals(source, compoundList.source) &&
        Objects.equals(url, compoundList.url) &&
        Objects.equals(attributes, compoundList.attributes) &&
        Objects.equals(elements, compoundList.elements);
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, size, elementClass, source, url, attributes, elements);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class CompoundList {\n");
    
    sb.append("    id: ").append(toIndentedString(id)).append("\n");
    sb.append("    size: ").append(toIndentedString(size)).append("\n");
    sb.append("    elementClass: ").append(toIndentedString(elementClass)).append("\n");
    sb.append("    source: ").append(toIndentedString(source)).append("\n");
    sb.append("    url: ").append(toIndentedString(url)).append("\n");
    sb.append("    attributes: ").append(toIndentedString(attributes)).append("\n");
    sb.append("    elements: ").append(toIndentedString(elements)).append("\n");
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

