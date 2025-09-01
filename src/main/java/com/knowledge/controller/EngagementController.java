package com.knowledge.controller;

import com.knowledge.dto.FeedbackTypeDTO;
import com.knowledge.enums.FeedbackType;
import com.knowledge.service.EngagementService;
import com.knowledge.vo.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@RestController
@RequestMapping("/api/engagement")
@Tag(name = "知识互动", description = "点赞/收藏/反馈接口")
public class EngagementController {

	@Autowired
	private EngagementService engagementService;

	@GetMapping("/feedback/types")
	@Operation(summary = "获取反馈类型枚举列表")
	public ApiResponse<List<FeedbackTypeDTO>> getFeedbackTypes() {
		List<FeedbackTypeDTO> feedbackTypes = Arrays.stream(FeedbackType.values())
				.map(type -> new FeedbackTypeDTO(type.getCode(), type.getDescription()))
				.collect(Collectors.toList());
		return ApiResponse.success(feedbackTypes);
	}

	@PostMapping("/like/{knowledgeId}")
	@Operation(summary = "点赞")
	public ApiResponse<Void> like(@PathVariable Long knowledgeId, @RequestParam(defaultValue = "1") Long userId) {
		engagementService.like(knowledgeId, userId);
		return ApiResponse.success(null);
	}

	@PostMapping("/unlike/{knowledgeId}")
	@Operation(summary = "取消点赞")
	public ApiResponse<Void> unlike(@PathVariable Long knowledgeId, @RequestParam(defaultValue = "1") Long userId) {
		engagementService.unlike(knowledgeId, userId);
		return ApiResponse.success(null);
	}

	@PostMapping("/favorite/{knowledgeId}")
	@Operation(summary = "收藏")
	public ApiResponse<Void> favorite(@PathVariable Long knowledgeId, @RequestParam(defaultValue = "1") Long userId) {
		engagementService.favorite(knowledgeId, userId);
		return ApiResponse.success(null);
	}

	@PostMapping("/unfavorite/{knowledgeId}")
	@Operation(summary = "取消收藏")
	public ApiResponse<Void> unfavorite(@PathVariable Long knowledgeId, @RequestParam(defaultValue = "1") Long userId) {
		engagementService.unfavorite(knowledgeId, userId);
		return ApiResponse.success(null);
	}

	@PostMapping("/feedback/{knowledgeId}")
	@Operation(summary = "提交反馈")
	public ApiResponse<Void> feedback(
			@PathVariable Long knowledgeId,
			@Parameter(description = "反馈内容") @RequestParam(required = false) String content,
			@Parameter(description = "反馈类型(out_of_date|unclear|not_relevant)") @RequestParam(required = false, name = "feedbackType") String feedbackType,
			@RequestParam(defaultValue = "1") Long userId) {
		engagementService.feedback(knowledgeId, userId, content, feedbackType);
		return ApiResponse.success(null);
	}

	@GetMapping("/feedbacks")
	@Operation(summary = "反馈列表")
	public ApiResponse<Object> listFeedbacks(
			@RequestParam(required = false) Integer page,
			@RequestParam(required = false) Integer size,
			@RequestParam(required = false) Long knowledgeId,
			@RequestParam(required = false) Long userId) {
		return ApiResponse.success(engagementService.listFeedbacks(page, size, knowledgeId, userId));
	}

	@DeleteMapping("/feedback/{id}")
	@Operation(summary = "删除反馈")
	public ApiResponse<Void> deleteFeedback(@PathVariable Long id) {
		engagementService.deleteFeedback(id);
		return ApiResponse.success(null);
	}

	@GetMapping("/favorites")
	@Operation(summary = "用户收藏列表")
	public ApiResponse<Object> listUserFavorites(
			@RequestParam(required = false) Integer page,
			@RequestParam(required = false) Integer size,
			@RequestParam(defaultValue = "1") Long userId) {
		return ApiResponse.success(engagementService.listUserFavorites(page, size, userId));
	}

	@GetMapping("/favorite/status/{knowledgeId}")
	@Operation(summary = "查询用户对某个知识的收藏状态")
	public ApiResponse<Object> getFavoriteStatus(
			@PathVariable Long knowledgeId,
			@RequestParam(defaultValue = "1") Long userId) {
		return ApiResponse.success(engagementService.getFavoriteStatus(knowledgeId, userId));
	}
}


