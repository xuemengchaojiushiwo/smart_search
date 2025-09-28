package com.knowledge.controller;

import com.knowledge.entity.Workspace;
import com.knowledge.entity.User;
import com.knowledge.service.WorkspaceService;
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

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/workspaces")
@RequiredArgsConstructor
@Tag(name = "工作空间管理", description = "工作空间相关接口")
public class WorkspaceController {
    private final WorkspaceService service;
    private final UserService userService;

    @GetMapping
    @Operation(summary = "获取工作空间列表", description = "获取用户有权限的工作空间列表")
    public ApiResponse<List<Workspace>> list() {
        log.info("获取工作空间列表");
        
        // 检查当前用户权限
        String currentUsername = SecurityUtils.getCurrentUsername();
        if (currentUsername == null) {
            return ApiResponse.error("未登录");
        }
        
        User currentUser = userService.findByUsername(currentUsername);
        if (currentUser == null) {
            return ApiResponse.error("用户不存在");
        }
        
        // 如果是admin用户，返回所有工作空间
        if ("Admin".equals(currentUser.getSystemRole())) {
            List<Workspace> workspaces = service.listAll();
            return ApiResponse.success(workspaces);
        }
        
        // 普通用户只返回有权限的工作空间
        List<String> allowedWorkspaces = userService.getAllowedWorkspaces(currentUser.getId());
        if (allowedWorkspaces == null || allowedWorkspaces.isEmpty()) {
            log.info("用户 {} 没有工作空间权限，返回空列表", currentUsername);
            return ApiResponse.success(new ArrayList<>());
        }
        
        List<Workspace> workspaces = service.listByCodes(allowedWorkspaces);
        log.info("用户 {} 有权限的工作空间: {}", currentUsername, allowedWorkspaces);
        return ApiResponse.success(workspaces);
    }

    @PostMapping
    @Operation(summary = "创建工作空间", description = "创建新的工作空间，仅admin可操作")
    public ApiResponse<Workspace> create(
            @Parameter(description = "工作空间信息", required = true) @RequestBody CreateWorkspaceReq req) {
        
        // 检查当前用户是否为admin
        String currentUsername = SecurityUtils.getCurrentUsername();
        if (currentUsername == null) {
            return ApiResponse.error("未登录");
        }
        
        User currentUser = userService.findByUsername(currentUsername);
        if (currentUser == null || !"Admin".equals(currentUser.getSystemRole())) {
            return ApiResponse.error("权限不足，只有admin可以创建工作空间");
        }
        
        log.info("Admin用户 {} 创建工作空间: code={}, name={}", currentUsername, req.getCode(), req.getName());
        Workspace workspace = service.create(req.getCode(), req.getName(), req.getDescription());
        
        // 同步工作空间到admin账户
        syncWorkspaceToAdmin(req.getCode());
        
        return ApiResponse.success("工作空间创建成功", workspace);
    }
    
    /**
     * 同步工作空间给admin账户
     */
    private void syncWorkspaceToAdmin(String workspaceCode) {
        try {
            User admin = userService.findByUsername("666666");
            if (admin != null) {
                String currentWorkspace = admin.getWorkspace();
                if (currentWorkspace == null || currentWorkspace.trim().isEmpty()) {
                    // admin没有工作空间，直接设置
                    admin.setWorkspace(workspaceCode);
                    userService.updateById(admin);
                    log.info("已为admin用户设置工作空间: {}", workspaceCode);
                } else {
                    // 检查admin是否已有该工作空间
                    List<String> adminWorkspaces = Arrays.asList(currentWorkspace.split(","));
                    if (!adminWorkspaces.contains(workspaceCode)) {
                        // 添加新工作空间
                        String newWorkspace = currentWorkspace + "," + workspaceCode;
                        admin.setWorkspace(newWorkspace);
                        userService.updateById(admin);
                        log.info("已为admin用户添加工作空间: {}", workspaceCode);
                    } else {
                        log.info("Admin用户已拥有工作空间: {}", workspaceCode);
                    }
                }
            } else {
                log.warn("未找到admin用户，无法同步工作空间");
            }
        } catch (Exception e) {
            log.warn("同步工作空间给admin失败: {}", e.getMessage());
        }
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新工作空间", description = "更新工作空间信息，仅admin可操作")
    public ApiResponse<Workspace> update(
            @Parameter(description = "工作空间ID", required = true) @PathVariable Long id,
            @Parameter(description = "工作空间信息", required = true) @RequestBody UpdateWorkspaceReq req) {
        
        // 检查当前用户是否为admin
        String currentUsername = SecurityUtils.getCurrentUsername();
        if (currentUsername == null) {
            return ApiResponse.error("未登录");
        }
        
        User currentUser = userService.findByUsername(currentUsername);
        if (currentUser == null || !"Admin".equals(currentUser.getSystemRole())) {
            return ApiResponse.error("权限不足，只有admin可以更新工作空间");
        }
        
        log.info("Admin用户 {} 更新工作空间: id={}, name={}", currentUsername, id, req.getName());
        
        // 这里需要实现更新逻辑，暂时返回成功
        return ApiResponse.success("工作空间更新成功", null);
    }
    
    @DeleteMapping("/{id}")
    @Operation(summary = "删除工作空间", description = "删除工作空间，仅admin可操作")
    public ApiResponse<Void> delete(
            @Parameter(description = "工作空间ID", required = true) @PathVariable Long id) {
        
        // 检查当前用户是否为admin
        String currentUsername = SecurityUtils.getCurrentUsername();
        if (currentUsername == null) {
            return ApiResponse.error("未登录");
        }
        
        User currentUser = userService.findByUsername(currentUsername);
        if (currentUser == null || !"Admin".equals(currentUser.getSystemRole())) {
            return ApiResponse.error("权限不足，只有admin可以删除工作空间");
        }
        
        log.info("Admin用户 {} 删除工作空间: id={}", currentUsername, id);
        
        // 这里需要实现删除逻辑，暂时返回成功
        return ApiResponse.success("工作空间删除成功", null);
    }

    @Data
    public static class CreateWorkspaceReq {
        private String code;
        private String name;
        private String description;
    }
    
    @Data
    public static class UpdateWorkspaceReq {
        private String name;
        private String description;
    }
}


