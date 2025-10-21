package com.knowledge.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.knowledge.entity.KnowledgeHistoryVersion;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 知识历史版本Mapper
 */
@Mapper
public interface KnowledgeHistoryVersionMapper extends BaseMapper<KnowledgeHistoryVersion> {
    
    /**
     * 根据知识ID获取所有历史版本
     */
    @Select("SELECT * FROM knowledge_history_versions WHERE knowledge_id = #{knowledgeId} AND deleted = 0 ORDER BY version_number ASC")
    List<KnowledgeHistoryVersion> selectByKnowledgeId(@Param("knowledgeId") Long knowledgeId);
    
    /**
     * 根据知识ID和版本号获取特定版本
     */
    @Select("SELECT * FROM knowledge_history_versions WHERE knowledge_id = #{knowledgeId} AND version_number = #{versionNumber} AND deleted = 0")
    KnowledgeHistoryVersion selectByKnowledgeIdAndVersion(@Param("knowledgeId") Long knowledgeId, @Param("versionNumber") Integer versionNumber);
    
    /**
     * 获取知识的最新版本号
     */
    @Select("SELECT COALESCE(MAX(version_number), 0) FROM knowledge_history_versions WHERE knowledge_id = #{knowledgeId} AND deleted = 0")
    Integer getMaxVersionNumber(@Param("knowledgeId") Long knowledgeId);
    
    /**
     * 获取知识的版本数量
     */
    @Select("SELECT COUNT(*) FROM knowledge_history_versions WHERE knowledge_id = #{knowledgeId} AND deleted = 0")
    Integer getVersionCount(@Param("knowledgeId") Long knowledgeId);
}
