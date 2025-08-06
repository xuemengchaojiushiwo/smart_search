package com.knowledge.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;

@Data
public class CategoryDTO {
    
    @NotBlank(message = "类目名称不能为空")
    private String name;
    
    @NotNull(message = "层级不能为空")
    private Integer level;
    
    private Long parentId;
    
    private Integer sortOrder;
    
    private String description;
    
    private String changeReason;
} 
