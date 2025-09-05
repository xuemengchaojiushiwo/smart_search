package com.knowledge.dto;

import lombok.Data;

/**
 * 反馈类型DTO
 */
@Data
public class FeedbackTypeDTO {
    private String code;
    private String description;

    public FeedbackTypeDTO(String code, String description) {
        this.code = code;
        this.description = description;
    }
}
