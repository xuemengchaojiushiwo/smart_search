package com.knowledge.controller;

import com.knowledge.entity.Workspace;
import com.knowledge.service.WorkspaceService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/workspaces")
@RequiredArgsConstructor
public class WorkspaceController {
    private final WorkspaceService service;

    @GetMapping
    public List<Workspace> list() {
        return service.listAll();
    }

    @PostMapping
    public Workspace create(@RequestBody CreateWorkspaceReq req) {
        return service.create(req.getCode(), req.getName(), req.getDescription());
    }

    @Data
    public static class CreateWorkspaceReq {
        private String code;
        private String name;
        private String description;
    }
}


