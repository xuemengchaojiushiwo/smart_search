package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

@Data
@TableName("chat_messages")
public class ChatMessage {
    @TableId(type = IdType.AUTO)
    private Long id;

    private String sessionId;

    private String messageId;

    private String role; // user / assistant

    private String content;

    private String referencesJson; // 存JSON文本

    private Long timestampMs;

    private String createdBy;
}


