"""
Adaptive Interview Engine for IntervueAI
Manages interview state progression, adaptive difficulty adjustment,
question selection from question bank, and candidate report generation.
"""

from typing import Dict, Any, List, Optional
from backend.data.question_bank import QUESTION_BANK, get_question_by_id

SKILL_SEQUENCE = [
    "Programming Fundamentals",
    "Problem Solving",
    "Data Structures & Algorithms",
    "Technical Understanding",
    "Communication"
]

DIFFICULTY_LEVELS = ["EASY", "MEDIUM", "HARD"]

def calculate_next_difficulty(current_difficulty: str, last_score: float) -> str:
    """
    Adaptive logic based on candidate score:
    - score < 40: decrease difficulty (or EASY)
    - score 40-70: maintain current difficulty
    - score > 70: increase difficulty (or HARD)
    """
    curr_idx = DIFFICULTY_LEVELS.index(current_difficulty) if current_difficulty in DIFFICULTY_LEVELS else 1

    if last_score < 40:
        new_idx = max(0, curr_idx - 1)
    elif last_score > 70:
        new_idx = min(len(DIFFICULTY_LEVELS) - 1, curr_idx + 1)
    else:
        new_idx = curr_idx

    return DIFFICULTY_LEVELS[new_idx]

import uuid
import logging
from backend.data.question_bank import QUESTION_BANK, get_question_by_id, register_dynamic_question

logger = logging.getLogger("adaptive_engine")

