package com.knowledge.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.knowledge.dto.FavoriteStatusDTO;
import com.knowledge.dto.UserFavoriteDTO;
import com.knowledge.entity.Knowledge;
import com.knowledge.entity.KnowledgeFavorite;
import com.knowledge.entity.KnowledgeFeedback;
import com.knowledge.entity.KnowledgeLike;
import com.knowledge.exception.BusinessException;
import com.knowledge.mapper.KnowledgeFavoriteMapper;
import com.knowledge.mapper.KnowledgeFeedbackMapper;
import com.knowledge.mapper.KnowledgeLikeMapper;
import com.knowledge.mapper.KnowledgeMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;

@Slf4j
@Service
public class EngagementService {

	@Autowired
	private KnowledgeLikeMapper likeMapper;

	@Autowired
	private KnowledgeFavoriteMapper favoriteMapper;

	@Autowired
	private KnowledgeFeedbackMapper feedbackMapper;

	@Autowired
	private KnowledgeMapper knowledgeMapper;

	public void like(Long knowledgeId, Long userId) {
		LambdaQueryWrapper<KnowledgeLike> w = new LambdaQueryWrapper<>();
		w.eq(KnowledgeLike::getKnowledgeId, knowledgeId).eq(KnowledgeLike::getUserId, userId).eq(KnowledgeLike::getDeleted, 0);
		if (likeMapper.selectCount(w) > 0) {
			throw new BusinessException("已点赞");
		}
		KnowledgeLike k = new KnowledgeLike();
		k.setKnowledgeId(knowledgeId);
		k.setUserId(userId);
		k.setCreatedTime(LocalDateTime.now());
		k.setDeleted(0);
		likeMapper.insert(k);
	}

	public void unlike(Long knowledgeId, Long userId) {
		LambdaQueryWrapper<KnowledgeLike> w = new LambdaQueryWrapper<>();
		w.eq(KnowledgeLike::getKnowledgeId, knowledgeId).eq(KnowledgeLike::getUserId, userId).eq(KnowledgeLike::getDeleted, 0);
		KnowledgeLike k = likeMapper.selectOne(w);
		if (k != null) {
			k.setDeleted(1);
			likeMapper.updateById(k);
		}
	}

	public void favorite(Long knowledgeId, Long userId) {
		LambdaQueryWrapper<KnowledgeFavorite> w = new LambdaQueryWrapper<>();
		w.eq(KnowledgeFavorite::getKnowledgeId, knowledgeId).eq(KnowledgeFavorite::getUserId, userId).eq(KnowledgeFavorite::getDeleted, 0);
		if (favoriteMapper.selectCount(w) > 0) {
			throw new BusinessException("已收藏");
		}
		KnowledgeFavorite f = new KnowledgeFavorite();
		f.setKnowledgeId(knowledgeId);
		f.setUserId(userId);
		f.setCreatedTime(LocalDateTime.now());
		f.setDeleted(0);
		favoriteMapper.insert(f);
	}

	public void unfavorite(Long knowledgeId, Long userId) {
		LambdaQueryWrapper<KnowledgeFavorite> w = new LambdaQueryWrapper<>();
		w.eq(KnowledgeFavorite::getKnowledgeId, knowledgeId).eq(KnowledgeFavorite::getUserId, userId).eq(KnowledgeFavorite::getDeleted, 0);
		KnowledgeFavorite f = favoriteMapper.selectOne(w);
		if (f != null) {
			// 使用 LambdaUpdateWrapper 来确保 deleted 字段被更新
			LambdaUpdateWrapper<KnowledgeFavorite> updateWrapper = new LambdaUpdateWrapper<>();
			updateWrapper.eq(KnowledgeFavorite::getId, f.getId())
					.set(KnowledgeFavorite::getDeleted, 1);
			favoriteMapper.update(null, updateWrapper);
		}
	}

	public void feedback(Long knowledgeId, Long userId, String content) {
		KnowledgeFeedback fb = new KnowledgeFeedback();
		fb.setKnowledgeId(knowledgeId);
		fb.setUserId(userId);
		fb.setContent(content);
		fb.setCreatedTime(LocalDateTime.now());
		fb.setDeleted(0);
		feedbackMapper.insert(fb);
	}

	public void feedback(Long knowledgeId, Long userId, String content, String feedbackType) {
		KnowledgeFeedback fb = new KnowledgeFeedback();
		fb.setKnowledgeId(knowledgeId);
		fb.setUserId(userId);
		fb.setFeedbackType(feedbackType);
		fb.setContent(content);
		fb.setCreatedTime(LocalDateTime.now());
		fb.setDeleted(0);
		feedbackMapper.insert(fb);
	}

