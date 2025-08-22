package com.knowledge.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.knowledge.entity.SearchHistory;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface SearchHistoryMapper extends BaseMapper<SearchHistory> {

    // 获取热门搜索
    @Select("SELECT query, COUNT(*) as count FROM search_history " +
            "WHERE deleted = 0 AND search_time >= DATE_SUB(NOW(), INTERVAL 1 HOUR) " +
            "GROUP BY query ORDER BY count DESC LIMIT #{limit}")
    List<String> selectHotSearches(@Param("limit") Integer limit);

    // 获取用户推荐问题
    @Select("SELECT query FROM search_history " +
            "WHERE deleted = 0 AND user_id = #{userId} " +
            "ORDER BY search_time DESC LIMIT #{limit}")
    List<String> selectUserRecommendations(@Param("userId") Long userId, @Param("limit") Integer limit);

    // 获取全局推荐问题
    @Select("SELECT query FROM search_history " +
            "WHERE deleted = 0 " +
            "ORDER BY search_time DESC LIMIT #{limit}")
    List<String> selectGlobalRecommendations(@Param("limit") Integer limit);
    
    // 从历史搜索中获取建议
    @Select("SELECT query FROM search_history " +
            "WHERE deleted = 0 AND query LIKE CONCAT(#{query}, '%') " +
            "GROUP BY query ORDER BY COUNT(*) DESC, MAX(search_time) DESC LIMIT #{limit}")
    List<String> selectSuggestionsFromHistory(@Param("query") String query, @Param("limit") Integer limit);
}
