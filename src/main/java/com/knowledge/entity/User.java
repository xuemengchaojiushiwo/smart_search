package com.knowledge.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("users")
public class User {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    // LDAP 返回的人名/账户
    private String username;

    // 工号/员工编号（登录填写）
    @TableField("staffid")
    private String staffId;

    private String email;

    // 系统角色（用于鉴权）。为兼容旧逻辑，仍保留 role 字段
    private String role;

    // 员工在组织内的职能角色（LDAP返回）
    @TableField("staff_role")
    private String staffRole;

    // 系统内角色（ADMIN/DEPT_ADMIN/USER等）
    @TableField("system_role")
    private String systemRole;

    // 工作空间（逗号分隔）
    private String workspace;
    
    private Integer status;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdTime;
    
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedTime;

    @TableLogic
    private Integer deleted;
}
