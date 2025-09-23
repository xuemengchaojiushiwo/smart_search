package com.knowledge.controller;

import com.knowledge.dto.FeedbackTypeDTO;
import com.knowledge.enums.FeedbackType;
import com.knowledge.service.EngagementService;
import com.knowledge.util.SecurityUtils;
import com.knowledge.vo.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.Data;
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
	public ApiResponse<Void> like(@PathVariable Long knowledgeId) {
		// 从SecurityContext中获取当前用户名作为userId
		String currentUsername = SecurityUtils.getCurrentUsername();
		Long userId;
		try {
			userId = Long.parseLong(currentUsername);
		} catch (NumberFormatException e) {
			log.error("用户名无法转换为数字ID: {}", currentUsername);
			throw new IllegalArgumentException("用户标识格式错误，无法处理点赞请求");
		}
		engagementService.like(knowledgeId, userId);
		return ApiResponse.success(null);
	}

	@PostMapping("/unlike/{knowledgeId}")
	@Operation(summary = "取消点赞")
	public ApiResponse<Void> unlike(@PathVariable Long knowledgeId) {
		// 从SecurityContext中获取当前用户名作为userId
		String currentUsername = SecurityUtils.getCurrentUsername();
		Long userId;
		try {
			userId = Long.parseLong(currentUsername);
		} catch (NumberFormatException e) {
			log.error("用户名无法转换为数字ID: {}", currentUsername);
			throw new IllegalArgumentException("用户标识格式错误，无法处理取消点赞请求");
		}
		engagementService.unlike(knowledgeId, userId);
		return ApiResponse.success(null);
	}

	@PostMapping("/favorite/{knowledgeId}")
	@Operation(summary = "收藏")
	public ApiResponse<Void> favorite(@PathVariable Long knowledgeId) {
		// 从SecurityContext中获取当前用户名作为userId
		String currentUsername = SecurityUtils.getCurrentUsername();
		Long userId;
		try {
			userId = Long.parseLong(currentUsername);
		} catch (NumberFormatException e) {
			log.error("用户名无法转换为数字ID: {}", currentUsername);
			throw new IllegalArgumentException("用户标识格式错误，无法处理收藏请求");
		}
		engagementService.favorite(knowledgeId, userId);
		return ApiResponse.success(null);
	}

	@PostMapping("/unfavorite/{knowledgeId}")
	@Operation(summary = "取消收藏")
	public ApiResponse<Void> unfavorite(@PathVariable Long knowledgeId) {
		// 从SecurityContext中获取当前用户名作为userId
		String currentUsername = SecurityUtils.getCurrentUsername();
		Long userId;
		try {
			userId = Long.parseLong(currentUsername);
		} catch (NumberFormatException e) {
			log.error("用户名无法转换为数字ID: {}", currentUsername);
			throw new IllegalArgumentException("用户标识格式错误，无法处理取消收藏请求");
		}
		engagementService.unfavorite(knowledgeId, userId);
		return ApiResponse.success(null);
	}

	@PostMapping("/feedback/{knowledgeId}")
	@Operation(summary = "提交反馈")
	public ApiResponse<Void> feedback(
			@PathVariable Long knowledgeId,
			@RequestBody FeedbackRequest request) {
		// 从SecurityContext中获取当前用户名作为userId
		String currentUsername = SecurityUtils.getCurrentUsername();
		Long userId;
		try {
			userId = Long.parseLong(currentUsername);
		} catch (NumberFormatException e) {
			log.error("用户名无法转换为数字ID: {}", currentUsername);
			throw new IllegalArgumentException("用户标识格式错误，无法处理反馈请求");
		}
		
		log.info("收到反馈请求: knowledgeId={}, userId={}, content={}, feedbackType={}", 
				knowledgeId, userId, request.getContent(), request.getFeedbackType());
		
		engagementService.feedback(knowledgeId, userId, request.getContent(), request.getFeedbackType());
		return ApiResponse.success(null);
	}


	@GetMapping("/feedbacks")
	@Operation(summary = "反馈列表")
	public ApiResponse<Object> listFeedbacks(
			@RequestParam(required = false) Integer page,
			@RequestParam(required = false) Integer size,
			@RequestParam(required = false) Long knowledgeId) {
		// 从SecurityContext中获取当前用户名作为userId
		String currentUsername = SecurityUtils.getCurrentUsername();
		Long userId;
		try {
			userId = Long.parseLong(currentUsername);
		} catch (NumberFormatException e) {
			log.error("用户名无法转换为数字ID: {}", currentUsername);
			throw new IllegalArgumentException("用户标识格式错误，无法处理反馈列表请求");
		}
		
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
			@RequestParam(required = false) Integer size) {
		// 从SecurityContext中获取当前用户名作为userId
		String currentUsername = SecurityUtils.getCurrentUsername();
		Long userId;
		try {
			userId = Long.parseLong(currentUsername);
		} catch (NumberFormatException e) {
			log.error("用户名无法转换为数字ID: {}", currentUsername);
			throw new IllegalArgumentException("用户标识格式错误，无法处理收藏列表请求");
		}
		
		return ApiResponse.success(engagementService.listUserFavorites(page, size, userId));
	}

	@GetMapping("/favorite/status/{knowledgeId}")
	@Operation(summary = "查询用户对某个知识的收藏状态")
	public ApiResponse<Object> getFavoriteStatus(@PathVariable Long knowledgeId) {
		// 从SecurityContext中获取当前用户名作为userId
		String currentUsername = SecurityUtils.getCurrentUsername();
		Long userId;
		try {
			userId = Long.parseLong(currentUsername);
		} catch (NumberFormatException e) {
			log.error("用户名无法转换为数字ID: {}", currentUsername);
			throw new IllegalArgumentException("用户标识格式错误，无法处理收藏状态查询请求");
		}
		
		return ApiResponse.success(engagementService.getFavoriteStatus(knowledgeId, userId));
	}

	@Data
	public static class FeedbackRequest {
		/**
		 * 反馈内容
		 */
		private String content;
		
		/**
		 * 反馈类型，如out_of_date/unclear/not_relevant
		 */
		private String feedbackType;
	}
}


