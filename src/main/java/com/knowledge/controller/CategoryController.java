package com.knowledge.controller;

import com.knowledge.vo.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.Operation;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/categories")
@Tag(name = "类目管理(兼容)", description = "已废弃，兼容返回由知识树生成的数据")
public class CategoryController {
    
    @Autowired
    private com.knowledge.service.KnowledgeService knowledgeService;
    
    // 废弃的创建/更新/删除接口不再提供（保持路由存在会造成误用），仅保留 /tree 兼容
    
    @GetMapping("/tree")
    @Operation(summary = "获取类目树(兼容)", description = "由知识树生成的兼容数据，后续请改用 /api/knowledge/{parentId}/children")
    public ApiResponse<List<com.knowledge.vo.KnowledgeTreeVO>> getCategoryTree() {
        log.info("获取类目树(兼容)");
        List<com.knowledge.vo.KnowledgeTreeVO> tree = knowledgeService.getKnowledgeTree();
        return ApiResponse.success(tree);
    }
}
