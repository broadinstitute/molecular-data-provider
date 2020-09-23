package apimodels;

import apimodels.Attribute;
import apimodels.CollectionInfo;
import apimodels.GeneInfo;
import apimodels.GeneListAllOf;
import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.*;
import java.util.Set;
import javax.validation.*;
import java.util.Objects;
import javax.validation.constraints.*;
/**
 * GeneList
 */

@SuppressWarnings({"UnusedReturnValue", "WeakerAccess"})
public class GeneList   {
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
  private List<GeneInfo> elements = null;

  public GeneList id(String id) {
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

  public GeneList size(Integer size) {
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

  public GeneList elementClass(String elementClass) {
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

  public GeneList source(String source) {
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

  public GeneList url(String url) {
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

  public GeneList attributes(List<Attribute> attributes) {
    this.attributes = attributes;
    return this;
  }

  public GeneList addAttributesItem(Attribute attributesItem) {
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

  public GeneList elements(List<GeneInfo> elements) {
    this.elements = elements;
    return this;
  }

  public GeneList addElementsItem(GeneInfo elementsItem) {
    if (elements == null) {
      elements = new ArrayList<>();
    }
    elements.add(elementsItem);
    return this;
  }

   /**
   * Members of the gene list.
   * @return elements
  **/
  @Valid
  public List<GeneInfo> getElements() {
    return elements;
  }

  public void setElements(List<GeneInfo> elements) {
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
    GeneList geneList = (GeneList) o;
    return Objects.equals(id, geneList.id) &&
        Objects.equals(size, geneList.size) &&
        Objects.equals(elementClass, geneList.elementClass) &&
        Objects.equals(source, geneList.source) &&
        Objects.equals(url, geneList.url) &&
        Objects.equals(attributes, geneList.attributes) &&
        Objects.equals(elements, geneList.elements);
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, size, elementClass, source, url, attributes, elements);
  }

  @SuppressWarnings("StringBufferReplaceableByString")
  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class GeneList {\n");
    
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

