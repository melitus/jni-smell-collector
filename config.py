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
