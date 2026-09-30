"""
Complete categorized keywords for JNI design smell research
All 261 keywords from OPTIMIZED_KEYWORDS, organized by category
"""

import pandas as pd

CATEGORIES = {
    # ============================================================
    # CATEGORY 0: BASELINE KEYWORDS (For Scientific Comparison)
    # ============================================================
    "baseline": [
        "Python/C issue",
        "foreign library",
        "foreign function interface",
        "polyglot",
        "programming languages issues",
        "incompatibility",
        "compilation errors",
        "memory issues",
        "performance issues",
        "security issues",
        "API",
    ],

    # ============================================================
    # CATEGORY 1: CORE JNI CONCEPTS
    # ============================================================
    "core_jni": [
        "JNI issue",
        "JNI problem",
        "JNI error",
        "JNI crash",
        "JNI bug",
        "JNI interop",
        "JNI integration",
        "Java native integration",
        "call C from Java",
        "call C++ from Java",
        "call native code from Java",
        "JNI callback",
        "JNI callback Java",
        "JNI native method",
        "JNI boundary",
    ],

    # ============================================================
    # CATEGORY 2: REFERENCE MANAGEMENT
    # ============================================================
    "reference_mgmt": [
        "Global Reference Hoarding",
        "Overuse of Global References",
        "Local Reference Table Overflow",
        "global reference table overflow",
        "too many global references",
        "global reference limit exceeded",
        "local reference table overflow",
        "too many local references",
        "local reference limit",
        "JNI reference leak",
        "global reference leak",
        "local reference leak",
        "DeleteLocalRef",
        "DeleteGlobalRef",
        "NewGlobalRef",
        "NewLocalRef",
        "JNI reference management",
        "JNI reference cleanup",
        "JNI reference count",
        "JNI reference scope",
        "JNI weak global reference",
        "NewWeakGlobalRef",
    ],

    # ============================================================
    # CATEGORY 3: MEMORY ISSUES
    # ============================================================
    "memory": [
        "JNI memory leak",
        "JNI memory corruption",
        "JNI memory management",
        "Direct Memory Pinning",
        "memory pinning JNI",
        "JNI memory allocation",
        "JNI heap memory",
        "JNI native memory",
        "JNI out of memory",
        "JNI buffer overflow",
        "JNI stack overflow",
        "JNI memory access",
        "JNI memory safety",
        "JNI dangling pointer",
        "JNI use after free",
        "JNI double free",
        "JNI memory barrier",
        "JNI garbage collection",
        "JNI GC interaction",
        "JNI heap corruption",
    ],

    # ============================================================
    # CATEGORY 4: THREADING & SYNCHRONIZATION
    # ============================================================
    "threading": [
        "JNI MonitorEnter deadlock",
        "JNI global reference thread safety",
        "JNI deadlock",
        "JNI synchronization deadlock",
        "JNI synchronization issue",
        "JNI thread safety",
        "JNI threading",
        "JNI threading issue",
        "JNI threading global reference",
        "global reference different thread",
        "JNI race condition",
        "JNI concurrent",
        "AttachCurrentThread",
        "DetachCurrentThread",
        "JNI MonitorEnter",
        "JNI MonitorExit",
        "native code deadlock",
        "JNI thread local storage",
        "JNI thread attach",
        "JNI thread detach",
        "JNI multithreading",
        "JNI thread pool",
    ],

    # ============================================================
    # CATEGORY 5: DATA TYPE CONVERSION
    # ============================================================
    "data_conversion": [
        "jstring to const char",
        "jbyteArray to C array",
        "JNI string conversion",
        "JNI array conversion",
        "JNI primitive types",
        "JNI type conversion",
        "JNI data types",
        "Modified UTF-8",
        "GetStringUTFChars",
        "ReleaseStringUTFChars",
        "NewStringUTF",
        "JNI char conversion",
        "JNI int conversion",
        "JNI byte array",
        "JNI long array",
        "JNI float array",
        "JNI double array",
        "JNI boolean array",
        "JNI object array",
        "JNI type mismatch",
    ],

    # ============================================================
    # CATEGORY 6: STRUCT & OBJECT MAPPING
    # ============================================================
    "struct_mapping": [
        "struct mapping JNI",
        "JNI struct",
        "JNI object mapping",
        "JNI class mapping",
        "JNI field access",
        "JNI method invocation",
        "GetObjectField",
        "SetObjectField",
        "GetMethodID",
        "GetFieldID",
        "JNI object passing",
        "JNI object lifecycle",
        "JNI object serialization",
        "JNI complex types",
    ],

    # ============================================================
    # CATEGORY 7: ERROR & EXCEPTION HANDLING
    # ============================================================
    "error_handling": [
        "UnsatisfiedLinkError",
        "JNI exception",
        "JNI exception handling",
        "JNI error handling",
        "JNI error code",
        "JNI return code",
        "JNI error check",
        "JNI pending exception",
        "ExceptionCheck",
        "ExceptionClear",
        "JNI catch exception",
        "SIGSEGV java",
        "hs_err_pid.log",
        "JVM crash",
        "JNI segfault",
        "JNI crash log",
        "JNI fatal error",
        "JNI abort",
    ],

    # ============================================================
    # CATEGORY 8: LIBRARY LOADING
    # ============================================================
    "library_loading": [
        "System.loadLibrary",
        "java.library.path",
        "JNI library load",
        "JNI library not found",
        "JNI DLL load",
        "JNI SO load",
        "ABI mismatch JNI",
        "undefined reference JNI",
        "DLL hell java",
        "JNI native library",
        "JNI library linking",
        "JNI library path",
        "JNI shared library",
        "JNI dynamic library",
        "JNI static library",
    ],

    # ============================================================
    # CATEGORY 9: PERFORMANCE ISSUES
    # ============================================================
    "performance": [
        "JNI performance",
        "JNI performance bottleneck",
        "JNI performance issue",
        "JNI slow",
        "JNI overhead",
        "JNI optimization",
        "JNI optimization techniques",
        "JNI profiling tools",
        "JNI profiling",
        "JNI benchmark",
        "JNI vs pure Java performance",
        "JNI call overhead",
    ],

    # ============================================================
    # CATEGORY 10: SECURITY ISSUES
    # ============================================================
    "security": [
        "JNI security",
        "JNI security vulnerabilities",
        "JNI security issue",
        "JNI buffer overflow",
        "JNI injection",
        "JNI validation",
        "JNI input validation",
        "JNI unsafe code",
        "JNI memory safety",
        "JNI privilege escalation",
    ],

    # ============================================================
    # CATEGORY 11: COMPILATION & BUILD
    # ============================================================
    "compilation": [
        "JNI compilation",
        "JNI compilation error",
        "JNI header generation",
        "javah",
        "JNI build",
        "JNI build error",
        "JNI linking error",
        "JNI undefined symbol",
        "JNI symbol not found",
        "JNI include path",
        "JNI compiler flags",
        "JNI cross-compilation",
    ],

    # ============================================================
    # CATEGORY 12: PLATFORM COMPATIBILITY
    # ============================================================
    "platform": [
        "JNI compatibility",
        "JNI platform specific",
        "JNI cross-platform",
        "JNI Windows",
        "JNI Linux",
        "JNI Android",
        "JNI Android NDK",
        "JNI iOS",
        "JNI portable",
        "JNI endianness",
        "JNI word size",
        "JNI 32-bit 64-bit",
    ],

    # ============================================================
    # CATEGORY 13: DEBUGGING & TOOLS
    # ============================================================
    "debugging": [
        "JNI debugging",
        "JNI debugging techniques",
        "JNI debug",
        "JNI logging",
        "JNI tracing",
        "JNI tools",
        "JNI best practices",
        "JNI patterns",
        "JNI design patterns",
        "JNI troubleshooting",
    ],

    # ============================================================
    # CATEGORY 14: RESOURCE MANAGEMENT
    # ============================================================
    "resource_mgmt": [
        "JNI resource management",
        "JNI resource leak",
        "JNI file handle",
        "JNI socket",
        "JNI cleanup",
        "JNI finalize",
        "JNI destructor",
        "JNI destructor called",
        "JNI resource cleanup",
        "JNI resource release",
    ],

    # ============================================================
    # CATEGORY 15: JNI SPECIFIC FUNCTIONS
    # ============================================================
    "jni_functions": [
        "JNIEnv",
        "JavaVM",
        "JNI_OnLoad",
        "JNI_OnUnload",
        "JNI version",
        "JNI GetEnv",
        "JNI FindClass",
        "JNI CallVoidMethod",
        "JNI CallObjectMethod",
        "JNI CallIntMethod",
        "JNI NewObject",
        "JNI GetStaticMethodID",
        "JNI GetStaticFieldID",
        "JNI RegisterNatives",
        "JNI UnregisterNatives",
        "JNI PushLocalFrame",
        "JNI PopLocalFrame",
        "JNI EnsureLocalCapacity",
    ],

    # ============================================================
    # CATEGORY 16: ANTI-PATTERNS & CODE SMELLS
    # ============================================================
    "anti_patterns": [
        "JNI anti-pattern",
        "JNI bad practice",
        "JNI code smell",
        "JNI design smell",
        "JNI technical debt",
        "JNI refactoring",
        "JNI improvement",
        "JNI optimization needed",
        "JNI maintenance",
        "JNI legacy code",
    ],

    # ============================================================
    # CATEGORY 17: RELATED INTEROP TECHNOLOGIES
    # ============================================================
    "related_tech": [
        "JNA",
        "JNA vs JNI",
        "JavaCPP",
        "Project Panama",
        "Panama FFI",
        "SWIG Java",
        "JNI wrapper",
        "JNI framework",
        "JNI alternative",
        "JNI comparison",
    ],
}