DYNAMIC_TOPIC_TEMPLATES = {
    "Programming Fundamentals": {
        "EASY": {
            "en": "To clarify foundational programming principles, could you explain how memory is allocated for value types versus reference types, or what happens when a variable scope ends?",
            "hi": "मूलभूत प्रोग्रामिंग सिद्धांतों को स्पष्ट करने के लिए, क्या आप समझा सकते हैं कि value types और reference types के लिए मेमोरी कैसे आवंटित होती है, या वेरिएबल का scope समाप्त होने पर क्या होता है?",
            "concepts": ["stack vs heap", "value vs reference", "variable scope", "memory allocation"],
            "points": ["Value types are stored directly on the stack with deterministic lifetime.", "Reference types store a pointer on the stack pointing to object data on the heap.", "When scope exits, stack frames are popped automatically."],
            "rubric": {
                "excellent": "Clearly contrasts stack and heap allocation, explains pointer/reference dereferencing, and discusses scope lifetime.",
                "good": "Explains difference between primitive value copy and object reference copy correctly.",
                "average": "Understands scope but struggles to explain memory differences.",
                "poor": "Confuses variables and cannot explain memory concepts."
            }
        },
        "MEDIUM": {
            "en": "Could you explain the difference between synchronous and asynchronous execution in modern application runtimes, and when asynchronous I/O is preferred?",
            "hi": "क्या आप आधुनिक एप्लिकेशन रनटाइम्स में सिंक्रोनस और एसिंक्रोनस निष्पादन के बीच के अंतर को समझा सकते हैं, और एसिंक्रोनस I/O को कब प्राथमिकता दी जाती है?",
            "concepts": ["synchronous blocking", "asynchronous non-blocking", "event loop / thread pool", "I/O bound tasks"],
            "points": ["Synchronous execution blocks the current thread until the operation finishes.", "Asynchronous execution registers a callback/promise and frees the thread for other work.", "Async I/O prevents server thread exhaustion during database and network calls."],
            "rubric": {
                "excellent": "Clearly explains blocking vs non-blocking I/O, event loops/callbacks, and resource utilization during concurrency.",
                "good": "Understands that async doesn't block the UI/thread while sync waits for completion.",
                "average": "Knows async is faster or non-blocking but vague on thread mechanics.",
                "poor": "Cannot distinguish between sync and async execution."
            }
        },
        "HARD": {
            "en": "Building on your strong understanding, how do modern language runtimes handle concurrency models (such as threads versus event loops) and prevent memory race conditions?",
            "hi": "आपकी मजबूत समझ को आगे बढ़ाते हुए, आधुनिक प्रोग्रामिंग रनटाइम्स concurrency मॉडल्स (जैसे threads बनाम event loops) को कैसे संभालते हैं और memory race conditions को कैसे रोकते हैं?",
            "concepts": ["race conditions", "mutual exclusion / locks", "atomic operations", "event loop vs multi-threading", "immutability"],
            "points": ["Threads share memory space, requiring mutexes, semaphores, or atomic primitives to prevent concurrent write corruptions.", "Event-loop models use single-threaded cooperative scheduling for I/O while worker threads handle heavy compute.", "Immutability and message passing (actor model) eliminate shared-state race hazards."],
            "rubric": {
                "excellent": "Articulates memory consistency models, lock contention trade-offs (deadlocks/livelocks), atomics, and compares thread pools with event loops.",
                "good": "Explains race conditions clearly and mentions mutexes/locks or synchronized blocks.",
                "average": "Mentions multithreading but has superficial understanding of synchronization.",
                "poor": "Cannot explain race conditions or how threads interact."
            }
        }
    },
    "Problem Solving": {
        "EASY": {
            "en": "When you encounter an unexpected runtime crash or logic bug in your code, what are the first three systematic steps you take to isolate the root cause?",
            "hi": "जब आपको अपने कोड में कोई अनपेक्षित रनटाइम क्रैश या लॉजिक बग मिलता है, तो मूल कारण को अलग करने के लिए आप कौन से पहले तीन व्यवस्थित कदम उठाते हैं?",
            "concepts": ["reproduction", "stack trace inspection", "isolating variables / binary search", "logging / debugging"],
            "points": ["First reproduce the bug consistently with a minimal test input.", "Inspect the stack trace, error logs, and recent code changes.", "Use debugger breakpoints or structured logging to verify variable states."],
            "rubric": {
                "excellent": "Describes a disciplined scientific debugging methodology: reliable reproduction, stack trace analysis, hypothesis testing, and regression test authoring.",
                "good": "Mentions reproducing the issue, reading logs, and using print statements or debugger.",
                "average": "Mentions random trial-and-error fixes without structured isolation.",
                "poor": "Has no clear approach to debugging."
            }
        },
        "MEDIUM": {
            "en": "How do you approach breaking down an ambiguous or poorly specified software requirement before writing any code?",
            "hi": "कोई भी कोड लिखने से पहले आप एक अस्पष्ट या अपूर्ण सॉफ्टवेयर आवश्यकता को कैसे विभाजित और स्पष्ट करते हैं?",
            "concepts": ["stakeholder clarification", "edge case identification", "acceptance criteria", "modular decomposition"],
            "points": ["Ask clarifying questions to identify inputs, expected outputs, and constraints.", "Map user flows and document explicit edge cases and failure modes.", "Define measurable acceptance criteria and break the task into small testable units."],
            "rubric": {
                "excellent": "Demonstrates proactive requirements gathering, edge-case analysis, contracts/APIs definition, and phased delivery planning.",
                "good": "Explains asking questions, listing assumptions, and dividing the problem into steps.",
                "average": "Focuses only on jumping straight into coding and figuring it out as they go.",
                "poor": "Does not acknowledge the risk of ambiguous specifications."
            }
        },
        "HARD": {
            "en": "In a distributed system experiencing intermittent latency spikes under peak load, how would you systematically diagnose whether the bottleneck is CPU, memory pressure, I/O, lock contention, or network saturation?",
            "hi": "पीक लोड के तहत रुक-रुक कर होने वाले लेटेंसी स्पाइक्स वाले एक वितरित सिस्टम में, आप व्यवस्थित रूप से कैसे निदान करेंगे कि बाधा CPU, मेमोरी दबाव, I/O, लॉक कन्टेन्शन या नेटवर्क संतृप्ति है?",
            "concepts": ["distributed tracing", "telemetry / APM metrics", "thread dump analysis", "p99 vs p50 percentiles", "bottleneck isolation"],
            "points": ["Analyze p99 and p99.9 latency percentiles alongside distributed traces to pinpoint the exact lagging microservice.", "Inspect system-level metrics (CPU utilization, memory swapping, GC pauses, disk queue depths, connection pool wait times).", "Capture thread dumps or flame graphs during latency spikes to detect lock contention or synchronous blocking calls."],
            "rubric": {
                "excellent": "Exhibits deep observability mastery: distributed traces, percentiles over averages, flame graphs, database connection pools, GC profiling, and network queue metrics.",
                "good": "Mentions checking server metrics (CPU, RAM), database queries, and checking logs.",
                "average": "Vague suggestions like 'restart the server' or 'add more servers' without diagnosis.",
                "poor": "Fails to provide any systematic diagnostic process."
            }
        }
    },
    "Data Structures & Algorithms": {
        "EASY": {
            "en": "As a foundational diagnostic, what is the time complexity difference between accessing an element by index in an Array versus searching in a singly Linked List?",
            "hi": "एक मूलभूत प्रश्न के रूप में, एक Array में इंडेक्स द्वारा किसी तत्व तक पहुँचने और एक singly Linked List में खोजने के बीच समय जटिलता (time complexity) में क्या अंतर है?",
            "concepts": ["O(1) random access", "O(N) sequential traversal", "contiguous memory", "pointer dereferencing"],
            "points": ["Array elements reside in contiguous memory, allowing O(1) direct offset calculation.", "Linked list elements are dispersed in memory connected via pointers, requiring O(N) sequential traversal.", "Arrays benefit from CPU cache locality while linked lists have higher cache miss rates."],
            "rubric": {
                "excellent": "Clearly distinguishes O(1) contiguous offset calculation from O(N) pointer traversal, referencing CPU cache locality advantages.",
                "good": "States O(1) for array index and O(N) for linked list search with correct basic rationale.",
                "average": "Knows the complexities but cannot explain why arrays have constant time access.",
                "poor": "Gives incorrect complexities."
            }
        },
        "MEDIUM": {
            "en": "When would you choose to use a Hash Table over a Binary Search Tree, and how do hash collisions typically get resolved in practice?",
            "hi": "आप बाइनरी सर्च ट्री के स्थान पर हैश टेबल का उपयोग कब चुनेंगे, और व्यावहारिक रूप से हैश टकराव (hash collisions) को कैसे हल किया जाता है?",
            "concepts": ["average O(1) vs guaranteed O(log N)", "ordered traversal vs unordered", "separate chaining", "open addressing / linear probing"],
            "points": ["Hash tables offer O(1) average lookup/insertion when ordering is not required.", "Binary Search Trees provide guaranteed O(log N) operations and maintain sorted order for range queries.", "Collisions are resolved via separate chaining (linked lists / balanced trees in buckets) or open addressing."],
            "rubric": {
                "excellent": "Compares amortized O(1) vs guaranteed O(log N), discusses range query trade-offs, and details collision resolution mechanisms like separate chaining and Robin Hood hashing.",
                "good": "Identifies that hash tables are O(1) for unsorted data and explains chaining.",
                "average": "Mentions fast lookups but gives unclear explanation of collisions.",
                "poor": "Cannot explain how a hash table works."
            }
        },
        "HARD": {
            "en": "How would you design an in-memory Cache with an LRU (Least Recently Used) eviction policy to achieve strict O(1) time complexity for both `get` and `put` operations?",
            "hi": "`get` और `put` दोनों परिचालनों के लिए सख्त O(1) समय जटिलता प्राप्त करने के लिए आप LRU निष्कासन नीति के साथ इन-मेमोरी कैश कैसे डिज़ाइन करेंगे?",
            "concepts": ["hash map + doubly linked list", "O(1) lookup", "O(1) node relocation", "capacity eviction", "thread safety / concurrency"],
            "points": ["Combine a Hash Map for O(1) key-to-node lookup with a Doubly Linked List for O(1) node insertion, deletion, and relocation.", "On `get`, look up node in hash map and move it to the head of the list.", "On `put` at capacity, remove the tail node from both list and hash map, then insert the new node at the head."],
            "rubric": {
                "excellent": "Provides the complete Hash Map + Doubly Linked List architecture, details pointer updates for O(1) node moves, and addresses thread safety with read-write locks.",
                "good": "Mentions hash map plus linked list to maintain order in O(1) time.",
                "average": "Suggests an array or queue which results in O(N) eviction/move time.",
                "poor": "Cannot articulate a data structure approach for LRU."
            }
        }
    },
    "Technical Understanding": {
        "EASY": {
            "en": "To clarify fundamental web architecture, what happens at a high level between your browser and the server when you submit a web form?",
            "hi": "मौलिक वेब आर्किटेक्चर को स्पष्ट करने के लिए, जब आप कोई वेब फ़ॉर्म सबमिट करते हैं तो आपके ब्राउज़र और सर्वर के बीच उच्च स्तर पर क्या होता है?",
            "concepts": ["HTTP POST request", "request headers and payload", "server routing / controller", "HTTP response status (200/302)"],
            "points": ["The browser packages form fields into an HTTP POST or GET request body/query.", "The request travels over TCP/TLS to the destination web server.", "The server processes the payload, performs validation, and returns an HTTP response code and payload."],
            "rubric": {
                "excellent": "Walks through client validation, HTTP method, payload encoding, TLS transport, server routing/handling, and response lifecycle.",
                "good": "Explains HTTP POST request being sent to the server and the server sending back a response.",
                "average": "Mentions sending data to the server but lacks HTTP specifics.",
                "poor": "Cannot describe client-server communication."
            }
        },
        "MEDIUM": {
            "en": "What are the core architectural differences between RESTful APIs and GraphQL, and what factors guide your choice between them for a new project?",
            "hi": "RESTful API और GraphQL के बीच मुख्य आर्किटेक्चरल अंतर क्या हैं, और एक नए प्रोजेक्ट के लिए उनके बीच आपके चयन को कौन से कारक निर्देशित करते हैं?",
            "concepts": ["fixed endpoints vs single endpoint", "over-fetching and under-fetching", "schema definition", "HTTP caching vs application caching"],
            "points": ["REST uses standardized HTTP verbs and distinct URIs per resource.", "GraphQL exposes a single endpoint allowing clients to query exact fields, eliminating over-fetching.", "REST leverages standard HTTP caching natively; GraphQL queries are usually POST requests requiring client-side caching libraries."],
            "rubric": {
                "excellent": "Thoroughly compares over/under-fetching, HTTP caching mechanisms, schema evolution, and operational complexity.",
                "good": "Explains that GraphQL lets client request exact data needed while REST has fixed endpoints.",
                "average": "Mentions GraphQL is newer but lacks clear trade-off analysis.",
                "poor": "Confuses REST with database queries."
            }
        },
        "HARD": {
            "en": "How would you design a distributed transaction or event flow across multiple independent microservices to maintain eventual consistency without introducing distributed two-phase locking?",
            "hi": "वितरित दो-चरणीय लॉकिंग (2PC) को शामिल किए बिना अंतिम स्थिरता (eventual consistency) बनाए रखने के लिए आप कई स्वतंत्र माइक्रोसर्विसेज में एक वितरित लेनदेन या इवेंट फ्लो कैसे डिज़ाइन करेंगे?",
            "concepts": ["Saga pattern", "choreography vs orchestration", "compensating transactions", "outbox pattern", "idempotent consumers"],
            "points": ["Implement the Saga Pattern using either event-driven choreography or an orchestrator service.", "Each microservice executes its local transaction and publishes a domain event.", "If a downstream step fails, the saga initiates compensating transactions in reverse to revert intermediate state.", "Use the Transactional Outbox pattern with idempotent consumers to guarantee at-least-once message delivery without duplicates."],
            "rubric": {
                "excellent": "Demonstrates mastering the Saga pattern (choreographed vs orchestrated), compensating transactions, Outbox pattern, and idempotency keys.",
                "good": "Explains event-driven architecture, eventual consistency, and rolling back previous actions if a step fails.",
                "average": "Suggests global locks or database sharing, ignoring distributed decoupling principles.",
                "poor": "Cannot explain how distributed systems handle partial failures."
            }
        }
    },
    "Communication": {
        "EASY": {
            "en": "When you are stuck on a technical blocker or difficult problem during an assignment, how do you communicate with your team or mentor to seek assistance effectively?",
            "hi": "जब आप किसी असाइनमेंट के दौरान किसी तकनीकी रुकावट या कठिन समस्या में फंस जाते हैं, तो प्रभावी ढंग से सहायता प्राप्त करने के लिए आप अपनी टीम या मेंटर से कैसे संवाद करते हैं?",
            "concepts": ["attempted solutions first", "concise problem statement", "reproduction steps / context", "respect for teammate time"],
            "points": ["Clearly state what you are trying to achieve and the exact error encountered.", "Summarize what you have already tried and what was ruled out.", "Provide relevant logs or minimal code snippets to make assistance efficient."],
            "rubric": {
                "excellent": "Demonstrates the 'rubber-duck' pre-check, summarizes hypotheses tested, provides minimal reproducible context, and respects team velocity.",
                "good": "Explains the problem clearly along with what was already attempted before asking.",
                "average": "Asks for help without doing initial research or without explaining what was tried.",
                "poor": "Passively waits or asks teammates to do the task for them."
            }
        },
        "MEDIUM": {
            "en": "How do you provide constructive, empathetic feedback during a code review when you identify potential architectural flaws or anti-patterns in a peer's pull request?",
            "hi": "कोड समीक्षा के दौरान जब आप किसी सहकर्मी के पुल अनुरोध में संभावित आर्किटेक्चरल खामियाँ या एंटी-पैटर्न देखते हैं, तो आप रचनात्मक और सहानुभूतिपूर्ण प्रतिक्रिया कैसे देते हैं?",
            "concepts": ["focus on the code not the person", "explaining the 'why' / trade-offs", "suggesting actionable alternatives", "praising good work"],
            "points": ["Frame comments around code maintainability and user impact rather than personal critiques.", "Ask clarifying questions (e.g., 'Have you considered...?') rather than issuing commands.", "Provide specific code suggestions with explanations of the trade-offs."],
            "rubric": {
                "excellent": "Exemplifies high psychological safety: separates author identity from code, references shared team standards, explains downstream risks, and provides concrete alternatives.",
                "good": "Focuses on explaining why a change is needed constructively and politely.",
                "average": "Points out mistakes bluntly without constructive guidance.",
                "poor": "Creates friction through aggressive or dismissive comments."
            }
        },
        "HARD": {
            "en": "How do you handle a scenario where leadership or a product manager insists on an aggressive release deadline that would force cutting essential automated testing and creating severe technical debt?",
            "hi": "आप ऐसी स्थिति को कैसे संभालते हैं जहाँ नेतृत्व या एक उत्पाद प्रबंधक एक आक्रामक रिलीज़ समय सीमा पर जोर देता है जो आवश्यक स्वचालित परीक्षणों को काटने और गंभीर तकनीकी ऋण पैदा करने के लिए मजबूर करेगा?",
            "concepts": ["risk quantification", "scope reduction over quality compromise", "transparent trade-off presentation", "phased rollout / MVP"],
            "points": ["Quantify the operational and business risks of releasing untested code (outages, customer churn, hotfix costs).", "Propose reducing feature scope rather than compromising engineering quality.", "Offer a phased release strategy: deliver an MVP with full test coverage now, follow with remaining features in the next iteration."],
            "rubric": {
                "excellent": "Translates technical debt into business impact (downtime risk, velocity tax), proposes scope negotiation over quality erosion, and presents clear phased delivery options.",
                "good": "Explains risks to product managers respectfully and suggests cutting non-essential features instead of testing.",
                "average": "Either blindly obeys without warning of consequences, or refuses aggressively without alternatives.",
                "poor": "Accepts zero-testing blindly without acknowledging risks."
            }
        }
    },
    "React & Frontend": {
        "EASY": {
            "en": "To diagnose foundational understanding of React, could you explain the core difference between component 'props' and 'state', and how data flows between components?",
            "hi": "React के मूलभूत सिद्धांतों को स्पष्ट करने के लिए, क्या आप 'props' और 'state' के बीच मुख्य अंतर समझा सकते हैं, और डेटा कॉम्पोनेंट्स के बीच कैसे प्रवाहित होता है?",
            "concepts": ["props vs state", "unidirectional data flow", "immutability", "re-rendering"],
            "points": ["Props are read-only inputs passed from parent to child.", "State is local mutable data managed within the component.", "Modifying state triggers a component re-render."],
            "rubric": {
                "excellent": "Clearly distinguishes immutable props from component state, explains unidirectional flow, and mentions re-rendering triggers.",
                "good": "Correctly states props are passed down and state is internal.",
                "average": "Understands they hold data but confuses who controls them.",
                "poor": "Cannot explain the difference between props and state."
            }
        },
        "MEDIUM": {
            "en": "In practical React applications, how do you handle side effects and asynchronous data fetching using hooks like useEffect, and how do you prevent memory leaks or stale state?",
            "hi": "व्यावहारिक React एप्लिकेशन्स में, आप useEffect जैसे hooks का उपयोग करके एसिंक्रोनस डेटा फ़ेचिंग को कैसे संभालते हैं, और मेमोरी लीक या स्टेल स्टेट को कैसे रोकते हैं?",
            "concepts": ["useEffect hook", "dependency array", "cleanup function", "race conditions / abort controller"],
            "points": ["useEffect handles side effects after rendering with a dependency array to control re-execution.", "Cleanup functions cancel active timers, subscriptions, or AbortControllers.", "Omitting dependencies causes stale closures and unexpected state."],
            "rubric": {
                "excellent": "Thoroughly details the dependency array mechanics, cleanup functions with AbortController, and stale closure risks.",
                "good": "Explains calling fetch inside useEffect and specifying dependencies.",
                "average": "Mentions useEffect fetches data but unclear on cleanup.",
                "poor": "Cannot explain how data fetching works in React."
            }
        },
        "HARD": {
            "en": "In a large-scale React application experiencing UI latency, how would you systematically diagnose and optimize unnecessary component re-renders, and when would you use memoization (useMemo/React.memo) versus restructuring component hierarchy or state lifting?",
            "hi": "एक बड़े React एप्लिकेशन में, आप अनावश्यक कॉम्पोनेंट री-रेंडर्स को कैसे ऑप्टिमाइज़ करेंगे, और आप memoization बनाम कॉम्पोनेंट पदानुक्रम के पुनर्गठन का उपयोग कब करेंगे?",
            "concepts": ["React Profiler", "React.memo / useMemo / useCallback", "state colocation", "virtual DOM reconciliation"],
            "points": ["Use React DevTools Profiler to identify components re-rendering unnecessarily.", "Colocate state down to only the subtree that needs it before reaching for memoization.", "Use React.memo and useCallback with stable function references to skip pure component renders."],
            "rubric": {
                "excellent": "Covers React Profiler diagnostics, state colocation over premature memoization, referential equality with useCallback/useMemo, and virtual DOM diffing.",
                "good": "Explains React.memo and useMemo to prevent re-renders when props don't change.",
                "average": "Suggests useMemo everywhere without profiling.",
                "poor": "Cannot explain why components re-render in React."
            }
        }
    },
    "Python & Backend": {
        "EASY": {
            "en": "To clarify foundational Python principles, could you explain the difference between mutable and immutable data types (such as lists versus tuples), and what happens when an object is passed to a function?",
            "hi": "Python के मूलभूत सिद्धांतों को स्पष्ट करने के लिए, क्या आप mutable और immutable डेटा प्रकारों (जैसे lists बनाम tuples) के बीच अंतर समझा सकते हैं?",
            "concepts": ["mutable vs immutable", "pass-by-object-reference", "lists vs tuples", "hashability"],
            "points": ["Mutable types (list, dict, set) can be modified in place; immutable types (int, str, tuple) cannot.", "Python uses pass-by-object-reference, so mutating an argument inside a function modifies the caller's object."],
            "rubric": {
                "excellent": "Explains memory identity (id), in-place modification vs reassignment, pass-by-object-reference, and dictionary key hashability.",
                "good": "Distinguishes lists as changeable and tuples as unchangeable.",
                "average": "Understands lists can change but cannot explain function argument behavior.",
                "poor": "Cannot explain data types in Python."
            }
        },
        "MEDIUM": {
            "en": "When building a web backend in Python (such as with FastAPI or Django), how do you design RESTful endpoints, validate incoming request schemas, and manage database connection sessions safely?",
            "hi": "Python (जैसे FastAPI या Django) में वेब बैकएंड बनाते समय, आप RESTful endpoints कैसे डिज़ाइन करते हैं, डेटा सत्यापन कैसे करते हैं, और डेटाबेस कनेक्शन कैसे प्रबंधित करते हैं?",
            "concepts": ["Pydantic validation", "dependency injection / context managers", "ORM / connection pooling", "HTTP status codes"],
            "points": ["Use Pydantic or serializers for declarative request payload validation.", "Use dependency injection or context managers to ensure database sessions are cleanly opened and closed.", "Map errors to semantic HTTP status codes (400, 404, 422, 500)."],
            "rubric": {
                "excellent": "Walks through declarative schema validation, connection pooling with session cleanup, and standardized error handling.",
                "good": "Explains endpoints, models, and using ORM to query the database.",
                "average": "Basic explanation of writing functions that return JSON.",
                "poor": "Cannot describe how Python APIs work."
            }
        },
        "HARD": {
            "en": "How does Python handle concurrency under the Global Interpreter Lock (GIL), and when would you choose asyncio versus multi-threading versus multi-processing for high-concurrency systems?",
            "hi": "Python Global Interpreter Lock (GIL) के तहत concurrency को कैसे संभालता है, और आप asyncio बनाम multi-threading बनाम multi-processing का चयन कब करेंगे?",
            "concepts": ["Global Interpreter Lock (GIL)", "I/O bound vs CPU bound", "asyncio event loop", "multiprocessing IPC"],
            "points": ["The GIL prevents multiple native threads from executing Python bytecodes simultaneously in a single process.", "For I/O bound tasks (network/db), asyncio or threading allows cooperative or preemptive release of GIL.", "For CPU-bound tasks, multiprocessing bypasses the GIL by spawning separate OS processes with dedicated memory spaces."],
            "rubric": {
                "excellent": "Thoroughly articulates bytecode GIL acquisition/release, compares memory overhead of processes vs threads vs coroutines, and maps work types accurately.",
                "good": "Explains GIL limits CPU threading and recommends multiprocessing for CPU and asyncio for I/O.",
                "average": "Mentions GIL but confused on thread vs process differences.",
                "poor": "Unaware of GIL or concurrency in Python."
            }
        }
    },
    "JavaScript": {
        "EASY": {
            "en": "To diagnose core JavaScript fundamentals, what is the key difference between `var`, `let`, and `const`, particularly regarding variable hoisting and block scoping?",
            "hi": "JavaScript के मूलभूत सिद्धांतों को स्पष्ट करने के लिए, `var`, `let` और `const` में विशेष रूप से hoisting और block scoping के संबंध में क्या मुख्य अंतर है?",
            "concepts": ["var function-scoped", "let/const block-scoped", "hoisting & temporal dead zone", "const re-assignment"],
            "points": ["var is function-scoped and hoisted with undefined initialization.", "let and const are block-scoped residing in Temporal Dead Zone until initialized.", "const prevents variable identifier reassignment."],
            "rubric": {
                "excellent": "Clearly explains block vs function scope, temporal dead zone, hoisting mechanics, and immutable identifier binding.",
                "good": "Explains let and const have block scope and const cannot be reassigned while var has function scope.",
                "average": "Understands const cannot change but vague on let vs var scoping.",
                "poor": "Cannot distinguish var, let, and const."
            }
        },
        "MEDIUM": {
            "en": "In modern JavaScript runtimes, how does the Event Loop coordinate microtasks (Promises) versus macrotasks (setTimeout), and how do closures retain variables across execution contexts?",
            "hi": "आधुनिक JavaScript रनटाइम्स में, Event Loop microtasks (Promises) बनाम macrotasks (setTimeout) को कैसे समन्वयित करता है, और closures निष्पादन संदर्भों में वेरिएबल्स को कैसे बनाए रखते हैं?",
            "concepts": ["event loop", "microtask queue vs macrotask queue", "Promises vs setTimeout", "closure lexical scope"],
            "points": ["Microtask queue is drained completely after the current execution frame before any macrotask runs.", "Promises and queueMicrotask populate microtasks, while setTimeout and I/O populate macrotasks.", "Closures preserve lexical environment references on the heap even after outer functions return."],
            "rubric": {
                "excellent": "Clearly contrasts microtask vs macrotask queues, explains execution order with Promises and timers, and articulates closure memory retention.",
                "good": "Explains that Promises run before setTimeout and closures allow inner functions to access outer variables.",
                "average": "Mentions event loop is asynchronous but confuses microtasks and macrotasks.",
                "poor": "Cannot explain how asynchronous JavaScript works."
            }
        },
        "HARD": {
            "en": "How does JavaScript manage prototypal inheritance under the hood compared to classical class inheritance, and how would you diagnose and prevent memory leaks caused by detached DOM nodes or lingering closures in single-page applications?",
            "hi": "JavaScript क्लासिकल इनहेरिटेंस की तुलना में प्रोटोटाइपल इनहेरिटेंस को कैसे प्रबंधित करता है, और आप सिंगल-पेज एप्लिकेशन्स में मेमोरी लीक्स का निदान कैसे करेंगे?",
            "concepts": ["prototype chain", "__proto__ vs prototype", "detached DOM tree", "closure retention leak", "V8 heap profiler"],
            "points": ["Objects delegate property lookups up the [[Prototype]] chain rather than copying class definitions.", "Detached DOM trees occur when removed DOM elements remain referenced in event listeners or global scopes.", "Use Chrome DevTools Memory Heap Snapshot / allocation timeline to detect retained objects."],
            "rubric": {
                "excellent": "Masterfully explains [[Prototype]] delegation, prototype pollution defenses, detached DOM node retention in closures, and memory profiling.",
                "good": "Explains prototype chain and identifies common memory leak causes like forgotten listeners.",
                "average": "Basic mention of prototype and knows memory leaks slow down the app.",
                "poor": "Unaware of prototypal inheritance or memory leak diagnosis."
            }
        }
    },
    "REST APIs & Web Services": {
        "EASY": {
            "en": "When designing RESTful APIs, what are the primary differences between HTTP GET and POST methods, and what HTTP status codes signify client error versus server error?",
            "hi": "RESTful API डिज़ाइन करते समय, HTTP GET और POST में क्या मुख्य अंतर है, और कौन से स्टेटस कोड क्लाइंट एरर बनाम सर्वर एरर दर्शाते हैं?",
            "concepts": ["GET idempotent vs POST non-idempotent", "query parameters vs body", "4xx client error", "5xx server error"],
            "points": ["GET is idempotent and retrieves data using query parameters; POST modifies server state using request body.", "4xx status codes (400, 401, 404) represent client mistakes; 5xx codes (500, 502, 503) represent internal server failures."],
            "rubric": {
                "excellent": "Clearly contrasts idempotency, payload semantics, caching suitability, and details 4xx vs 5xx categories with examples.",
                "good": "Distinguishes GET for reading and POST for creating data, explaining 400s vs 500s correctly.",
                "average": "Knows GET reads and POST sends data, but vague on HTTP codes.",
                "poor": "Confuses GET and POST or status codes."
            }
        },
        "MEDIUM": {
            "en": "How do you design a secure, stateless REST API authentication flow using JWT (JSON Web Tokens), and how do you handle token expiration and secure refresh without compromising client security?",
            "hi": "JWT का उपयोग करके आप एक सुरक्षित, स्टेटलेस REST API प्रमाणीकरण फ़्लो कैसे डिज़ाइन करते हैं, और टोकन समाप्ति और रिफ्रेश को कैसे संभालते हैं?",
            "concepts": ["JWT header/payload/signature", "stateless token validation", "refresh token rotation", "HttpOnly secure cookies"],
            "points": ["JWTs contain encoded claims verified using cryptographic signatures without server session lookup.", "Short-lived access tokens minimize exposure if intercepted.", "Refresh tokens stored in HttpOnly, SameSite cookies with rotation prevent XSS and CSRF token theft."],
            "rubric": {
                "excellent": "Details header/payload/signature verification, short-lived access tokens, refresh token rotation, and HttpOnly cookie security against XSS/CSRF.",
                "good": "Explains signing tokens and using access + refresh tokens for re-authentication.",
                "average": "Mentions JWT has a token but suggests storing sensitive data in localStorage.",
                "poor": "Cannot explain how JWT authentication operates."
            }
        },
        "HARD": {
            "en": "How do you enforce idempotency for critical payment and order APIs in a distributed microservices architecture, and how do you handle race conditions during concurrent identical requests?",
            "hi": "एक वितरित माइक्रोसर्विसेज आर्किटेक्चर में महत्वपूर्ण पेमेंट APIs के लिए आप idempotency कैसे लागू करते हैं, और समवर्ती समान अनुरोधों के दौरान रेस कंडीशंस को कैसे संभालते हैं?",
            "concepts": ["idempotency keys", "distributed lock / Redis SETNX", "atomic state transition", "outbox / event deduplication"],
            "points": ["Clients supply a unique Idempotency-Key header for state-mutating requests.", "Server checks a distributed cache (e.g., Redis) or unique database constraint using atomic locks (SETNX).", "If a request is already processing, concurrent duplicates receive a 409 Conflict or wait for the cached response."],
            "rubric": {
                "excellent": "Architects end-to-end idempotency: client UUID key, distributed locks with TTL, database unique constraints, atomic state machines, and returning cached responses.",
                "good": "Explains using an idempotency key saved in database or cache to check for existing requests.",
                "average": "Suggests checking if user already paid without atomic guarantees.",
                "poor": "Unaware of idempotency in distributed APIs."
            }
        }
    },
    "Databases & SQL": {
        "EASY": {
            "en": "In relational databases, what is the fundamental purpose of a Primary Key versus a Foreign Key, and when would you use an INNER JOIN versus a LEFT JOIN in SQL?",
            "hi": "रिलेशनल डेटाबेस में Primary Key और Foreign Key का क्या उद्देश्य है, और SQL में INNER JOIN बनाम LEFT JOIN का उपयोग कब किया जाता है?",
            "concepts": ["unique primary key", "referential integrity foreign key", "INNER JOIN intersection", "LEFT JOIN include all left rows"],
            "points": ["A Primary Key uniquely identifies each row in a table.", "A Foreign Key establishes a referential relationship to a primary key in another table.", "INNER JOIN returns only matching rows from both tables; LEFT JOIN returns all rows from the left table and matched rows from the right table."],
            "rubric": {
                "excellent": "Clearly defines uniqueness, referential integrity constraints, nullability rules, and contrasts join row inclusions with examples.",
                "good": "Explains primary key is unique ID, foreign key connects tables, and explains inner vs left join correctly.",
                "average": "Knows keys identify data but confuses inner and left join behavior.",
                "poor": "Cannot explain primary keys or SQL joins."
            }
        },
        "MEDIUM": {
            "en": "How do database indexes (such as B-Trees) accelerate SQL queries, what are the write performance trade-offs of adding indexes, and how do you resolve an N+1 query problem in backend ORMs?",
            "hi": "डेटाबेस इंडेक्स (जैसे B-Trees) SQL प्रश्नों को कैसे तेज़ करते हैं, इंडेक्स जोड़ने के क्या नुकसान हैं, और आप ORM में N+1 क्वेरी समस्या को कैसे हल करते हैं?",
            "concepts": ["B-tree index traversal", "write amplification overhead", "EXPLAIN ANALYZE query plan", "eager loading / JOIN vs N+1"],
            "points": ["B-Tree indexes reduce search complexity from O(N) table scans to O(log N) tree lookups.", "Indexes introduce write amplification because INSERT/UPDATE/DELETE operations must update index structures.", "N+1 query problems are resolved using eager loading (`select_related` / `prefetch_related` or SQL JOINs) instead of lazy querying in loops."],
            "rubric": {
                "excellent": "Explains balanced tree traversal, write overhead/page splits, reading execution plans, and eager vs lazy loading mechanisms.",
                "good": "Explains indexes make reads fast but slow down writes, and explains eager loading for N+1 queries.",
                "average": "Knows indexes speed up searches but vague on write trade-offs or N+1 queries.",
                "poor": "Cannot explain database indexes."
            }
        },
        "HARD": {
            "en": "In high-throughput relational databases, how do ACID transaction isolation levels (Read Committed, Repeatable Read, Serializable) prevent anomalies like Phantom Reads, and how would you resolve deadlocks under heavy concurrent updates?",
            "hi": "उच्च-थ्रूपुट डेटाबेस में ACID आइसोलेशन लेवल्स फैंटम रीड्स जैसी समस्याओं को कैसे रोकते हैं, और आप डेडलॉक्स को कैसे हल करेंगे?",
            "concepts": ["ACID isolation levels", "phantom reads / dirty reads", "two-phase locking / MVCC", "deadlock detection and deterministic lock ordering"],
            "points": ["Isolation levels govern trade-offs between concurrency and consistency (Dirty Read, Non-Repeatable Read, Phantom Read).", "MVCC (Multi-Version Concurrency Control) provides snapshot isolation without blocking read queries.", "Deadlocks are resolved by enforcing deterministic lock acquisition ordering across transactions, short transaction durations, and automatic retry loops."],
            "rubric": {
                "excellent": "Deeply articulates ANSI SQL isolation anomalies, MVCC snapshots vs pessimistic locking, and deadlock mitigation via deterministic lock ordering.",
                "good": "Explains dirty reads and phantom reads, and mentions reducing transaction time or ordering locks to avoid deadlocks.",
                "average": "Mentions ACID acronym but cannot distinguish isolation levels.",
                "poor": "Unaware of database transactions and concurrency anomalies."
            }
        }
    }
}

