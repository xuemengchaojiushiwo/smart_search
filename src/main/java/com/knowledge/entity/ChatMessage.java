package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.*;
import com.knowledge.mybatis.PostgresJsonbTypeHandler;
import lombok.Data;
import org.apache.ibatis.type.JdbcType;

@Data
@TableName("chat_messages")
public class ChatMessage {
    @TableId(type = IdType.AUTO)
    private Long id;

    private String sessionId;

    private String messageId;

    private String role; // user / assistant

    private String content;
    @TableField(typeHandler = PostgresJsonbTypeHandler.class, jdbcType = JdbcType.OTHER)
    private String referencesJson; // 存JSON文本

    private Long timestampMs;

    private String createdBy;
}


