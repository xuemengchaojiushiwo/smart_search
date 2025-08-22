package com.knowledge.service;

import com.alibaba.fastjson2.JSON;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.knowledge.dto.CategoryDTO;
import com.knowledge.entity.Category;
import com.knowledge.entity.CategoryChangeLog;
import com.knowledge.exception.BusinessException;
import com.knowledge.mapper.CategoryMapper;
import com.knowledge.vo.CategoryTreeVO;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

@Slf4j
@Service
public class CategoryService extends ServiceImpl<CategoryMapper, Category> {

    @Autowired
    private CategoryChangeLogService categoryChangeLogService;

    // 创建类目
    @Transactional
    public Category createCategory(CategoryDTO dto, String currentUser) {
        Category category = new Category();
        BeanUtils.copyProperties(dto, category);
        category.setCreatedBy(currentUser);

        // 验证父类目是否存在
        if (dto.getParentId() != null) {
            Category parent = getById(dto.getParentId());
            if (parent == null) {
                throw new BusinessException("父类目不存在");
            }
            category.setLevel(parent.getLevel() + 1);
        } else {
            category.setLevel(1);
        }

        save(category);

        // 记录创建历史
        CategoryChangeLog changeLog = new CategoryChangeLog();
        changeLog.setCategoryId(category.getId());
        changeLog.setChangeType("CREATE");
        changeLog.setNewData(JSON.toJSONString(category));
        changeLog.setChangeReason("创建类目");
        changeLog.setChangedBy(currentUser);
        changeLog.setChangedTime(LocalDateTime.now());
        categoryChangeLogService.save(changeLog);

        return category;
    }

    // 更新类目
    @Transactional
    public Category updateCategory(Long id, CategoryDTO dto, String currentUser) {
        Category category = getById(id);
        if (category == null) {
            throw new BusinessException("类目不存在");
        }

        // 记录变更历史
        CategoryChangeLog changeLog = new CategoryChangeLog();
        changeLog.setCategoryId(id);
        changeLog.setChangeType("UPDATE");
        changeLog.setOldData(JSON.toJSONString(category));
        changeLog.setChangeReason(dto.getChangeReason());
        changeLog.setChangedBy(currentUser);
        changeLog.setChangedTime(LocalDateTime.now());
        categoryChangeLogService.save(changeLog);

        // 更新类目
        BeanUtils.copyProperties(dto, category);
        category.setUpdatedBy(currentUser);
        updateById(category);

        return category;
    }

    // 删除类目
    @Transactional
    public void deleteCategory(Long id, String currentUser) {
        Category category = getById(id);
        if (category == null) {
            throw new BusinessException("类目不存在");
        }

        // 检查是否有子类目
        if (baseMapper.countChildrenByParentId(id) > 0) {
            throw new BusinessException("存在子类目，无法删除");
        }

        // 记录删除历史
        CategoryChangeLog changeLog = new CategoryChangeLog();
        changeLog.setCategoryId(id);
        changeLog.setChangeType("DELETE");
        changeLog.setOldData(JSON.toJSONString(category));
        changeLog.setChangeReason("删除类目");
        changeLog.setChangedBy(currentUser);
        changeLog.setChangedTime(LocalDateTime.now());
        categoryChangeLogService.save(changeLog);

        // 执行删除
        removeById(id);
    }

    // 获取类目树
    public List<CategoryTreeVO> getCategoryTree() {
        List<Category> allCategories = baseMapper.selectAllCategories();
        return buildCategoryTree(allCategories, null);
    }

    // 构建类目树
    private List<CategoryTreeVO> buildCategoryTree(List<Category> allCategories, Long parentId) {
        List<CategoryTreeVO> tree = new ArrayList<>();

        for (Category category : allCategories) {
            if (Objects.equals(category.getParentId(), parentId)) {
                CategoryTreeVO node = new CategoryTreeVO();
                BeanUtils.copyProperties(category, node);
                node.setChildren(buildCategoryTree(allCategories, category.getId()));
                tree.add(node);
            }
        }

        return tree;
    }
}
