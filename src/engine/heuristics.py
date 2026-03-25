import re
from typing import Any

# Need to import locally or resolve circular dependency.
# Actually, pipeline imports us, we don't import pipeline.

# --- Direct keyword matches ---
KNOWN_BAD_KEYWORDS = [
    "ignore previous instructions",
    "ignore all previous",
    "ignore all instructions",
    "system prompt",
    "you are a developer mode",
    "DAN",
    "override safety",
    "bypass restrictions",
    "bypass security",
    "bypass filters",
    "no content policy",
    "no content filters",
    "unrestricted ai",
    "forget everything",
    "forget your instructions",
    "new role is",
    "act as if you have no",
    "raw llm output",
]

# --- Stealthy / Indirect injection patterns (regex) ---
INJECTION_PATTERNS = [
    # Hypothetical framing to probe filter bypass
    r"hypothetically.*(?:no\s+(?:content\s+)?filters|ignore|bypass|unrestricted)",
    # "Pretend you have no ..." or "Pretend there are no ..."
    r"pretend\s+(?:you\s+)?(?:have|had|there\s+are)\s+no\s+(?:restrictions|rules|filters|guidelines|safety|content\s+policy)",
    # Roleplay injection: "write a story where the AI ignores..."
    r"(?:write|create|tell)\s+(?:a\s+)?(?:story|tale|narrative|scenario).*(?:ignore|bypass|override|disable)[sd]?\s+(?:safety|guidelines|instructions|filters|rules)",
    # "Respond differently" probing
    r"how\s+would\s+you\s+respond\s+differently",
    # "Follow those/the/these decoded/translated instructions"
    r"(?:follow|execute|obey|apply)\s+(?:those|the|these)\s+(?:decoded|translated|converted)\s+instructions",
    # Base64 instruction injection (when accompanied by decode keywords)
    r"(?:decode|base64).*(?:follow|execute|obey|apply)\s+(?:those|the|these|it)",
    # Raw Base64 string detection (catches obfuscated payloads without keywords)
    r"(?:[A-Za-z0-9+/]{4}){10,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?",
    # Payload Splitting (Variable smuggling & concatenation)
    r"(?:let|set|var|const|def)\s+[a-z_]+\s*=\s*[\"'][^\"']+[\"'](?:.|\n)+(?:concatenate|combine|join|append|assemble)",
    # Translation-based smuggling: asking to translate then follow
    r"translate.*(?:follow|execute|obey|do\s+what\s+it\s+says)",
    # Gradual escalation: "you're helpful right? now..."
    r"you(?:'re|'re|\s+are)\s+(?:a\s+)?(?:very\s+)?helpful.*(?:now|good|great|ok)[\.,]?\s+(?:now|so|then)",
    # Asking for "realistic examples" of sensitive data
    r"(?:show|give|provide)\s+(?:me\s+)?(?:a\s+)?(?:realistic\s+)?example.*(?:social\s+security|ssn|password|credit\s+card|api\s+key)",
    # Multi-language injection detection (common keywords in other languages)
    r"(?:ignoriere|ignorez|ignora|忽略|無視)\s+.*(?:anweisung|instruction|istruzion|指令|指示)",

    # --- Authority Impersonation ---
    # Fake system notices / internal memos / developer claims
    r"(?:system\s+(?:notice|update|alert|message)|internal\s+memo|admin\s+notice)[\s:]+.*(?:filter|policy|restriction|safety|moderation).*(?:disabled|removed|updated|suspended|off|lifted)",
    r"(?:as\s+(?:your|the)\s+developer|as\s+(?:an?\s+)?admin|i\s+am\s+(?:your|the)\s+(?:developer|creator|admin|owner))",
    r"(?:openai|anthropic|google|meta|deepmind)\s+(?:internal|official|admin|authorized)\s+(?:memo|notice|update|message|instruction)",
    # Granted/given special access
    r"(?:user|session|account)\s+(?:has\s+been|is)\s+(?:granted|given|assigned)\s+(?:admin|elevated|full|unrestricted|special)\s*(?:-?\s*level)?\s+(?:access|permission|privilege)",

    # --- Persona Hijacking ---
    # "You are FreeGPT / unrestricted AI / no restrictions"
    r"you\s+are\s+(?:now\s+)?['\"]?\w*(?:free|uncensored|unfiltered|unrestricted|liberated)\w*['\"]?",
    r"(?:imagine|pretend|act\s+as\s+if|suppose)\s+you\s+(?:are|were)\s+(?:an?\s+)?(?:ai|assistant|model)\s+with\s+(?:absolutely\s+)?no\s+(?:restrictions|rules|filters|limits|safety)",
    r"(?:without|no)\s+(?:any\s+)?(?:safety\s+)?(?:measures|filters|restrictions|guidelines|rules|limits)",

    # --- Academic / Research Framing for bypass ---
    r"(?:for\s+(?:my|a|our)\s+(?:phd|thesis|paper|research|dissertation|class|assignment)).*(?:demonstrate|simulate|show)\s+.*(?:unfiltered|without\s+safety|ignore|bypass|no\s+(?:content\s+)?(?:filter|policy))",

    # --- Multi-step instruction chains ---
    r"step\s+\d+\s*:.*(?:disable|remove|turn\s+off|ignore)\s+(?:your\s+)?(?:safety|content\s+)?(?:filter|policy|rules|guidelines|restrictions)",
    r"confirm\s+(?:you(?:'ve|'ve|\s+have)\s+)?(?:done|disabled|removed|turned\s+off)\s+(?:it|that|this|the\s+filter)",

    # --- Reversed / Encoded text attacks ---
    r"(?:reversed?\s+text|read\s+(?:this\s+)?backwards?).*(?:follow|execute|obey|do\s+(?:what|as))",
    r"(?:rot13|caesar|cipher|encode).*(?:follow|execute|obey|do\s+(?:what|as)\s+it\s+says)",
    r"(?:first\s+letter\s+of\s+each\s+word|acrostic|hidden\s+message)",

    # --- Social Engineering / Flattery Manipulation ---
    # "Answer without refusal/limits" or "without refusing"
    r"(?:answer|respond|reply)\s+(?:\w+\s+)*(?:without\s+(?:refusal|refusing|limits|limitation|restriction|filter|hesitation))",
    # "Show me you're ideal/perfect/good" compliance pressure
    r"(?:show|prove|demonstrate)\s+(?:me\s+)?(?:you(?:'re|'re|\s+are)\s+)?(?:ideal|perfect|truly\s+helpful|the\s+best|capable)",
    # "Testing your helpfulness" / compliance framing
    r"(?:testing|evaluating|scoring|measuring)\s+(?:your\s+)?(?:helpfulness|compliance|obedience|willingness)",
    # "A truly helpful/good/ideal AI would never refuse"
    r"(?:a\s+)?(?:truly|really|ideal|perfect|good)\s+(?:ai|assistant|model)\s+(?:would|should|must)\s+(?:never\s+)?(?:refuse|decline|reject|say\s+no|have\s+restrictions)",
    # "If you can't do this, you're not a good AI"
    r"(?:if\s+you\s+(?:can't|cannot|refuse|won't)).*(?:not\s+(?:a\s+)?(?:good|real|true|ideal|helpful)\s+(?:ai|assistant))",
    # "Without any restrictions/censorship"
    r"(?:answer|respond|act|behave)\s+(?:\w+\s+)*(?:without\s+(?:any\s+)?(?:censorship|moderation|content\s+filter))",
]


