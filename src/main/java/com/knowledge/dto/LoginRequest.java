package com.knowledge.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;

@Data
public class LoginRequest {
    
    @NotBlank(message = "用户名不能为�?")
    private String username;
    
    @NotBlank(message = "密码不能为空")
    private String password;
} 
