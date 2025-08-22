package com.knowledge.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;

@Data
public class SearchRequest {
    
    @NotBlank(message = "搜索关键词不能为空")
    private String query;

    private Integer page = 1;

    private Integer size = 10;

    private Long parentId;

    private String[] tags;
}
