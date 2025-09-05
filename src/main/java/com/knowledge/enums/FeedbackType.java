package com.knowledge.enums;

/**
 * 反馈类型枚举
 */
public enum FeedbackType {
    OUT_OF_DATE("out_of_date", "内容过时"),
    UNCLEAR("unclear", "内容不清晰"),
    NOT_RELEVANT("not_relevant", "内容不相关");

    private final String code;
    private final String description;

    FeedbackType(String code, String description) {
        this.code = code;
        this.description = description;
    }

    public String getCode() {
        return code;
    }

    public String getDescription() {
        return description;
    }

    /**
     * 根据代码获取枚举
     */
    public static FeedbackType fromCode(String code) {
        for (FeedbackType type : values()) {
            if (type.getCode().equals(code)) {
                return type;
            }
        }
        return null;
    }
}
