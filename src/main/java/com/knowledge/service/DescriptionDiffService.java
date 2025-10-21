package com.knowledge.service;

import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

/**
 * 生成知识描述的差异高亮 HTML（新增/删除）。
 * 说明：
 * - 基于简单的标记感知分词 + LCS，对文本 token 做增删高亮；
 * - 对 HTML 标签本身不做包裹，避免破坏结构；
 * - 新增使用 <ins class="diff-ins">，删除使用 <del class="diff-del">；
 * - 返回完整可直接渲染的 HTML 片段（包含内联样式）。
 */
@Service
public class DescriptionDiffService {

    public String generateHtmlDiff(String oldHtml, String newHtml) {
        List<String> a = tokenizeHtml(oldHtml == null ? "" : oldHtml);
        List<String> b = tokenizeHtml(newHtml == null ? "" : newHtml);

        // LCS 动态规划
        int n = a.size();
        int m = b.size();
        int[][] dp = new int[n + 1][m + 1];
        for (int i = n - 1; i >= 0; i--) {
            for (int j = m - 1; j >= 0; j--) {
                if (a.get(i).equals(b.get(j))) {
                    dp[i][j] = dp[i + 1][j + 1] + 1;
                } else {
                    dp[i][j] = Math.max(dp[i + 1][j], dp[i][j + 1]);
                }
            }
        }

        StringBuilder out = new StringBuilder();
        // 内联简易样式（GitHub 风格近似）
        out.append("<style>")
           .append(".diff-ins{background:#e6ffed;outline:1px solid #34d058;padding:0 2px;}")
           .append(".diff-del{background:#ffeef0;outline:1px solid #d73a49;color:#b31d28;text-decoration:line-through;padding:0 2px;}")
           .append("</style>");

        int i = 0, j = 0;
        while (i < n && j < m) {
            String ai = a.get(i);
            String bj = b.get(j);
            if (ai.equals(bj)) {
                // 相同 token 直接输出
                out.append(ai);
                i++; j++;
            } else if (dp[i + 1][j] >= dp[i][j + 1]) {
                // a 中有而 b 中无 -> 删除
                appendDeleted(out, ai);
                i++;
            } else {
                // b 中有而 a 中无 -> 新增
                appendInserted(out, bj);
                j++;
            }
        }
        while (i < n) { appendDeleted(out, a.get(i++)); }
        while (j < m) { appendInserted(out, b.get(j++)); }

        return out.toString();
    }

    private static void appendInserted(StringBuilder out, String token) {
        if (isHtmlTag(token)) { out.append(token); return; }
        if (isWhitespace(token)) { out.append(token); return; }
        out.append("<ins class=\"diff-ins\">").append(escapeIfNeeded(token)).append("</ins>");
    }

    private static void appendDeleted(StringBuilder out, String token) {
        if (isHtmlTag(token)) { out.append(token); return; }
        if (isWhitespace(token)) { out.append(token); return; }
        out.append("<del class=\"diff-del\">").append(escapeIfNeeded(token)).append("</del>");
    }

    private static String escapeIfNeeded(String token) {
        // 基于我们以 HTML 片段 token 化的策略：
        // - tag token 原样输出；
        // - 文本 token 可能包含 < > &，做一次转义更安全。
        StringBuilder sb = new StringBuilder();
        for (char c : token.toCharArray()) {
            switch (c) {
                case '&': sb.append("&amp;"); break;
                case '<': sb.append("&lt;"); break;
                case '>': sb.append("&gt;"); break;
                case '"': sb.append("&quot;"); break;
                case '\'': sb.append("&#39;"); break;
                default: sb.append(c);
            }
        }
        return sb.toString();
    }

    private static boolean isHtmlTag(String token) {
        return token.startsWith("<") && token.endsWith(">");
    }

    private static boolean isWhitespace(String token) {
        for (int k = 0; k < token.length(); k++) {
            if (!Character.isWhitespace(token.charAt(k))) return false;
        }
        return true;
    }

    /**
     * 将 HTML 字符串分成 token：
     * - 保留标签整体为单一 token（<...>）
     * - 文本按“词/标点/空白”拆分，尽量避免破坏中文（逐字 token 化）
     */
    private static List<String> tokenizeHtml(String html) {
        List<String> tokens = new ArrayList<>();
        if (html == null || html.isEmpty()) return tokens;

        int i = 0, n = html.length();
        while (i < n) {
            char c = html.charAt(i);
            if (c == '<') {
                int j = i + 1;
                while (j < n && html.charAt(j) != '>') j++;
                if (j < n) {
                    tokens.add(html.substring(i, j + 1));
                    i = j + 1;
                    continue;
                }
            }

            // 空白连续收集
            if (Character.isWhitespace(c)) {
                int j = i + 1;
                while (j < n && Character.isWhitespace(html.charAt(j))) j++;
                tokens.add(html.substring(i, j));
                i = j;
                continue;
            }

            // 英文/数字连续收集为一个 token；中文及其他符号逐字
            if (isAsciiWord(c)) {
                int j = i + 1;
                while (j < n && isAsciiWord(html.charAt(j))) j++;
                tokens.add(html.substring(i, j));
                i = j;
            } else {
                tokens.add(String.valueOf(c));
                i++;
            }
        }
        return tokens;
    }

    private static boolean isAsciiWord(char c) {
        return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '-';
    }
}






