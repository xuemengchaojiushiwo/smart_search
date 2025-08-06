package com.knowledge.vo;

import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
public class CategoryTreeVO {

    private Long id;

    private String name;

    private Integer level;

    private Long parentId;

    private Integer sortOrder;

    private Integer status;

    private String description;

    private String createdBy;

    private LocalDateTime createdTime;

    private String updatedBy;

    private LocalDateTime updatedTime;

    private List<CategoryTreeVO> children;
}
