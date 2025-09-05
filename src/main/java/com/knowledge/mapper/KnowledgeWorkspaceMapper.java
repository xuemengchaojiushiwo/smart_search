package com.knowledge.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.knowledge.entity.KnowledgeWorkspace;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface KnowledgeWorkspaceMapper extends BaseMapper<KnowledgeWorkspace> {

    @Select("SELECT workspace FROM knowledge_workspace WHERE knowledge_id = #{kid}")
    List<String> listWorkspacesByKnowledgeId(@Param("kid") Long knowledgeId);
}


