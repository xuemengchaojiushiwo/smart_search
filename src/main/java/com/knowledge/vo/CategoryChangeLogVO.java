package com.knowledge.vo;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class CategoryChangeLogVO {

    private Long id;

    private Long categoryId;

    private String changeType;

    private String oldData;

    private String newData;

    private String changeReason;

    private String changedBy;

    private LocalDateTime changedTime;
}