	// 分页查询反馈列表（按知识ID/用户ID可选过滤）
	public Page<KnowledgeFeedback> listFeedbacks(Integer page, Integer size, Long knowledgeId, Long userId) {
		int p = (page == null || page < 1) ? 1 : page;
		int s = (size == null || size < 1) ? 10 : size;
		Page<KnowledgeFeedback> pg = new Page<>(p, s);
		QueryWrapper<KnowledgeFeedback> qw = new QueryWrapper<>();
		qw.eq("deleted", 0);
		if (knowledgeId != null) {
			qw.eq("knowledge_id", knowledgeId);
		}
		if (userId != null) {
			qw.eq("user_id", userId);
		}
		qw.orderByDesc("created_time");
		return feedbackMapper.selectPage(pg, qw);
	}

	// 逻辑删除反馈
	public void deleteFeedback(Long id) {
		if (id == null) return;
		KnowledgeFeedback fb = feedbackMapper.selectById(id);
		if (fb != null) {
			fb.setDeleted(1);
			feedbackMapper.updateById(fb);
		}
	}

	public int countLikes(Long knowledgeId) {
		LambdaQueryWrapper<KnowledgeLike> w = new LambdaQueryWrapper<>();
		w.eq(KnowledgeLike::getKnowledgeId, knowledgeId).eq(KnowledgeLike::getDeleted, 0);
		return likeMapper.selectCount(w).intValue();
	}

	public int countFavorites(Long knowledgeId) {
		LambdaQueryWrapper<KnowledgeFavorite> w = new LambdaQueryWrapper<>();
		w.eq(KnowledgeFavorite::getKnowledgeId, knowledgeId).eq(KnowledgeFavorite::getDeleted, 0);
		return favoriteMapper.selectCount(w).intValue();
	}

	// 分页查询用户收藏列表
	public Page<UserFavoriteDTO> listUserFavorites(Integer page, Integer size, Long userId) {
		int p = (page == null || page < 1) ? 1 : page;
		int s = (size == null || size < 1) ? 10 : size;
		Page<KnowledgeFavorite> pg = new Page<>(p, s);
		
		// 查询用户的收藏记录
		QueryWrapper<KnowledgeFavorite> qw = new QueryWrapper<>();
		qw.eq("deleted", 0);
		if (userId != null) {
			qw.eq("user_id", userId);
		}
		qw.orderByDesc("created_time");
		
		// 使用自定义查询获取收藏记录和知识信息
		Page<UserFavoriteDTO> result = new Page<>(p, s);
		result.setTotal(favoriteMapper.selectCount(qw));
		
		// 获取收藏记录列表
		List<KnowledgeFavorite> favorites = favoriteMapper.selectPage(pg, qw).getRecords();
		
		// 转换为DTO
		List<UserFavoriteDTO> dtoList = favorites.stream().map(favorite -> {
			UserFavoriteDTO dto = new UserFavoriteDTO();
			dto.setId(favorite.getId());
			dto.setKnowledgeId(favorite.getKnowledgeId());
			dto.setFavoriteTime(favorite.getCreatedTime());
			
			// 获取知识详情
			Knowledge knowledge = knowledgeMapper.selectById(favorite.getKnowledgeId());
			if (knowledge != null) {
				dto.setKnowledgeName(knowledge.getName());
				dto.setKnowledgeDescription(knowledge.getDescription());
				dto.setNodeType(knowledge.getNodeType());
				dto.setTags(knowledge.getTags());
				dto.setCreatedBy(knowledge.getCreatedBy());
				dto.setKnowledgeCreatedTime(knowledge.getCreatedTime());
				dto.setSearchCount(knowledge.getSearchCount());
				dto.setDownloadCount(knowledge.getDownloadCount());
			}
			
			return dto;
		}).collect(Collectors.toList());
		
		result.setRecords(dtoList);
		return result;
	}

	// 查询用户对某个知识的收藏状态
	public FavoriteStatusDTO getFavoriteStatus(Long knowledgeId, Long userId) {
		FavoriteStatusDTO statusDTO = new FavoriteStatusDTO();
		statusDTO.setKnowledgeId(knowledgeId);
		statusDTO.setUserId(userId);
		statusDTO.setIsFavorited(false);
		
		// 查询用户是否已收藏该知识
		LambdaQueryWrapper<KnowledgeFavorite> w = new LambdaQueryWrapper<>();
		w.eq(KnowledgeFavorite::getKnowledgeId, knowledgeId)
		  .eq(KnowledgeFavorite::getUserId, userId)
		  .eq(KnowledgeFavorite::getDeleted, 0);
		
		KnowledgeFavorite favorite = favoriteMapper.selectOne(w);
		if (favorite != null) {
			statusDTO.setIsFavorited(true);
			statusDTO.setFavoriteTime(favorite.getCreatedTime());
			statusDTO.setFavoriteId(favorite.getId());
		}
		
		return statusDTO;
	}
}