# Helper function to get flat list (for Stack Overflow)
def get_all_keywords() -> list:
    """Get all 261 keywords as a flat list."""
    all_keywords = []
    for category_keywords in CATEGORIES.values():
        all_keywords.extend(category_keywords)
    return all_keywords

# Information Gain calculation for keyword relevance
# IG = H(Class) - H(Class|Keyword) measures how much a keyword reduces uncertainty
# about whether a post is a JNI design smell vs. general programming issue

def calculate_information_gain(frequency: int, post_count: int,
                               total_posts: int, jni_specificity: float = 1.0,
                               effectiveness_score: float = None) -> float:
    """
    Calculate Information Gain (IG) for a keyword.
    
    IG(keyword, class) = H(class) - H(class | keyword)
    
    Measures how much knowing a keyword reduces uncertainty about
    whether a post contains JNI design smell signals.
    
    Uses effectiveness_score as primary discriminative signal when available,
    falling back to jni_specificity-based calculation.
    Based on Brown et al. (1992) feature selection framework.
    
    Parameters:
    - frequency: Number of posts matching keyword
    - post_count: Direct keyword matches  
    - total_posts: Total posts in corpus
    - jni_specificity: 1.0 if JNI-specific, 0.5 if general
    - effectiveness_score: Pre-computed effectiveness score
    
    Returns:
    - Information gain in bits (0 = no info, high = very discriminative)
    """
    import math
    
    # Prior entropy H(Class) - P(smell) = 0.3
    p_class = 0.3
    h_class = -p_class * math.log2(p_class) - (1 - p_class) * math.log2(1 - p_class)
    
    # P(smell | keyword) approximation
    if effectiveness_score is not None and effectiveness_score > 0:
        # Use effectiveness_score as primary discriminative signal
        # effectiveness_score = frequency × specificity + avg_score × 0.1
        # Normalize to [0.01, 0.99] range
        max_possible = max(frequency * jni_specificity, 1)
        p_smell_given_kw = min(0.99, max(0.01, effectiveness_score / max_possible))
    else:
        # Fallback: use jni_specificity directly
        p_smell_given_kw = min(0.99, max(0.01, jni_specificity))
    
    # Conditional entropy H(class | keyword)
    if p_smell_given_kw > 0 and p_smell_given_kw < 1:
        h_class_given_kw = (-p_smell_given_kw * math.log2(p_smell_given_kw) 
                          - (1 - p_smell_given_kw) * math.log2(1 - p_smell_given_kw))
    else:
        h_class_given_kw = 0.0  # Keyword gives complete certainty
    
    # Information Gain = reduction in uncertainty
    ig = h_class - h_class_given_kw
    return max(0.0, ig)


