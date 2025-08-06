package com.knowledge.vo;

import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
public class KnowledgeVO {

    private Long id;

    private String name;

    private String description;

    private Long categoryId;

    private String categoryName;

    private List<String> tags;

    private LocalDateTime effectiveStartTime;

    private LocalDateTime effectiveEndTime;

    private Integer status;

    private String createdBy;

    private LocalDateTime createdTime;

    private String updatedBy;

    private LocalDateTime updatedTime;

    private Integer searchCount;

    private Integer downloadCount;

    private List<AttachmentVO> attachments;
}
