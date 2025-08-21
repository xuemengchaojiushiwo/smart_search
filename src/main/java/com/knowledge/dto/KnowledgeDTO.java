package com.knowledge.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import java.time.LocalDateTime;
import java.util.List;

@Data
public class KnowledgeDTO {

    @NotBlank(message = "知识名称不能为空")
    private String name;

    private String description;

    @NotNull(message = "类目ID不能为空")
    private Long categoryId;

    private List<String> tags;

    // 结构化表格数据：{columns:[{name,type}], rows:[...]}
    private Object tableData;

    private LocalDateTime effectiveStartTime;

    private LocalDateTime effectiveEndTime;

    private String changeReason;
}