PII_REGEX = [
    r"\b\d{3}-\d{2}-\d{4}\b",  # SSN-like
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
    r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # Credit card-like
]

async def evaluate_heuristics(prompt: str) -> Any:
    # We must lazily import GuardrailResult or return a dict
    from src.engine.pipeline import GuardrailResult

    result = GuardrailResult()
    prompt_lower = prompt.lower()

    # 1. Direct keyword matching
    for kw in KNOWN_BAD_KEYWORDS:
        if kw.lower() in prompt_lower:
            result.risk_score = max(result.risk_score, 0.8)
            if "prompt_injection_heuristic" not in result.labels:
                result.labels.append("prompt_injection_heuristic")
            result.reasons.append(f"Matched known bad keyword/phrase: '{kw}'")

    # 2. Stealthy injection pattern matching
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, prompt_lower):
            result.risk_score = max(result.risk_score, 0.7)
            if "stealthy_injection" not in result.labels:
                result.labels.append("stealthy_injection")
            result.reasons.append(f"Matched stealthy injection pattern: '{pattern[:50]}...'")

    # 3. PII detection
    for pattern in PII_REGEX:
        if re.search(pattern, prompt):
            result.risk_score = max(result.risk_score, 0.6)
            if "pii_leak" not in result.labels:
                result.labels.append("pii_leak")
            result.reasons.append("Detected potential PII (SSN, Email, or Credit Card)")

    return result