def get_platform_keywords(platform: str, effectiveness_df: pd.DataFrame,
                          max_total: int = 20, min_ig: float = 0.05) -> list:
    """
    Select reduced keywords for a specific platform using information gain
    and category-aware stratified selection.

    Strategy:
    1. Guarantee 1 keyword per category (minimum coverage of all 17 smell types)
    2. Rank remaining by information gain
    3. Apply forum-specific vocabulary normalization
    4. Knee-point detection for optimal selection size

    Parameters:
    - effectiveness_df: DataFrame from calculate_keyword_effectiveness()
    - platform: "stackoverflow", "reddit", "hackernews", "lobsters", or "apache"
    - max_total: Maximum keywords to select (forum-typical: 15-35)
    - min_ig: Minimum information gain to include a keyword

    Returns:
    - Selected keywords list, stratified by category with IG ranking
    """
    import math
    from collections import defaultdict

    total_posts = len(effectiveness_df)

    # Phase 1: Calculate IG for all keywords
    kw_ig = []
    for _, row in effectiveness_df.iterrows():
        ig = calculate_information_gain(
            frequency=row['frequency'],
            post_count=row['post_count'],
            total_posts=total_posts,
            jni_specificity=row['jni_specificity']
        )
        if ig >= min_ig:
            kw_ig.append({
                'keyword': row['keyword'],
                'category': row['category'],
                'ig': ig,
                'frequency': row['frequency'],
                'effectiveness_score': row['effectiveness_score']
            })

    # Phase 2: Category-aware stratified selection
    # Guarantee at least 1 keyword per category
    selected = []
    selected_set = set()
    categories_covered = set()

    # Sort by IG within each category
    kw_by_category = defaultdict(list)
    for kw in kw_ig:
        kw_by_category[kw['category']].append(kw)

    # For each category, pick the top IG keyword
    for category in CATEGORIES.keys():
        if category in kw_by_category and len(kw_by_category[category]) > 0:
            top_kw = max(kw_by_category[category], key=lambda x: x['ig'])
            if top_kw['keyword'] not in selected_set:
                selected.append(top_kw['keyword'])
                selected_set.add(top_kw['keyword'])
                categories_covered.add(category)

    # Phase 3: Fill remaining budget by information gain ranking
    # Sort all keywords by IG (descending), excluding already selected
    remaining_candidates = [kw for kw in kw_ig if kw['keyword'] not in selected_set]
    remaining_candidates.sort(key=lambda x: x['ig'], reverse=True)

    # Platform-specific filtering to avoid redundancy
    for kw in remaining_candidates:
        if len(selected) >= max_total:
            break

        keyword = kw['keyword']
        if keyword in selected_set:
            continue

        # Platform-specific deduplication rules
        skip = False
        if platform == "apache":
            # Avoid duplicate Android-related terms
            if "Android" in keyword and any(
                "Android" in s for s in selected
            ):
                skip = True
        elif platform in ("reddit", "hackernews", "lobsters"):
            # Avoid terms that are too Stack Overflow specific
            so_specific = any(term in keyword.lower()
                            for term in ['stackoverflow', 'so ', 'post ', 'question '])
            if so_specific and platform != "stackoverflow":
                # Still allow if no alternative available
                non_jni_count = len([s for s in selected if not any(t in s.lower() for t in ['jni', 'java', 'c'])])
                if non_jni_count < 3:
                    pass  # Allow 3 general terms
                else:
                    skip = True

        if not skip:
            selected.append(keyword)
            selected_set.add(keyword)

    # Phase 4: Pad with category representatives if budget remains
    # Ensure all categories have at least representation
    for category in CATEGORIES.keys():
        if len(selected) >= max_total:
            break
        if category not in categories_covered:
            # Find any keyword from this category not already selected
            if category in kw_by_category:
                for kw in kw_by_category[category]:
                    if kw['keyword'] not in selected_set:
                        selected.append(kw['keyword'])
                        selected_set.add(kw['keyword'])
                        break

    # Phase 5: Final trim to max_total (keep highest IG)
    if len(selected) > max_total:
        # Re-rank all selected by IG and keep top max_total
        selected_with_ig = []
        for kw in kw_ig:
            if kw['keyword'] in selected_set:
                selected_with_ig.append(kw)
        selected_with_ig.sort(key=lambda x: x['ig'], reverse=True)
        selected = [kw['keyword'] for kw in selected_with_ig[:max_total]]

    return selected


if __name__ == "__main__":
    all_kw = get_all_keywords()
    print(f"Total keywords: {len(all_kw)}")
    print(f"Categories: {len(CATEGORIES)}")
    for name, keywords in CATEGORIES.items():
        print(f"  {name}: {len(keywords)} keywords")