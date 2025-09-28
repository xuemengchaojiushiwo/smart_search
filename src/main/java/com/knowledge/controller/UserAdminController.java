package com.knowledge.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.knowledge.entity.User;
import com.knowledge.service.UserService;
import com.knowledge.util.SecurityUtils;
import com.knowledge.vo.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.Arrays;
import java.util.List;

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
        
        // 过滤掉admin用户（包括admin和666666）
        qw.and(w -> w.ne(User::getUsername, "admin")
                .and(w2 -> w2.ne(User::getUsername, "666666")));
        
        if (keyword != null && !keyword.isEmpty()) {
            qw.and(w -> w.like(User::getUsername, keyword)
                    .or().like(User::getStaffId, keyword)
                    .or().like(User::getEmail, keyword));
        }
        if (workspace != null && !workspace.isEmpty() && !"ALL".equalsIgnoreCase(workspace)) {
            qw.like(User::getWorkspace, workspace);
        }
        log.info("用户查询条件: {}", qw.getTargetSql());
        Page<User> result = userService.page(pg, qw);
        log.info("查询结果数量: {}", result.getRecords().size());
        return ApiResponse.success(result);
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新用户的系统角色/工作空间")
    public ApiResponse<Void> update(
            @PathVariable Long id,
            @RequestBody UpdateUserReq req
    ) {
        // 检查当前用户是否为admin
        String currentUsername = SecurityUtils.getCurrentUsername();
        if (currentUsername == null) {
            return ApiResponse.error("未登录");
        }
        
        User currentUser = userService.findByUsername(currentUsername);
        if (currentUser == null || !"Admin".equals(currentUser.getSystemRole())) {
            return ApiResponse.error("权限不足，请联系admin修改");
        }
        
        User u = new User();
        u.setId(id);
        if (req.getSystemRole() != null) {
            u.setSystemRole(req.getSystemRole());
        }
        if (req.getWorkspace() != null) {
            u.setWorkspace(req.getWorkspace());
            
            // 如果更新了工作空间，需要同步给admin账户
            syncWorkspaceToAdmin(req.getWorkspace());
        }
        userService.updateById(u);
        return ApiResponse.success(null);
    }
    
    @PostMapping("/init-admin")
    @Operation(summary = "初始化admin账户", description = "不受token管控，多次调用保证只有一个admin")
    public ApiResponse<String> initAdmin() {
        try {
            // 检查是否已存在666666用户
            User existingAdmin = userService.findByUsername("666666");
            if (existingAdmin != null) {
                log.info("Admin用户已存在，ID: {}", existingAdmin.getId());
                return ApiResponse.success("Admin用户已存在");
            }
            
            // 创建666666用户作为admin
            User admin = new User();
            admin.setUsername("666666");
            admin.setStaffId("666666");
            admin.setEmail("admin@company.com");
            admin.setSystemRole("Admin");
            admin.setStaffRole("Admin");
            admin.setWorkspace("WPB,工作空间2"); // 默认工作空间
            admin.setDisplayName("系统管理员");
            admin.setStatus(1);
            admin.setDeleted(0);
            
            userService.save(admin);
            log.info("Admin用户创建成功，ID: {}", admin.getId());
            
            return ApiResponse.success("Admin用户初始化成功");
        } catch (Exception e) {
            log.error("初始化admin用户失败", e);
            return ApiResponse.error("初始化admin用户失败: " + e.getMessage());
        }
    }
    
    /**
     * 同步工作空间给admin账户
     */
    private void syncWorkspaceToAdmin(String workspace) {
        try {
            User admin = userService.findByUsername("admin");
            if (admin != null && admin.getWorkspace() != null) {
                // 检查admin是否已有该工作空间
                List<String> adminWorkspaces = Arrays.asList(admin.getWorkspace().split(","));
                if (!adminWorkspaces.contains(workspace)) {
                    // 添加新工作空间
                    String newWorkspace = admin.getWorkspace() + "," + workspace;
                    admin.setWorkspace(newWorkspace);
                    userService.updateById(admin);
                    log.info("已为admin用户添加工作空间: {}", workspace);
                }
            }
        } catch (Exception e) {
            log.warn("同步工作空间给admin失败: {}", e.getMessage());
        }
    }

    @Data
    public static class UpdateUserReq {
        private String systemRole;
        private String workspace;
    }
}


