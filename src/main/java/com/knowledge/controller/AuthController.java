package com.knowledge.controller;

import com.knowledge.dto.LoginRequest;
import com.knowledge.entity.User;
import com.knowledge.service.UserService;
import com.knowledge.util.JwtTokenProvider;
import com.knowledge.vo.ApiResponse;
import com.knowledge.vo.LoginResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;

/**
 * 用户认证控制器 */
@Slf4j
@RestController
@RequestMapping("/api/auth")
@Tag(name = "用户认证", description = "用户登录认证相关接口")
public class AuthController {

    @Autowired
    private UserService userService;

    @Autowired
    private JwtTokenProvider jwtTokenProvider;

    @PostMapping("/login")
    @Operation(summary = "用户登录", description = "用户登录并返回JWT token")
    public ApiResponse<LoginResponse> login(
            @Parameter(description = "登录信息", required = true) @Valid @RequestBody LoginRequest request) {
        log.info("用户登录: {}", request.getUsername());

        // 验证用户
        User user = userService.validateUser(request.getUsername(), request.getPassword());

        // 生成token（优先使用systemRole）
        String roleForToken = user.getSystemRole() != null ? user.getSystemRole() : user.getRole();
        String token = jwtTokenProvider.generateToken(user.getUsername(), roleForToken);

        // 构建响应
        LoginResponse response = new LoginResponse();
        response.setSuccess(true);
        response.setToken(token);
        response.setExpiresIn(jwtTokenProvider.getExpirationTime());

        LoginResponse.UserVO userVO = new LoginResponse.UserVO();
        userVO.setId(user.getId());
        userVO.setUsername(user.getUsername());
        userVO.setEmail(user.getEmail());
        userVO.setRole(roleForToken);
        response.setUser(userVO);

        return ApiResponse.success("登录成功", response);
    }

    @PostMapping("/logout")
    @Operation(summary = "退出登录", description = "用户退出登录，客户端应清除本地token")
    public ApiResponse<Void> logout(@RequestHeader(value = "Authorization", required = false) String authorization) {
        log.info("用户退出登录: token={}", authorization);
        // 当前无服务端token状态，前端清除即可
        return ApiResponse.success("退出成功", null);
    }
}
