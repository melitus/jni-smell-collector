import os

# Local output directory
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# PHASE 1: FORUM MINING
# ============================================================

# Phase 1A: Baseline Forums (matching paper exactly)
PHASE1_BASELINE_KEYWORDS = [
    "JNI issue", "Python/C issue", "foreign library", "foreign function interface",
    "polyglot", "programming languages issues", "incompatibility", "compilation errors",
    "memory issues", "performance issues", "security issues", "API"
]

PHASE1_BASELINE_FORUMS = [
    {"name": "Stack Overflow", "site": "stackoverflow.com", "method": "stackexchange"},
    {"name": "GitHub Issues", "site": "github.com", "method": "github"},
    {"name": "Bugzilla", "site": "bugzilla.mozilla.org", "method": "bugzilla_api"},
]

# Phase 1B: Extension Forums (your contribution)
PHASE1_EXTENSION_KEYWORDS = [
    # Memory/Lifecycle
    "JNI memory leak", "DeleteLocalRef", "global reference leak", "Overuse of Global References",
    "Local Reference Table Overflow", "Global Reference Hoarding",
    # Crashes/Boundary
    "UnsatisfiedLinkError", "SIGSEGV java", "hs_err_pid.log", "JVM crash",
    # Data Translation
    "Modified UTF-8", "jstring to const char", "jbyteArray to C array",
    "Silent String Corruption", "Direct Memory Pinning", "struct mapping JNI",
    # Build/Link
    "java.library.path", "System.loadLibrary", "ABI mismatch JNI", "undefined reference JNI", "DLL hell java",
    # Concurrency
    "JNI MonitorEnter deadlock", "AttachCurrentThread", "JNI global reference thread safety"
]

PHASE1_EXTENSION_FORUMS = [
    # Baseline forums (for comparison)
    {"name": "Stack Overflow", "site": "stackoverflow.com", "method": "stackexchange"},
    {"name": "GitHub Issues", "site": "github.com", "method": "github"},
    {"name": "Bugzilla", "site": "bugzilla.mozilla.org", "method": "bugzilla_api"},
    # Extension forums (your contribution)
    {"name": "Microsoft Q&A", "site": "learn.microsoft.com", "method": "microsoft_qa_api"},  # <-- CHANGED from "fallback"
    {"name": "Oracle Community", "site": "community.oracle.com", "method": "fallback"},
    {"name": "Reddit", "site": "reddit.com", "method": "reddit_json"},
    {"name": "Hacker News", "site": "news.ycombinator.com", "method": "hn_api"},
    {"name": "LLVM Discourse", "site": "discourse.llvm.org", "method": "llvm_api"},
    {"name": "Apache Lists", "site": "lists.apache.org", "method": "apache_api"},
    {"name": "Lobsters", "site": "lobste.rs", "method": "lobsters_api"},
]

# ============================================================
# PHASE 2: DOCUMENTATION EXTRACTION
# ============================================================

# Official documentation URLs to extract anti-patterns from
PHASE2_DOCUMENTATION_URLS = [
    {
        "name": "IBM DeveloperWorks JNI Article",
        "url": "https://www.ibm.com/developerworks/library/j-jni/index.html",
        "type": "article"
    },
    {
        "name": "Android JNI Performance Guide",
        "url": "https://developer.android.com/training/articles/perf-jni",
        "type": "guide"
    },
    {
        "name": "Android JNI Tips",
        "url": "https://developer.android.com/ndk/guides/jni-tips",
        "type": "guide"
    },
    {
        "name": "Oracle JNI Specification",
        "url": "https://docs.oracle.com/javase/8/docs/technotes/guides/jni/spec/jniTOC.html",
        "type": "specification"
    },
]

# ============================================================
# PHASE 3: SOURCE CODE ANALYSIS
# ============================================================

# 10 baseline systems to analyze (matching paper)
PHASE3_BASELINE_REPOS = [
    "https://github.com/google/conscrypt.git",
    "https://github.com/libgdx/libgdx.git",
    "https://github.com/eclipse-openj9/openj9.git",
    "https://github.com/facebook/react-native.git",
    "https://github.com/realm/realm-java.git",
    "https://github.com/bytedeco/javacpp.git",
    "https://github.com/java-native-access/jna.git",
    "https://github.com/LWJGL/lwjgl3.git",
    "https://github.com/ArtifexSoftware/mupdf.git",  # Replaced 7zip (not on GitHub)
    "https://github.com/videolan/vlc.git",
]

STACKEXCHANGE_API_KEY = "rl_6tCCJohCUSHcN8kVcghTNeoRd"

# Optimized keywords for re-mining scripts (comprehensive catalog)
OPTIMIZED_KEYWORDS = [
    # ============================================================
    # CATEGORY 0: BASELINE KEYWORDS (For Scientific Comparison)
    # Purpose: Control group to compare against JNI-specific results
    # These represent GENERAL cross-language/programming issues
    # ============================================================
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

    # ============================================================
    # CATEGORY 1: CORE JNI CONCEPTS (15 keywords)
    # ============================================================
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

    # ============================================================
    # CATEGORY 2: REFERENCE MANAGEMENT - Core Design Smells (22 keywords)
    # ============================================================
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

    # ============================================================
    # CATEGORY 3: MEMORY ISSUES (20 keywords)
    # ============================================================
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

    # ============================================================
    # CATEGORY 4: THREADING & SYNCHRONIZATION (22 keywords)
    # ============================================================
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

    # ============================================================
    # CATEGORY 5: DATA TYPE CONVERSION (20 keywords)
    # ============================================================
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

    # ============================================================
    # CATEGORY 6: STRUCT & OBJECT MAPPING (14 keywords)
    # ============================================================
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

    # ============================================================
    # CATEGORY 7: ERROR & EXCEPTION HANDLING (18 keywords)
    # ============================================================
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

    # ============================================================
    # CATEGORY 8: LIBRARY LOADING (15 keywords)
    # ============================================================
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

    # ============================================================
    # CATEGORY 9: PERFORMANCE ISSUES (12 keywords)
    # ============================================================
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

    # ============================================================
    # CATEGORY 10: SECURITY ISSUES (10 keywords)
    # ============================================================
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

    # ============================================================
    # CATEGORY 11: COMPILATION & BUILD (12 keywords)
    # ============================================================
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

    # ============================================================
    # CATEGORY 12: PLATFORM COMPATIBILITY (12 keywords)
    # ============================================================
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

    # ============================================================
    # CATEGORY 13: DEBUGGING & TOOLS (10 keywords)
    # ============================================================
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

    # ============================================================
    # CATEGORY 14: RESOURCE MANAGEMENT (10 keywords)
    # ============================================================
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

    # ============================================================
    # CATEGORY 15: JNI SPECIFIC FUNCTIONS (18 keywords)
    # ============================================================
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

    # ============================================================
    # CATEGORY 16: ANTI-PATTERNS & CODE SMELLS (10 keywords)
    # ============================================================
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

    # ============================================================
    # CATEGORY 17: RELATED INTEROP TECHNOLOGIES (10 keywords)
    # ============================================================
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
]

# Tags for Stack Overflow search (same as scraper.py default behavior)
STACKOVERFLOW_TAGS = "java-native-interface;Java Native Interface;jni;JNI;jniwrapper;jna;FFI;native interop" 
