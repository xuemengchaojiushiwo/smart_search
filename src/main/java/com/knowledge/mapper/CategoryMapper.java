package com.knowledge.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.knowledge.entity.Category;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface CategoryMapper extends BaseMapper<Category> {

    // 获取所有类目
    @Select("SELECT * FROM categories WHERE deleted = 0 ORDER BY sort_order ASC")
    List<Category> selectAllCategories();

    // 获取子类目
    @Select("SELECT * FROM categories WHERE parent_id = #{parentId} AND deleted = 0 ORDER BY sort_order ASC")
    List<Category> selectChildrenByParentId(@Param("parentId") Long parentId);

    // 检查是否有子类目
    @Select("SELECT COUNT(*) FROM categories WHERE parent_id = #{parentId} AND deleted = 0")
    Integer countChildrenByParentId(@Param("parentId") Long parentId);
}
