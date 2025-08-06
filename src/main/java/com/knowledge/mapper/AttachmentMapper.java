package com.knowledge.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.knowledge.entity.Attachment;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface AttachmentMapper extends BaseMapper<Attachment> {

    // 根据知识ID查询附件
    @Select("SELECT * FROM attachments WHERE knowledge_id = #{knowledgeId} AND deleted = 0")
    List<Attachment> selectByKnowledgeId(@Param("knowledgeId") Long knowledgeId);

    // 获取下载次数最多的附件
    @Select("SELECT a.*, k.name as knowledgeName FROM attachments a " +
            "LEFT JOIN knowledge k ON a.knowledge_id = k.id " +
            "WHERE a.deleted = 0 AND k.deleted = 0 " +
            "ORDER BY a.download_count DESC " +
            "LIMIT #{limit}")
    List<Attachment> selectTopDownloads(@Param("limit") Integer limit);
}
