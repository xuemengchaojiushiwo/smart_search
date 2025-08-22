package com.knowledge.controller;

import com.knowledge.dto.CategoryDTO;
import com.knowledge.entity.Category;
import com.knowledge.service.CategoryService;
import com.knowledge.vo.CategoryTreeVO;
import com.knowledge.vo.Result;
import com.knowledge.vo.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/categories")
@Tag(name = "类目管理", description = "知识类目管理相关接口")
public class CategoryController {
    
    @Autowired
    private CategoryService categoryService;
    
    @PostMapping
    @Operation(summary = "创建类目", description = "创建新的知识类目")
    public ApiResponse<Category> createCategory(
            @Parameter(description = "类目信息", required = true) @Valid @RequestBody CategoryDTO dto) {
        log.info("创建类目: {}", dto.getName());
        Category category = categoryService.createCategory(dto, "admin"); // 暂时写死用户
        return ApiResponse.success("类目创建成功", category);
    }
    
    @PutMapping("/{id}")
    @Operation(summary = "更新类目", description = "根据ID更新类目信息")
    public ApiResponse<Category> updateCategory(
            @Parameter(description = "类目ID", required = true, example = "1") @PathVariable Long id,
            @Parameter(description = "类目信息", required = true) @Valid @RequestBody CategoryDTO dto) {
        log.info("更新类目: {}", id);
        Category category = categoryService.updateCategory(id, dto, "admin"); // 暂时写死用户
        return ApiResponse.success("类目更新成功", category);
    }
    
    @DeleteMapping("/{id}")
    @Operation(summary = "删除类目", description = "根据ID删除类目")
    public ApiResponse<Map<String, Object>> deleteCategory(
            @Parameter(description = "类目ID", required = true, example = "1") @PathVariable Long id) {
        log.info("删除类目: {}", id);
        categoryService.deleteCategory(id, "admin"); // 暂时写死用户

        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("message", "删除成功");
        return ApiResponse.success("类目删除成功", result);
    }
    
    @GetMapping("/{id}")
    @Operation(summary = "获取类目详情", description = "根据ID获取类目详细信息")
    public ApiResponse<Category> getCategory(
            @Parameter(description = "类目ID", required = true, example = "1") @PathVariable Long id) {
        log.info("获取类目详情: {}", id);
        Category category = categoryService.getById(id);
        return ApiResponse.success(category);
    }

    @GetMapping("/tree")
    @Operation(summary = "获取类目树", description = "获取完整的类目树结构")
    public ApiResponse<List<CategoryTreeVO>> getCategoryTree() {
        log.info("获取类目树");
        List<CategoryTreeVO> tree = categoryService.getCategoryTree();
        return ApiResponse.success(tree);
    }
}
