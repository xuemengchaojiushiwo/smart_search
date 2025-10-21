package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.*;
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;
import com.knowledge.mybatis.PostgresJsonbTypeHandler;
import lombok.Data;
import org.apache.ibatis.type.JdbcType;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * 知识历史版本实体
 * 存储每个版本的完整信息，支持详细的版本比较
 */
@Data
@TableName(value = "knowledge_history_versions", autoResultMap = true)
public class KnowledgeHistoryVersion {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    /**
     * 知识ID
     */
    private Long knowledgeId;
    
    /**
     * 版本号（数字）
     */
    private Integer versionNumber;
    
    /**
     * 版本名称（如V1, V2, V3等）
     */
    private String versionName;
    
    /**
     * 知识名称
     */
    private String name;
    
    /**
     * 知识描述
     */
    private String description;
    
    /**
     * 父级ID
     */
    private Long parentId;
    
    /**
     * 节点类型
     */
    private String nodeType;
    
    /**
     * 标签列表
     */
    @TableField(typeHandler = PostgresJsonbTypeHandler.class, jdbcType = JdbcType.OTHER)
    private List<String> tags;
    
    /**
     * 结构化表格数据：{columns:[{name,type}], rows:[...]}
     */
    @TableField(typeHandler = PostgresJsonbTypeHandler.class, jdbcType = JdbcType.OTHER)
    private Object tableData;
    
    /**
     * 生效开始时间
     */
    private LocalDateTime effectiveStartTime;
    
    /**
     * 生效结束时间
     */
    private LocalDateTime effectiveEndTime;
    
    /**
     * 状态
     */
    private Integer status;
    
    /**
     * 搜索次数
     */
    private Integer searchCount;
    
    /**
     * 下载次数
     */
    private Integer downloadCount;
    
    /**
     * 变更类型：CREATE-创建, UPDATE-更新, DELETE-删除
     */
    private String changeType;
    
    /**
     * 变更原因
     */
    private String changeReason;
    
    /**
     * 变更摘要
     */
    private String changeSummary;
    
    /**
     * 字段变更详情（JSON格式）
     * 存储具体哪些字段发生了变化，以及变化前后的值
     */
    @TableField(typeHandler = PostgresJsonbTypeHandler.class, jdbcType = JdbcType.OTHER)
    private Map<String, Object> fieldChanges;
    
    /**
     * 创建人
     */
    private String createdBy;
    
    /**
     * 创建时间
     */
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdTime;
    
    /**
     * 更新人
     */
    private String updatedBy;
    
    /**
     * 更新时间
     */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedTime;
    
    /**
     * 逻辑删除
     */
    @TableLogic
    private Integer deleted;
}
