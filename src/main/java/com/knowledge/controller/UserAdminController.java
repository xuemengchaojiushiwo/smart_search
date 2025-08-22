package com.knowledge.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.knowledge.entity.User;
import com.knowledge.service.UserService;
import com.knowledge.vo.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/api/admin/users")
@RequiredArgsConstructor
@Tag(name = "用户管理", description = "系统角色与工作空间管理")
public class UserAdminController {

    private final UserService userService;

    @GetMapping
    @Operation(summary = "分页查询用户")
    public ApiResponse<Page<User>> list(
            @Parameter(description = "页码") @RequestParam(required = false) Integer page,
            @Parameter(description = "每页大小") @RequestParam(required = false) Integer size,
            @Parameter(description = "关键词(用户名/工号/邮箱)") @RequestParam(required = false) String keyword,
            @Parameter(description = "按workspace过滤(ALL/WPB/GPB等)") @RequestParam(required = false, name = "workspace") String workspace
    ) {
        int p = (page == null || page < 1) ? 1 : page;
        int s = (size == null || size < 1) ? 20 : size;
        Page<User> pg = new Page<>(p, s);
        LambdaQueryWrapper<User> qw = new LambdaQueryWrapper<>();
        qw.eq(User::getDeleted, 0);
        if (keyword != null && !keyword.isEmpty()) {
            qw.and(w -> w.like(User::getUsername, keyword)
                    .or().like(User::getStaffId, keyword)
                    .or().like(User::getEmail, keyword));
        }
        if (workspace != null && !workspace.isEmpty() && !"ALL".equalsIgnoreCase(workspace)) {
            qw.like(User::getWorkspace, workspace);
        }
        Page<User> result = userService.page(pg, qw);
        return ApiResponse.success(result);
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新用户的系统角色/工作空间")
    public ApiResponse<Void> update(
            @PathVariable Long id,
            @RequestBody UpdateUserReq req
    ) {
        User u = new User();
        u.setId(id);
        if (req.getSystemRole() != null) {
            u.setSystemRole(req.getSystemRole());
            // 同步兼容字段
            u.setRole(req.getSystemRole());
        }
        if (req.getWorkspace() != null) {
            u.setWorkspace(req.getWorkspace());
        }
        userService.updateById(u);
        return ApiResponse.success(null);
    }

    @Data
    public static class UpdateUserReq {
        private String systemRole;
        private String workspace;
    }
}


