package com.knowledge.vo;

import lombok.Data;

@Data
public class LoginResponse {

    private Boolean success;

    private String token;

    private Long expiresIn;

    private UserVO user;

    @Data
    public static class UserVO {
        private Long id;
        private String username;
        private String email;
        private String role;
        private String displayName;
        private String staffId;
        private String staffRole;
        private String systemRole;
        private String workspace;
        private java.util.List<DeptRoleVO> departments;
    }
    
    @Data
    public static class DeptRoleVO {
        private String dept;
        private String role;
    }
}
