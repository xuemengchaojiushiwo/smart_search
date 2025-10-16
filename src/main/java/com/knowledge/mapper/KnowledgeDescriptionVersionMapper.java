package com.knowledge.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.knowledge.entity.KnowledgeDescriptionVersion;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * 知识描述版本Mapper
 */
@Mapper
public interface KnowledgeDescriptionVersionMapper extends BaseMapper<KnowledgeDescriptionVersion> {
    
    /**
     * 根据知识ID查询所有版本
     */
    List<KnowledgeDescriptionVersion> selectByKnowledgeId(@Param("knowledgeId") Long knowledgeId);
    
    /**
     * 根据知识ID和版本号查询
     */
    KnowledgeDescriptionVersion selectByKnowledgeIdAndVersion(
        @Param("knowledgeId") Long knowledgeId,
        @Param("version") String version
    );
}



