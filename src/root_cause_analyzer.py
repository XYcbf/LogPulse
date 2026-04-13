import os
from typing import Any
from loguru import logger

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

def analyze_root_cause(report: dict[str, Any]) -> dict[str, Any]:
    """
    分析排查报告中的错误样本，并给出可能的错误原因。
    """
    all_samples = []
    for dataset in report.get("datasets", []):
        samples = dataset.get("error_samples", [])
        if samples:
            all_samples.extend(samples)
    
    # 去重
    unique_samples = list(set(all_samples))[:10]
    
    if not unique_samples:
        return {
            "summary": "未发现明显的错误日志样本。",
            "details": []
        }

    # 尝试使用 OpenAI 进行分析
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
    
    if HAS_OPENAI and api_key:
        try:
            client = OpenAI(api_key=api_key, base_url=base_url)
            prompt = (
                f"以下是从日志中提取的错误样本。请针对每个错误样本，"
                f"详细分析其可能的原因，并给出具体的解释和可操作的解决方案。请用中文回答。\n\n"
                f"请严格按照以下格式输出分析结果：\n"
                f"--- 错误样本 ---\n"
                f"[原始错误日志样本]\n"
                f"故障定性：[权限问题/环境缺失/代码逻辑错误/其他]\n"
                f"深度解释：[该报错在特定系统（如 Android 或 MIUI）下的具体含义，或详细的技术原因]\n"
                f"修复建议：[直接给出可操作的修改方案，例如：检查AndroidManifest.xml权限、更新依赖版本、检查文件路径等]\n\n"
                f"错误样本:\n" + "\n".join(unique_samples) + "\n"
            )
            response = client.chat.completions.create(
                model="deepseek-chat", # 使用 DeepSeek 默认模型
                messages=[{"role": "user", "content": prompt}]
            )
            analysis = response.choices[0].message.content
            return {
                "summary": "日志分析报告",
                "details": [analysis]
            }
        except Exception as e:
            logger.error(f"AI 分析失败: {e}")

    # 降级：基于规则的简单分析
    return _rule_based_analysis(unique_samples)

def _rule_based_analysis(samples: list[str]) -> dict[str, Any]:
    reasons = []
    for sample in samples:
        sample_lower = sample.lower()
        if "timeout" in sample_lower:
            reasons.append(f"检测到超时错误：'{sample}'。可能原因：网络波动、服务器负载过高或响应时间过长。")
        elif "permission" in sample_lower or "denied" in sample_lower:
            reasons.append(f"检测到权限错误：'{sample}'。可能原因：文件访问权限不足或 API 调用未授权。")
        elif "not found" in sample_lower or "404" in sample_lower:
            reasons.append(f"检测到资源缺失：'{sample}'。可能原因：文件路径错误或 API 接口不存在。")
        elif "nullpointer" in sample_lower or "none" in sample_lower:
            reasons.append(f"检测到空指针/空值引用：'{sample}'。可能原因：代码中未对空对象进行校验。")
        elif "failed to connect" in sample_lower:
            reasons.append(f"检测到连接失败：'{sample}'。可能原因：目标地址不可达或服务已停止。")
        else:
            reasons.append(f"检测到异常日志：'{sample}'。请检查相关业务逻辑。")
    
    return {
        "summary": "基于规则提取的错误原因分析：",
        "details": list(set(reasons))
    }