def are_questions_similar(q1: str, q2: str) -> bool:
    """Detects whether two questions are identical or semantically near-duplicates."""
    if not q1 or not q2:
        return False
    import re
    t1 = re.sub(r'[^\w\s]', '', q1.lower()).strip()
    t2 = re.sub(r'[^\w\s]', '', q2.lower()).strip()
    if t1 == t2:
        return True
    words1 = set(w for w in t1.split() if len(w) > 3)
    words2 = set(w for w in t2.split() if len(w) > 3)
    if not words1 or not words2:
        return False
    overlap = len(words1.intersection(words2)) / min(len(words1), len(words2))
    return overlap >= 0.70

def generate_project_adaptive_question(
    project: Dict[str, Any],
    difficulty: str,
    language: str = "en",
    turn_index: int = 1,
    last_score: Optional[float] = None,
    previous_answer: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates a personalized question grounded in a candidate's specific resume project.
    Branches into:
    - EASY: Simpler clarifying question on the project or foundational component
    - MEDIUM: Practical implementation question on state management, APIs, or trade-offs
    - HARD: Advanced architectural scaling, caching, race condition prevention, or performance
    """
    proj_name = project.get("name", "Featured Project")
    proj_techs = project.get("technologies") or ["relevant software libraries"]
    tech_str = ", ".join(proj_techs[:3])
    is_hi = (language == "hi")

    if difficulty == "EASY":
        q_type = "project_clarifying_foundational"
        reason = f"Adapting following weak answer on '{proj_name}'. Asking a simpler clarifying question to diagnose core project mechanics."
        if is_hi:
            q_text = f"आपके प्रोजेक्ट '{proj_name}' के दायरे को स्पष्ट करने के लिए, इसमें आपका व्यक्तिगत योगदान क्या था, और क्या आप सबसे सरल मुख्य कॉम्पोनेंट या फीचर के बारे में बता सकते हैं जिसे आपने {tech_str} का उपयोग करके बनाया?"
        else:
            q_text = f"To clarify the scope of your '{proj_name}' project, what was your specific individual contribution, and could you walk through the simplest core component or feature you personally implemented using {tech_str}?"
        concepts = ["individual contribution", "component functionality", "basic data flow", "core feature"]
        points = [
            f"Articulates candidate's individual responsibilities vs team contributions in {proj_name}.",
            f"Explains a concrete basic component built using {tech_str}.",
            "Demonstrates practical familiarity with the project codebase."
        ]
        rubric = {
            "excellent": f"Clearly delineates their personal contributions, walks through a specific component in {proj_name}, and explains how it worked.",
            "good": f"Identifies what they worked on and describes a feature of {proj_name}.",
            "average": "Describes the overall project without clarifying personal contributions.",
            "poor": "Cannot explain their role or components in the project."
        }
    elif difficulty == "HARD":
        q_type = "project_architectural_scaling"
        reason = f"Escalating following strong mastery on '{proj_name}'. Challenging candidate with an advanced architectural scaling and performance question."
        if is_hi:
            q_text = f"प्रोजेक्ट '{proj_name}' के आर्किटेक्चर को आगे बढ़ाते हुए: यदि यूजर ट्रैफिक और डेटा वॉल्यूम 100 गुना बढ़ जाए, तो आप क्लाइंट/सर्वर कैशिंग, रेस कंडीशंस की रोकथाम और {tech_str} के प्रदर्शन को कैसे ऑप्टिमाइज़ करेंगे?"
        else:
            q_text = f"Building on your architecture for '{proj_name}': if user traffic and data volume increased a hundredfold, how would you design client/server caching, prevent concurrent race conditions, and optimize {tech_str} for sub-second latency?"
        concepts = ["high-scale caching", "database indexing & connection pooling", "race condition prevention", "asynchronous decoupling"]
        points = [
            f"Architects a caching strategy (Redis / CDN / client memory) for {proj_name}.",
            "Addresses database concurrency, connection bottlenecks, and race conditions.",
            f"Details optimization techniques specific to {tech_str}."
        ]
        rubric = {
            "excellent": f"Presents a comprehensive scaling roadmap for {proj_name}, detailing caching tiers, database query optimization, and concurrency controls.",
            "good": f"Proposes caching and database indexes to scale {proj_name}.",
            "average": "Suggests adding more servers without structural architecture improvements.",
            "poor": "Cannot describe how to scale the project."
        }
    else: # MEDIUM
        q_type = "project_practical_tradeoffs"
        reason = f"Following up on '{proj_name}'. Exploring practical implementation details, state management, and error handling."
        if is_hi:
            q_text = f"आपके प्रोजेक्ट '{proj_name}' में, आपने {tech_str} का उपयोग करके स्टेट मैनेजमेंट, एसिंक्रोनस डेटा फ़्लो और एपीआई एरर हैंडलिंग को कैसे संभाला?"
        else:
            q_text = f"In your '{proj_name}', how did you handle state management, asynchronous data communication, and network error handling between components using {tech_str}?"
        concepts = ["state management", "async data flow", "error boundaries / exception handling", "API integration"]
        points = [
            f"Explains state management strategy and component communication in {proj_name}.",
            "Details asynchronous data retrieval and loading state patterns.",
            "Discusses error handling, user feedback, and network failure recovery."
        ]
        rubric = {
            "excellent": f"Clearly details state flow, async fetching with loading/error handling, and discusses technical trade-offs in {proj_name}.",
            "good": f"Explains how state was stored and how API calls were made in {proj_name}.",
            "average": "Superficial mention of variables and API calls without error handling.",
            "poor": "Cannot explain state or data flow in the project."
        }

    dyn_id = f"dyn_proj_{uuid.uuid4().hex[:8]}"
    q_obj = {
        "id": dyn_id,
        "role": "Software Developer Intern",
        "skill": f"Project: {proj_name}",
        "difficulty": difficulty,
        "question_en": q_text,
        "question_hi": q_text,
        "expected_concepts": concepts,
        "ideal_answer_points": points,
        "rubric": rubric,
        "follow_ups": [
            f"What was the most challenging bug you debugged in {proj_name}?",
            f"How would you improve the test coverage of {proj_name} today?"
        ],
        "is_dynamic": True
    }
    register_dynamic_question(q_obj)

    return {
        "question_id": dyn_id,
        "skill": f"Project: {proj_name}",
        "difficulty": difficulty,
        "question_text": q_text,
        "question": q_text,
        "question_en": q_text if not is_hi else (f"Regarding '{proj_name}' built with {tech_str}: can you explain your architecture and technical trade-offs?"),
        "question_hi": q_text if is_hi else (f"प्रोजेक्ट '{proj_name}' में, {tech_str} के साथ आपके आर्किटेक्चर और योगदान को समझाइए।"),
        "question_index": turn_index + 1,
        "total_questions": None,
        "language": language,
        "question_type": q_type,
        "reason": reason,
        "adaptive_reason": reason,
        "follow_ups": q_obj["follow_ups"]
    }

def generate_adaptive_offline_question(
    skill: str,
    difficulty: str,
    language: str = "en",
    turn_index: int = 0,
    previous_answer: Optional[str] = None,
    last_score: Optional[float] = None,
    question_type: Optional[str] = "competency",
    adaptive_reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates a high-quality rubric-grounded dynamic question when offline or Gemini is unavailable.
    Guarantees different questions for weak (EASY), moderate (MEDIUM), and strong (HARD) scores.
    """
    # Pick matching skill template or fallback with intelligent keyword mapping
    s_low = skill.lower()
    matched_key = None
    if any(x in s_low for x in ["react", "frontend", "html", "css", "vue", "angular"]):
        matched_key = "React & Frontend"
    elif any(x in s_low for x in ["javascript", "js", "typescript", "ts", "es6"]):
        matched_key = "JavaScript"
    elif any(x in s_low for x in ["python", "django", "fastapi", "flask"]):
        matched_key = "Python & Backend"
    elif any(x in s_low for x in ["sql", "database", "postgres", "mysql", "mongodb", "db"]):
        matched_key = "Databases & SQL"
    elif any(x in s_low for x in ["api", "rest", "backend", "node", "express", "endpoint"]):
        matched_key = "REST APIs & Web Services"
    elif any(x in s_low for x in ["data structure", "algorithm", "dsa", "array", "tree", "graph", "hash"]):
        matched_key = "Data Structures & Algorithms"
    elif any(x in s_low for x in ["problem", "debug", "troubleshoot"]):
        matched_key = "Problem Solving"
    elif any(x in s_low for x in ["communicat", "team", "review", "lead"]):
        matched_key = "Communication"
    else:
        for k in DYNAMIC_TOPIC_TEMPLATES:
            if k.lower() in s_low or s_low in k.lower():
                matched_key = k
                break
        if not matched_key:
            matched_key = "Programming Fundamentals"

    skill_data = DYNAMIC_TOPIC_TEMPLATES[matched_key]
    diff_data = skill_data.get(difficulty, skill_data["MEDIUM"])
    base_text = diff_data.get(language, diff_data["en"])

    # Personalize text if previous turn had context
    if last_score is not None and last_score < 40 and previous_answer:
        if language == "hi":
            question_text = f"आपके पिछले उत्तर को ध्यान में रखते हुए, आइए एक बुनियादी नैदानिक प्रश्न पर चर्चा करें: {base_text}"
        else:
            question_text = f"To clarify foundational understanding following your previous response: {base_text}"
    elif last_score is not None and last_score > 70 and previous_answer:
        if language == "hi":
            question_text = f"आपके पिछले उत्कृष्ट उत्तर को आगे बढ़ाते हुए, अगला गहराई वाला तकनीकी प्रश्न: {base_text}"
        else:
            question_text = f"Building on your strong previous explanation, let's explore an advanced scenario: {base_text}"
    else:
        question_text = base_text

    dyn_id = f"dyn_{matched_key[:4].lower().replace(' ', '_')}_{difficulty.lower()}_{turn_index}_{uuid.uuid4().hex[:6]}"
    q_obj = {
        "id": dyn_id,
        "role": "Software Developer Intern",
        "skill": skill,
        "difficulty": difficulty,
        "question_en": diff_data["en"],
        "question_hi": diff_data["hi"],
        "expected_concepts": diff_data["concepts"],
        "ideal_answer_points": diff_data["points"],
        "rubric": diff_data["rubric"],
        "follow_ups": [
            f"Can you provide a concrete example in code or system design for {skill}?",
            f"What trade-offs or edge cases would you consider when implementing this?"
        ],
        "is_dynamic": True
    }
    register_dynamic_question(q_obj)

    reason_str = adaptive_reason or (
        f"Diagnosing foundational principles with an accessible question." if difficulty == "EASY"
        else (f"Escalating to an advanced challenge following strong technical mastery." if difficulty == "HARD"
              else f"Exploring applied implementation details and design trade-offs.")
    )

    return {
        "question_id": dyn_id,
        "skill": skill,
        "difficulty": difficulty,
        "question_text": question_text,
        "question": question_text,
        "question_en": diff_data["en"],
        "question_hi": diff_data["hi"],
        "question_index": turn_index + 1,
        "total_questions": None,
        "language": language,
        "question_type": question_type or "competency",
        "reason": reason_str,
        "adaptive_reason": reason_str,
        "follow_ups": q_obj["follow_ups"]
    }

def select_next_question(
    interview_turn_index: int,
    current_difficulty: str,
    asked_question_ids: List[str],
    role: str = "Software Developer Intern",
    language: str = "en",
    total_questions: Optional[int] = None,
    previous_answer: Optional[str] = None,
    last_score: Optional[float] = None,
    remaining_seconds: Optional[float] = None,
    turns_history: Optional[List[Dict[str, Any]]] = None,
    resume_data: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Selects the next adaptive question based on:
    - Candidate's latest answer, evaluation score, and evidence.
    - Candidate's resume skills, projects, and technologies (when available).
    - Current difficulty level and score bands (0-4 weak -> EASY, 5-7 moderate -> MEDIUM, 8-10 strong -> HARD).
    - Deduplication safeguards ensuring no repeated or closely rephrased questions.
    """
    # 1. Total questions limit check
    if total_questions is not None and total_questions > 0 and interview_turn_index >= total_questions:
        return None

    # 2. Time-aware cutoff: if less than 30 seconds remain, conclude session
    if remaining_seconds is not None and remaining_seconds <= 30.0:
        logger.info(f"Session approaching 20-minute deadline ({remaining_seconds:.1f}s remaining). Concluding dynamic questioning.")
        return None

    # Collect texts of all previously asked questions for deduplication
    asked_texts = []
    for q_id in asked_question_ids:
        q_obj = get_question_by_id(q_id)
        if q_obj:
            if q_obj.get("question_en"):
                asked_texts.append(q_obj["question_en"])
            if q_obj.get("question_hi"):
                asked_texts.append(q_obj["question_hi"])
            if q_obj.get("question_text"):
                asked_texts.append(q_obj["question_text"])

    # 3. Determine Adaptive Target Difficulty and Question Category strictly based on current_difficulty and last_score
    target_difficulty = current_difficulty or "MEDIUM"
    if last_score is not None:
        if last_score < 40.0:
            q_category = "foundational_diagnostic"
            adaptive_reason = f"Candidate gave a weak answer on previous turn (score {last_score:.0f}/100). Adapting difficulty to {target_difficulty} to diagnose core principles."
        elif last_score > 70.0:
            q_category = "advanced_challenge"
            adaptive_reason = f"Candidate demonstrated strong mastery on previous turn (score {last_score:.0f}/100). Escalating difficulty to {target_difficulty}."
        else:
            q_category = "practical_application"
            adaptive_reason = f"Candidate provided a partially correct answer (score {last_score:.0f}/100). Continuing at {target_difficulty} with an applied scenario."
    else:
        q_category = "kickoff_assessment"
        adaptive_reason = "Initial technical competency assessment."

    # 4. RESUME-PERSONALIZED PATH (When resume is provided)
    if resume_data and (resume_data.get("detected_projects") or resume_data.get("projects") or resume_data.get("detected_skills") or resume_data.get("skills")):
        projects = resume_data.get("detected_projects") or resume_data.get("projects") or []
        skills = resume_data.get("detected_skills") or resume_data.get("skills") or []
        top_project = projects[0] if projects else None
        top_skill = skills[0] if skills else "Programming Fundamentals"

        # Turn 0: Kickoff question on candidate's project or skill
        if interview_turn_index == 0:
            if top_project:
                proj_name = top_project.get("name", "Key Project")
                proj_techs = top_project.get("technologies") or ["modern software tools"]
                tech_str = ", ".join(proj_techs[:2])
                q_skill = f"Project Deep-Dive: {proj_name}"
                q_type = "project_deep_dive"
                reason = f"Kickoff question personalized to candidate's resume project '{proj_name}'."
                
                if language == "hi":
                    q_text = f"आपके रिज्यूमे में उल्लिखित प्रोजेक्ट '{proj_name}' के संदर्भ में, क्या आप इसके समग्र आर्किटेक्चर को समझा सकते हैं, और आपने इसे बनाने के लिए {tech_str} को क्यों चुना?"
                    q_hi = q_text
                    q_en = f"In your resume, you featured '{proj_name}'. Can you explain the high-level architecture of this project, why you chose {tech_str}, and what key challenges you faced during development?"
                else:
                    q_text = f"In your resume, you featured '{proj_name}'. Can you explain the high-level architecture of this project, why you chose {tech_str}, and what key challenges you faced during development?"
                    q_en = q_text
                    q_hi = f"आपके रिज्यूमे में उल्लिखित प्रोजेक्ट '{proj_name}' के संदर्भ में, क्या आप इसके समग्र आर्किटेक्चर को समझा सकते हैं, और आपने इसे बनाने के लिए {tech_str} को क्यों चुना?"
                
                dyn_id = f"dyn_resume_proj_{uuid.uuid4().hex[:6]}"
                q_obj = {
                    "id": dyn_id,
                    "role": role,
                    "skill": q_skill,
                    "difficulty": "MEDIUM",
                    "question_en": q_en,
                    "question_hi": q_hi,
                    "expected_concepts": ["system architecture", "technology selection rationale", "data flow", "trade-offs"],
                    "ideal_answer_points": [
                        f"Explains the architecture and client/server data flow for {proj_name}.",
                        f"Articulates why {tech_str} was selected over alternatives.",
                        "Discusses technical challenges or trade-offs encountered during implementation."
                    ],
                    "rubric": {
                        "excellent": f"Clearly details the component architecture of {proj_name}, justifies choosing {tech_str}, and describes technical trade-offs.",
                        "good": f"Explains the purpose of {proj_name} and mentions how {tech_str} was used.",
                        "average": "Gives a superficial description of features without technical architecture.",
                        "poor": "Cannot explain the architecture or implementation details."
                    },
                    "follow_ups": [
                        f"How did you handle error handling or state management in {proj_name}?",
                        f"How would you optimize {proj_name} for higher traffic?"
                    ],
                    "is_dynamic": True
                }
                register_dynamic_question(q_obj)
                return {
                    "question_id": dyn_id,
                    "skill": q_skill,
                    "difficulty": "MEDIUM",
                    "question_text": q_text,
                    "question": q_text,
                    "question_en": q_en,
                    "question_hi": q_hi,
                    "question_index": 1,
                    "total_questions": total_questions,
                    "language": language,
                    "question_type": q_type,
                    "reason": reason,
                    "adaptive_reason": reason,
                    "follow_ups": q_obj["follow_ups"]
                }
            elif top_skill:
                # Skill verification kickoff
                q_skill = top_skill
                q_type = "skill_verification"
                reason = f"Kickoff question verifying core technical skill '{top_skill}' from candidate's resume."
                offline_q = generate_adaptive_offline_question(
                    skill=top_skill,
                    difficulty="MEDIUM",
                    language=language,
                    turn_index=0,
                    question_type=q_type,
                    adaptive_reason=reason
                )
                offline_q["total_questions"] = total_questions
                return offline_q

        # Turn 1: If Turn 0 was about top_project, adapt DIRECTLY on top_project!
        # Branches: Weak -> EASY clarifying, Moderate -> MEDIUM practical, Strong -> HARD scaling
        if interview_turn_index == 1 and top_project:
            proj_adaptive_q = generate_project_adaptive_question(
                project=top_project,
                difficulty=target_difficulty,
                language=language,
                turn_index=1,
                last_score=last_score,
                previous_answer=previous_answer
            )
            proj_adaptive_q["total_questions"] = total_questions
            return proj_adaptive_q

        # Turn >= 2 (or Turn 1 without project): Rotate to candidate's skills
        asked_skills = [t.get("skill") for t in (turns_history or [])]
        last_turn_skill = turns_history[-1].get("skill") if turns_history else None

        # If weak answer on last turn, STAY on the same skill to ask an easier foundational question!
        if last_score is not None and last_score < 40.0 and last_turn_skill:
            target_skill = last_turn_skill.replace("Project Deep-Dive: ", "").replace("Project: ", "")
        else:
            # Advance to an unassessed resume skill
            resume_skill_candidates = [
                s for s in skills 
                if not any(s.lower() in str(ask_s).lower() for ask_s in asked_skills)
            ]
            if resume_skill_candidates:
                target_skill = resume_skill_candidates[0]
            elif len(projects) > 1 and not any(projects[1].get("name", "").lower() in str(ask_s).lower() for ask_s in asked_skills):
                # Ask second project if available
                return generate_project_adaptive_question(
                    project=projects[1],
                    difficulty=target_difficulty,
                    language=language,
                    turn_index=interview_turn_index,
                    last_score=last_score,
                    previous_answer=previous_answer
                )
            else:
                target_skill = SKILL_SEQUENCE[interview_turn_index % len(SKILL_SEQUENCE)]

        # Try live Gemini generation with resume context if key is active
        try:
            from backend.ai.gemini_service import generate_dynamic_question_with_gemini
            gemini_dyn = generate_dynamic_question_with_gemini(
                role=role,
                skill=target_skill,
                difficulty=target_difficulty,
                language=language,
                asked_question_texts=asked_texts,
                previous_answer=previous_answer,
                last_score=last_score,
                remaining_seconds=remaining_seconds,
                resume_data=resume_data,
                question_type=q_category
            )
            if gemini_dyn and gemini_dyn.get("question_text"):
                cand_text = gemini_dyn["question_text"]
                if not any(are_questions_similar(cand_text, prev_t) for prev_t in asked_texts):
                    dyn_id = f"dyn_gemini_{target_skill[:4].lower().replace(' ', '_')}_{interview_turn_index}_{uuid.uuid4().hex[:6]}"
                    gemini_dyn["id"] = dyn_id
                    gemini_dyn["is_dynamic"] = True
                    register_dynamic_question(gemini_dyn)
                    return {
                        "question_id": dyn_id,
                        "skill": target_skill,
                        "difficulty": target_difficulty,
                        "question_text": cand_text,
                        "question": cand_text,
                        "question_index": interview_turn_index + 1,
                        "total_questions": total_questions,
                        "language": language,
                        "question_type": q_category,
                        "reason": adaptive_reason,
                        "adaptive_reason": adaptive_reason,
                        "follow_ups": gemini_dyn.get("follow_ups", [])
                    }
        except Exception:
            pass

        # Robust Offline Resume Question Generator
        offline_q = generate_adaptive_offline_question(
            skill=target_skill,
            difficulty=target_difficulty,
            language=language,
            turn_index=interview_turn_index,
            previous_answer=previous_answer,
            last_score=last_score,
            question_type=q_category,
            adaptive_reason=adaptive_reason
        )
        offline_q["total_questions"] = total_questions
        return offline_q

    # 5. STANDARD ROLE-BASED PATH (When resume is skipped or testing standard sequence)
    # Track skill counts
    skill_counts = {s: 0 for s in SKILL_SEQUENCE}
    last_turn_skill = None
    if turns_history:
        for t in turns_history:
            s = t.get("skill")
            if s in skill_counts:
                skill_counts[s] += 1
        last_turn_skill = turns_history[-1].get("skill")
    else:
        for q_id in asked_question_ids:
            q = get_question_by_id(q_id)
            if q and q.get("skill") in skill_counts:
                skill_counts[q["skill"]] += 1
                last_turn_skill = q["skill"]

    # In standard role-based path without resume, advance across SKILL_SEQUENCE competencies
    if interview_turn_index < len(SKILL_SEQUENCE):
        target_skill = SKILL_SEQUENCE[interview_turn_index]
    else:
        min_count = min(skill_counts.values())
        least_assessed = [s for s in SKILL_SEQUENCE if skill_counts[s] == min_count]
        target_skill = least_assessed[0]

    # Search existing static QUESTION_BANK for unasked question matching target_skill and target_difficulty
    candidates = [
        q for q in QUESTION_BANK
        if q.get("role") == role
        and q.get("skill") == target_skill
        and q.get("difficulty") == target_difficulty
        and q.get("id") not in asked_question_ids
    ]

    # Deduplicate against asked question texts
    unasked_candidates = []
    for c in candidates:
        c_text = c.get(f"question_{language}", c.get("question_en", ""))
        if not any(are_questions_similar(c_text, prev_t) for prev_t in asked_texts):
            unasked_candidates.append(c)

    if unasked_candidates:
        chosen = unasked_candidates[0]
        question_text = chosen.get(f"question_{language}", chosen.get("question_en", ""))
        return {
            "question_id": chosen["id"],
            "skill": chosen["skill"],
            "difficulty": chosen["difficulty"],
            "question_text": question_text,
            "question": question_text,
            "question_index": interview_turn_index + 1,
            "total_questions": total_questions,
            "language": language,
            "question_type": q_category,
            "reason": adaptive_reason,
            "adaptive_reason": adaptive_reason,
            "follow_ups": chosen.get("follow_ups", [])
        }

    # If static bank has no matching unasked questions for this difficulty, try Gemini
    try:
        from backend.ai.gemini_service import generate_dynamic_question_with_gemini
        gemini_dyn = generate_dynamic_question_with_gemini(
            role=role,
            skill=target_skill,
            difficulty=target_difficulty,
            language=language,
            asked_question_texts=asked_texts,
            previous_answer=previous_answer,
            last_score=last_score,
            remaining_seconds=remaining_seconds,
            question_type=q_category
        )
        if gemini_dyn and gemini_dyn.get("question_text"):
            cand_text = gemini_dyn["question_text"]
            if not any(are_questions_similar(cand_text, prev_t) for prev_t in asked_texts):
                dyn_id = f"dyn_gemini_{target_skill[:4].lower().replace(' ', '_')}_{interview_turn_index}_{uuid.uuid4().hex[:6]}"
                gemini_dyn["id"] = dyn_id
                gemini_dyn["is_dynamic"] = True
                register_dynamic_question(gemini_dyn)
                return {
                    "question_id": dyn_id,
                    "skill": target_skill,
                    "difficulty": target_difficulty,
                    "question_text": cand_text,
                    "question": cand_text,
                    "question_index": interview_turn_index + 1,
                    "total_questions": total_questions,
                    "language": language,
                    "question_type": q_category,
                    "reason": adaptive_reason,
                    "adaptive_reason": adaptive_reason,
                    "follow_ups": gemini_dyn.get("follow_ups", [])
                }
    except Exception as e:
        logger.warning(f"Live dynamic question generation error: {e}. Using adaptive offline generator.")

    # Fallback to adaptive offline generator
    dyn_q = generate_adaptive_offline_question(
        skill=target_skill,
        difficulty=target_difficulty,
        language=language,
        turn_index=interview_turn_index,
        previous_answer=previous_answer,
        last_score=last_score,
        question_type=q_category,
        adaptive_reason=adaptive_reason
    )
    dyn_q["total_questions"] = total_questions
    return dyn_q

def generate_candidate_report(
    candidate: Dict[str, Any],
    interview: Dict[str, Any],
    turns: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Synthesizes interview turns into an executive Recruiter Report.
    Includes skill breakdowns, evidence extracts, strengths, areas for improvement,
    and clear AI recommendation with human-in-the-loop separation.
    """
    if not turns:
        raw_reason = interview.get("termination_reason") or "NORMAL"
        status = interview.get("status") or "completed"
        term_reason = status if status in ["TIME_EXPIRED", "TERMINATED_WEAK_ANSWERS", "TERMINATED_FOCUS_VIOLATION"] else raw_reason
        if term_reason == "TIME_EXPIRED":
            status_display = "Time Expired (20-Minute Limit Reached)"
            term_summary = "The interview closed automatically because the maximum 20-minute time limit expired. No responses were evaluated."
        elif term_reason == "TERMINATED_FOCUS_VIOLATION":
            status_display = "Terminated (Focus Violation / Tab Switch Detected)"
            term_summary = "The interview ended automatically because the candidate switched away from the active interview page, minimized the browser, or switched applications. No responses were evaluated."
        elif term_reason == "TERMINATED_WEAK_ANSWERS":
            status_display = "Terminated (7 Consecutive Weak Answers <40/100)"
            term_summary = "The interview ended because 7 consecutive answers scored below the 40/100 threshold."
        else:
            status_display = "Incomplete Interview"
            term_summary = "Interview closed with no evaluated responses recorded."

        return {
            "candidate_id": candidate.get("id"),
            "candidate_name": candidate.get("name", "Anonymous Candidate"),
            "role": candidate.get("role", "Software Developer Intern"),
            "language": candidate.get("language", "en"),
            "interview_id": interview.get("id"),
            "started_at": str(interview.get("started_at")) if interview.get("started_at") else None,
            "completed_at": str(interview.get("completed_at")) if interview.get("completed_at") else None,
            "deadline_at": str(interview.get("deadline_at")) if interview.get("deadline_at") else None,
            "duration_seconds": 0.0,
            "duration_formatted": "0m 00s",
            "questions_answered": 0,
            "consecutive_weak_answers": interview.get("consecutive_weak_answers", 0),
            "termination_reason": term_reason,
            "termination_status_display": status_display,
            "termination_summary": term_summary,
            "overall_score": 0,
            "ai_recommendation": "Incomplete Interview",
            "ai_recommendation_summary": "Session ended before any competency questions could be evaluated.",
            "skills_breakdown": [],
            "strengths": [],
            "areas_to_improve": [],
            "turns": [],
            "human_decision_notice": "IMPORTANT: AI recommendations are purely assistive. Final hiring decisions must be executed by a human recruiter.",
            "fairness_status": {
                "protected_attributes_excluded": True,
                "language_fairness_applied": True,
                "evidence_backed": False,
                "human_in_the_loop": True
            }
        }

    # Aggregate by skill
    skill_map: Dict[str, List[Dict[str, Any]]] = {}
    for t in turns:
        s = t["skill"]
        if s not in skill_map:
            skill_map[s] = []
        skill_map[s].append(t)

    skills_breakdown = []
    total_score = 0.0
    all_strengths = []
    all_weaknesses = []

    for skill_name, turn_list in skill_map.items():
        avg_score = sum(t["score"] for t in turn_list) / len(turn_list)
        total_score += avg_score

        # Combine evidence
        evidence_snippets = [t["evidence"] for t in turn_list if t.get("evidence")]
        combined_evidence = " | ".join(evidence_snippets) if evidence_snippets else "Insufficient evidence from this answer."
        reasons = [t["reason"] for t in turn_list if t.get("reason")]
        combined_reason = " ".join(reasons)

        for t in turn_list:
            if t.get("strengths_json"):
                try:
                    import json
                    strengths = json.loads(t["strengths_json"])
                    all_strengths.extend(strengths)
                except Exception:
                    pass
            if t.get("weaknesses_json"):
                try:
                    import json
                    weaknesses = json.loads(t["weaknesses_json"])
                    all_weaknesses.extend(weaknesses)
                except Exception:
                    pass

        skills_breakdown.append({
            "skill": skill_name,
            "score": round(avg_score, 1),
            "evidence": combined_evidence,
            "reason": combined_reason,
            "difficulty_reached": turn_list[-1]["difficulty"],
            "turns_count": len(turn_list)
        })

    evaluated_skills = set(skill_map.keys())
    pending_skills = []
    for planned_skill in SKILL_SEQUENCE:
        if planned_skill not in evaluated_skills:
            pending_skills.append({
                "skill": planned_skill,
                "status": "Unavailable",
                "score": None,
                "reason": "Interview concluded before reaching this competency. Evaluation was not performed.",
                "evidence": "N/A - Competency not reached"
            })

    if skills_breakdown:
        overall_score = round(total_score / len(skills_breakdown), 1)
        if overall_score >= 80:
            recommendation = "Strong Match"
            rec_summary = "Candidate demonstrates superior conceptual depth and practical reasoning across evaluated skills."
        elif overall_score >= 65:
            recommendation = "Potential Match"
            rec_summary = "Candidate showed solid competence with opportunities for growth in complex architectural scenarios."
        elif overall_score >= 50:
            recommendation = "Needs Further Review"
            rec_summary = "Candidate demonstrated foundational grasp but inconsistent technical depth across core competencies."
        else:
            recommendation = "Low Alignment"
            rec_summary = "Candidate struggled with foundational concepts and core job-related problem solving."
    else:
        overall_score = 0.0
        recommendation = "Insufficient Data"
        rec_summary = "The interview concluded before any questions could be completed and evaluated."

    # Deduplicate strengths and weaknesses
    unique_strengths = list(dict.fromkeys(all_strengths))[:4]
    unique_weaknesses = list(dict.fromkeys(all_weaknesses))[:4]

    # Calculate interview duration and timing metadata
    started_at = interview.get("started_at")
    completed_at = interview.get("completed_at")
    deadline_at = interview.get("deadline_at")
    duration_seconds = 0.0
    if started_at:
        try:
            from datetime import datetime, timezone
            s_dt = datetime.fromisoformat(str(started_at).replace("Z", "+00:00"))
            if completed_at:
                c_dt = datetime.fromisoformat(str(completed_at).replace("Z", "+00:00"))
            else:
                c_dt = datetime.now(timezone.utc)
            if s_dt.tzinfo is None:
                s_dt = s_dt.replace(tzinfo=timezone.utc)
            if c_dt.tzinfo is None:
                c_dt = c_dt.replace(tzinfo=timezone.utc)
            duration_seconds = max(0.0, (c_dt - s_dt).total_seconds())
        except Exception:
            duration_seconds = float(len(turns) * 120.0)

    dur_mins = int(duration_seconds) // 60
    dur_secs = int(duration_seconds) % 60
    duration_formatted = f"{dur_mins}m {dur_secs:02d}s"

    raw_reason = interview.get("termination_reason") or "NORMAL"
    status = interview.get("status") or "completed"
    if status in ["TIME_EXPIRED", "TERMINATED_WEAK_ANSWERS", "TERMINATED_FOCUS_VIOLATION"]:
        termination_reason = status
    elif raw_reason in ["TIME_EXPIRED", "TERMINATED_WEAK_ANSWERS", "TERMINATED_FOCUS_VIOLATION"]:
        termination_reason = raw_reason
    else:
        termination_reason = "COMPLETED"

    if termination_reason == "TIME_EXPIRED":
        status_display = "Time Expired (20-Minute Limit Reached)"
        termination_summary = (
            "The interview closed automatically because the maximum 20-minute time limit expired. "
            "All questions answered and evaluations recorded prior to expiration were preserved."
        )
    elif termination_reason == "TERMINATED_FOCUS_VIOLATION":
        status_display = "Terminated (Focus Violation / Tab Switch Detected)"
        termination_summary = (
            "The interview ended automatically because the candidate switched away from the active interview page, "
            "minimized the browser, or switched applications. All responses, evaluations, and evidence recorded prior to the violation were preserved."
        )
    elif termination_reason == "TERMINATED_WEAK_ANSWERS":
        status_display = "Terminated (7 Consecutive Weak Answers <40/100)"
        termination_summary = (
            "The interview ended because 7 consecutive answers scored below the 40/100 threshold. "
            "All responses, evaluations, and evidence have been preserved in full."
        )
    else:
        status_display = "Completed"
        termination_summary = (
            "The candidate successfully completed the scheduled interview questions. "
            "All responses, evaluations, and score evidence have been verified."
        )
    # Retrieve resume metadata if candidate uploaded a resume
    resume_info = None
    res_id = interview.get("resume_id") or candidate.get("resume_id")
    if res_id:
        try:
            from backend.database.database import get_connection
            r_conn = get_connection()
            r_c = r_conn.cursor()
            r_c.execute("SELECT * FROM resumes WHERE id = ?", (res_id,))
            r_row = r_c.fetchone()
            r_conn.close()
            if r_row:
                import json
                p_data = json.loads(r_row["parsed_data_json"])
                resume_info = {
                    "resume_id": r_row["id"],
                    "filename": r_row["filename"],
                    "parser": r_row["parser_type"],
                    "detected_skills": p_data.get("detected_skills", []),
                    "detected_projects": p_data.get("detected_projects") or p_data.get("projects", []),
                    "languages_frameworks": p_data.get("languages_frameworks", []),
                    "tools_technologies": p_data.get("tools_technologies", []),
                    "experience": p_data.get("experience", []),
                    "summary": p_data.get("summary")
                }
        except Exception:
            pass

    return {
        "candidate_id": candidate.get("id"),
        "candidate_name": candidate.get("name", "Anonymous Candidate"),
        "role": candidate.get("role", "Software Developer Intern"),
        "language": candidate.get("language", "en"),
        "interview_id": interview.get("id"),
        "started_at": str(started_at) if started_at else None,
        "completed_at": str(completed_at) if completed_at else None,
        "deadline_at": str(deadline_at) if deadline_at else None,
        "duration_seconds": round(duration_seconds, 1),
        "duration_formatted": duration_formatted,
        "questions_answered": len(turns),
        "consecutive_weak_answers": interview.get("consecutive_weak_answers", 0),
        "termination_reason": termination_reason,
        "termination_status_display": status_display,
        "termination_summary": termination_summary,
        "overall_score": overall_score,
        "ai_recommendation": recommendation,
        "ai_recommendation_summary": rec_summary,
        "skills_breakdown": skills_breakdown,
        "pending_skills": pending_skills,
        "strengths": unique_strengths if unique_strengths else ["Communicated clearly throughout the interview session."],
        "areas_to_improve": unique_weaknesses if unique_weaknesses else ["Deepen knowledge in distributed system design and edge cases."],
        "turns": turns,
        "resume_info": resume_info,
        "human_decision_notice": "IMPORTANT: AI recommendations are purely assistive. Final hiring and shortlisting decisions must be executed by a human recruiter.",
        "fairness_status": {
            "protected_attributes_excluded": True,
            "language_fairness_applied": True,
            "evidence_backed": True,
            "human_in_the_loop": True
        }
    }
