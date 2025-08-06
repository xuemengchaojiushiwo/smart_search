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
    }
}
