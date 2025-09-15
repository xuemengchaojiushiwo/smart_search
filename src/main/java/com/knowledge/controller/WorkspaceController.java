package com.knowledge.controller;

import com.knowledge.entity.Workspace;
import com.knowledge.service.WorkspaceService;
import com.knowledge.vo.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/workspaces")
@RequiredArgsConstructor
@Tag(name = "工作空间管理", description = "工作空间相关接口")
public class WorkspaceController {
    private final WorkspaceService service;

    @GetMapping
    @Operation(summary = "获取工作空间列表", description = "获取所有工作空间列表")
    public ApiResponse<List<Workspace>> list() {
        log.info("获取工作空间列表");
        List<Workspace> workspaces = service.listAll();
        return ApiResponse.success(workspaces);
    }

    @PostMapping
    @Operation(summary = "创建工作空间", description = "创建新的工作空间")
    public ApiResponse<Workspace> create(
            @Parameter(description = "工作空间信息", required = true) @RequestBody CreateWorkspaceReq req) {
        log.info("创建工作空间: code={}, name={}", req.getCode(), req.getName());
        Workspace workspace = service.create(req.getCode(), req.getName(), req.getDescription());
        return ApiResponse.success("工作空间创建成功", workspace);
    }

    @Data
    public static class CreateWorkspaceReq {
        private String code;
        private String name;
        private String description;
    }
}


