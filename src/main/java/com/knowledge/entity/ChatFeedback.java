package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("chat_feedbacks")
public class ChatFeedback {
    @TableId(type = IdType.AUTO)
    private Long id;

    private String sessionId;

    private String messageId;

    private Long userId;

    private String attitude; // like / dislike

    private String content; // optional reason

    private LocalDateTime createdTime;

    @TableLogic
    private Integer deleted;
}


