"""
IntervueAI Question Bank
Comprehensive multilingual questions, rubrics, expected concepts, and sample answers.
Supports English (en) and Hindi (hi).
"""

QUESTION_BANK = [
    # ========================================================
    # 1. PROGRAMMING FUNDAMENTALS
    # ========================================================
    {
        "id": "prog_easy_1",
        "role": "Software Developer Intern",
        "skill": "Programming Fundamentals",
        "difficulty": "EASY",
        "question_en": "Can you explain what a variable is in programming, and what is the difference between declaring and initializing a variable?",
        "question_hi": "क्या आप समझा सकते हैं कि प्रोग्रामिंग में 'Variable' क्या होता है, और Variable को Declare करने और Initialize करने में क्या अंतर है?",
        "expected_concepts": ["memory allocation", "identifier/name", "data storage", "declaration vs initialization"],
        "ideal_answer_points": [
            "A variable is a named storage location in memory that holds a value.",
            "Declaration specifies the variable's name and type without necessarily assigning a value.",
            "Initialization gives the variable its initial value at the time of or after creation."
        ],
        "rubric": {
            "excellent": "Mentions memory location, named reference, clearly distinguishes declaration (allocating identifier/type) from initialization (assigning initial value), provides a simple code example.",
            "good": "Defines variable as a container for data and explains declaration vs initialization correctly.",
            "average": "Explains what a variable is but confuses declaration with initialization.",
            "poor": "Vague or incorrect explanation of variables."
        },
        "follow_ups": [
            "What happens if you use a variable before initializing it in languages like C++ or JavaScript?",
            "Can you explain the difference between immutable and mutable variables?"
        ],
        "demo_answers": {
            "strong_en": "A variable is a named container in memory used to store data that a program can manipulate. Declaration means defining the variable's name and type so the compiler knows it exists. Initialization means assigning an initial value to that variable, for example 'int x;' is declaration, while 'x = 10;' or 'int x = 10;' is initialization.",
            "average_en": "A variable stores values in a program like numbers or text. Declaring is making the variable and initializing is giving it a value when you start.",
            "weak_en": "A variable is like a number in math. It changes values.",
            "strong_hi": "प्रोग्रामिंग में Variable मेमोरी का एक नामी (named) लोकेशन होता है जहाँ हम डेटा स्टोर करते हैं। Declaration का मतलब है कंपाइलर को बताना कि यह variable किस नाम और डेटा टाइप का है। Initialization का मतलब उस variable को पहली बार कोई वैल्यू देना है, जैसे 'int a;' declaration है और 'a = 5;' initialization है।",
            "average_hi": "Variable डेटा स्टोर करने के काम आता है। Declaration में variable बनाते हैं और initialization में वैल्यू डालते हैं।",
            "weak_hi": "Variable वो होता है जो बदलता रहता है।"
        }
    },
    {
        "id": "prog_easy_2",
        "role": "Software Developer Intern",
        "skill": "Programming Fundamentals",
        "difficulty": "EASY",
        "question_en": "What is the difference between a 'while' loop and a 'for' loop? When would you prefer one over the other?",
        "question_hi": "'while' लूप और 'for' लूप में क्या अंतर है? आप एक के मुकाबले दूसरे को कब चुनेंगे?",
        "expected_concepts": ["iteration", "condition-based vs count-based", "known iterations vs unknown iterations", "loop structure"],
        "ideal_answer_points": [
            "A 'for' loop is generally used when the number of iterations is known beforehand.",
            "A 'while' loop is used when the number of iterations depends on an external condition or is unknown.",
            "Both can technically achieve the same results, but 'for' groups initialization, condition, and increment together."
        ],
        "rubric": {
            "excellent": "Clearly contrasts known vs condition-driven iterations, explains syntax differences, and gives practical use cases (e.g. iterating an array vs waiting for user input/network response).",
            "good": "Explains that for is for known counts and while is for conditions.",
            "average": "Knows both are loops but provides a shallow comparison.",
            "poor": "Cannot explain how either loop functions."
        },
        "follow_ups": [
            "What is a do-while loop and how does it differ from a while loop?",
            "How do you prevent an accidental infinite loop?"
        ],
        "demo_answers": {
            "strong_en": "A 'for' loop is best when we know the number of iterations in advance, such as looping through an array of known length. It bundles initialization, condition check, and increment in one line. A 'while' loop is preferred when iterations depend on dynamic conditions, like reading lines until EOF or waiting for user input.",
            "average_en": "A for loop has a counter and loops a set number of times. A while loop checks a condition and keeps running until that condition is false.",
            "weak_en": "Both are loops. You use for loop for lists and while loop for other things.",
            "strong_hi": "For loop का उपयोग तब किया जाता है जब हमें पहले से पता हो कि लूप कितनी बार चलना है, जैसे किसी Array को iterate करना। While loop का उपयोग तब करते हैं जब लूप का चलना किसी condition पर निर्भर करता है और iterations की संख्या पहले से तय नहीं होती, जैसे जब तक फ़ाइल समाप्त न हो।",
            "average_hi": "For loop गिनती के लिए होता है और while loop condition चेक करने के लिए जब तक सच हो।",
            "weak_hi": "दोनों लूप एक जैसे होते हैं बस नाम अलग है।"
        }
    },
    {
        "id": "prog_med_1",
        "role": "Software Developer Intern",
        "skill": "Programming Fundamentals",
        "difficulty": "MEDIUM",
        "question_en": "Can you explain the difference between Stack and Heap memory? How does memory allocation work in these two areas?",
        "question_hi": "Stack और Heap मेमोरी में क्या अंतर है? इन दोनों जगहों पर मेमोरी एलोकेशन कैसे काम करता है?",
        "expected_concepts": ["stack vs heap", "static vs dynamic allocation", "LIFO execution stack", "garbage collection / manual freeing", "speed differences"],
        "ideal_answer_points": [
            "Stack memory is used for static memory allocation, local variables, and function call frames, following LIFO.",
            "Heap memory is used for dynamic memory allocation where objects survive beyond a single function scope.",
            "Stack access is very fast and managed automatically by CPU, while Heap is larger, flexible, but slower and requires garbage collection or manual free."
        ],
        "rubric": {
            "excellent": "Mentions LIFO order, automatic deallocation of stack frames, dynamic sizing on heap, speed trade-offs, and fragmentation/garbage collection.",
            "good": "Explains stack is for local variables and heap is for dynamic objects, noting stack is faster.",
            "average": "Knows stack and heap exist but mixes up where objects and primitive variables reside.",
            "poor": "Vague or incorrect understanding of memory areas."
        },
        "follow_ups": [
            "What causes a Stack Overflow error?",
            "What is a memory leak and how does it happen in the heap?"
        ],
        "demo_answers": {
            "strong_en": "Stack memory is organized as a Last-In-First-Out structure used for function calls and local primitive variables. It is allocated and freed automatically, making it extremely fast. Heap memory is used for dynamic allocations where objects need to live beyond the scope of a single function. It requires manual memory management or garbage collection, making it slower and susceptible to fragmentation or memory leaks.",
            "average_en": "Stack is fast memory used for local function variables. Heap is larger memory used when you create new objects with the new keyword. Heap needs garbage collection.",
            "weak_en": "Stack is for data and heap is a pile of memory.",
            "strong_hi": "Stack मेमोरी LIFO (Last-In-First-Out) सिद्धांत पर काम करती है और इसका उपयोग लोकल वेरिएबल्स और फ़ंक्शन कॉल फ़्रेम्स के लिए होता है। यह बहुत तेज़ होती है और फ़ंक्शन खत्म होते ही अपने आप खाली हो जाती है। Heap मेमोरी डायनेमिक मेमोरी एलोकेशन के लिए होती है, जहाँ बड़े ऑब्जेक्ट्स स्टोर होते हैं। Heap बड़ी होती है लेकिन Stack से धीमी होती है और इसे गारबेज कलेक्टर या मैन्युअली फ्री करना पड़ता है।",
            "average_hi": "Stack फ़ंक्शन के अंदर के वेरिएबल्स के लिए होता है और Heap ऑब्जेक्ट्स के लिए। Stack तेज़ होता है।",
            "weak_hi": "मेमोरी दो तरह की होती है बस।"
        }
    },
    {
        "id": "prog_med_2",
        "role": "Software Developer Intern",
        "skill": "Programming Fundamentals",
        "difficulty": "MEDIUM",
        "question_en": "What is the difference between 'pass by value' and 'pass by reference'? How does this affect object mutation?",
        "question_hi": "'Pass by value' और 'pass by reference' में क्या अंतर है? यह ऑब्जेक्ट में बदलाव (mutation) को कैसे प्रभावित करता है?",
        "expected_concepts": ["pass by value", "pass by reference", "memory address/pointers", "copying values", "object mutations in callers"],
        "ideal_answer_points": [
            "Pass by value passes a copy of the actual variable data to the function; modifications do not affect the original.",
            "Pass by reference passes the memory address/reference, so changes inside the function modify the original variable.",
            "In languages like Python or JavaScript, references to objects are passed by value, meaning mutating object properties affects the caller, but reassigning the variable does not."
        ],
        "rubric": {
            "excellent": "Clearly distinguishes between value copy vs reference sharing, explains callers' scope impact, and clarifies nuanced behaviors (e.g. pass-by-value-of-reference).",
            "good": "Explains difference between modifying a copy versus modifying the original object.",
            "average": "Understands that one makes a copy and one modifies the original, but cannot explain how references work.",
            "poor": "Cannot explain value vs reference."
        },
        "follow_ups": [
            "How does JavaScript or Python handle arguments passed into functions?",
            "What is shallow copy versus deep copy?"
        ],
        "demo_answers": {
            "strong_en": "In pass by value, a copy of the variable's value is passed to the function, so changing it inside does not affect the original variable in the caller. In pass by reference, the actual memory address is passed, so any modification directly alters the caller's variable. Languages like Python pass references by value: modifying an object's attribute reflects outside, but reassigning the parameter does not.",
            "average_en": "Pass by value gives a copy so the original stays safe. Pass by reference points to the original memory so changing it changes the original data.",
            "weak_en": "Pass by value is for numbers and pass by reference is for strings.",
            "strong_hi": "Pass by value में फ़ंक्शन को वेरिएबल की एक कॉपी दी जाती है, इसलिए फ़ंक्शन के अंदर बदलाव करने पर ओरिजिनल वेरिएबल पर कोई असर नहीं पड़ता। Pass by reference में मेमोरी एड्रेस भेजा जाता है, जिससे फ़ंक्शन के अंदर किया गया कोई भी बदलाव सीधे ओरिजिनल डेटा में बदल जाता है।",
            "average_hi": "Value में कॉपी जाती है और reference में ओरिजिनल एड्रेस जाता है जिससे ओरिजिनल डेटा बदल जाता है।",
            "weak_hi": "दोनों में डेटा फ़ंक्शन में पास होता है।"
        }
    },
    {
        "id": "prog_hard_1",
        "role": "Software Developer Intern",
        "skill": "Programming Fundamentals",
        "difficulty": "HARD",
        "question_en": "How do Garbage Collection algorithms like Mark-and-Sweep work, and how can circular references cause memory leaks if not handled properly?",
        "question_hi": "Mark-and-Sweep जैसे Garbage Collection एल्गोरिदम कैसे काम करते हैं, और Circular References अगर ठीक से न संभाले जाएँ तो मेमोरी लीक कैसे पैदा कर सकते हैं?",
        "expected_concepts": ["Garbage Collection", "Mark and Sweep", "Root objects", "Reachability graph", "Reference Counting vs Tracing GC", "Circular References", "Weak References"],
        "ideal_answer_points": [
            "Mark-and-Sweep starts from root objects (globals, stack frames) and traverses the reachability graph to mark all reachable objects.",
            "In the sweep phase, any unmarked object is reclaimed from the heap.",
            "In naive reference counting, two objects referencing each other never reach zero count, causing a leak. Tracing GC (Mark-and-Sweep) handles circular references unless an external root keeps holding them."
        ],
        "rubric": {
            "excellent": "Distinguishes reference counting from tracing collectors, details root set traversal, explains mark phase vs sweep phase, and explains how circular references behave in both paradigms.",
            "good": "Explains the two phases of mark and sweep and identifies why circular references fail in reference counting.",
            "average": "Knows garbage collection cleans unused memory but lacks algorithmic details.",
            "poor": "Cannot explain garbage collection mechanics."
        },
        "follow_ups": [
            "What is generational garbage collection and why does it divide memory into young/old generations?",
            "How do weak references (WeakMap / weak_ptr) prevent circular memory leaks?"
        ],
        "demo_answers": {
            "strong_en": "Mark-and-Sweep is a tracing garbage collection algorithm. It begins from root references like global variables and current call stack frames, traversing object references and 'marking' every reachable object. In the sweep phase, any memory not marked is reclaimed. Circular references cause leaks in reference-counting collectors because their reference count never drops to zero, but Mark-and-Sweep resolves this if neither object is reachable from the roots.",
            "average_en": "Garbage collection finds memory you don't use anymore and frees it. Mark and sweep marks all reachable objects from roots and sweeps away the rest. Circular references can trick simple reference counters into keeping objects forever.",
            "weak_en": "Garbage collector deletes files and cleans RAM when full.",
            "strong_hi": "Mark-and-Sweep एक Tracing Garbage Collection एल्गोरिदम है। यह 'Root' ऑब्जेक्ट्स (जैसे ग्लोबल वेरिएबल्स और कॉल स्टैक) से शुरू होकर सभी पहुँचे जा सकने वाले (reachable) ऑब्जेक्ट्स को 'Mark' करता है। फिर Sweep चरण में उन सभी अन-मार्क ऑब्जेक्ट्स की मेमोरी को मुक्त करता है। Reference Counting में सर्कुलर रेफरेंस की वजह से काउंट कभी शून्य नहीं होता जिससे मेमोरी लीक होती है, लेकिन Mark-and-Sweep इसे संभाल लेता है यदि वे रूट्स से अनरीचेबल हों।",
            "average_hi": "Garbage collection अनयूज्ड मेमोरी को साफ़ करता है। Mark and sweep में पहले मार्क करते हैं फिर साफ़ करते हैं। सर्कुलर रेफरेंस मेमोरी लीक कर सकते हैं।",
            "weak_hi": "कचरा हटाने का सिस्टम होता है।"
        }
    },
    {
        "id": "prog_hard_2",
        "role": "Software Developer Intern",
        "skill": "Programming Fundamentals",
        "difficulty": "HARD",
        "question_en": "Explain the concept of Concurrency vs Parallelism. How do race conditions occur in multi-threaded programs and how do mutexes or semaphores prevent them?",
        "question_hi": "Concurrency और Parallelism की अवधारणा को समझाइए। मल्टी-थ्रेडेड प्रोग्राम्स में Race Conditions कैसे होती हैं और Mutex या Semaphore इन्हें कैसे रोकते हैं?",
        "expected_concepts": ["Concurrency vs Parallelism", "Multi-threading", "Race Condition", "Critical Section", "Mutex (Mutual Exclusion)", "Semaphore", "Atomic operations"],
        "ideal_answer_points": [
            "Concurrency is dealing with lots of things at once (structure/interleaving), while Parallelism is doing lots of things at once (simultaneous physical execution across cores).",
            "A race condition happens when multiple threads access shared mutable state concurrently, and the outcome depends on execution timing.",
            "A mutex locks the critical section so only one thread can enter at a time. A semaphore maintains a counter allowing a fixed number of concurrent accesses."
        ],
        "rubric": {
            "excellent": "Sharp distinction between concurrency and parallelism, precise definition of race condition with shared mutable state, and correct technical explanation of mutex locking vs semaphore signaling.",
            "good": "Explains concurrency vs parallelism well and explains how a mutex prevents threads from clashing.",
            "average": "Confuses concurrency and parallelism but understands locking.",
            "poor": "Fails to explain race conditions or threads."
        },
        "follow_ups": [
            "What is a deadlock and what are the Coffman conditions required for it to occur?",
            "What is the difference between a binary semaphore and a mutex?"
        ],
        "demo_answers": {
            "strong_en": "Concurrency is about structure—handling multiple tasks by interleaving execution, even on a single core. Parallelism is about simultaneous execution of tasks on multiple CPU cores. A race condition occurs when two threads read and write shared memory without synchronization, leading to unpredictable states. A mutex enforces mutual exclusion by locking the critical section to a single thread, while a semaphore uses a counter to control access for up to N threads.",
            "average_en": "Concurrency means managing multiple tasks at once, parallelism means actually running them at the exact same time on multi-core CPUs. Race conditions happen when threads fight over the same variable. Mutex locks it so only one thread touches it at a time.",
            "weak_en": "Concurrency is fast and parallelism is running threads.",
            "strong_hi": "Concurrency का मतलब है एक साथ कई कामों को मैनेज करना (भले ही सिंगल कोर पर टाइम-स्लाइसिंग से हो), जबकि Parallelism का अर्थ है कई CPU कोरों पर एक ही समय में वास्तविक रूप से काम चलना। Race condition तब होती है जब दो थ्रेड्स बिना सिंक्रोनाइज़ेशन के एक ही शेयर किए गए डेटा को पढ़ते या बदलते हैं। Mutex क्रिटिकल सेक्शन को लॉक कर देता है ताकि एक बार में सिर्फ एक थ्रेड प्रवेश कर सके, और Semaphore एक काउंटर के जरिए सीमित थ्रेड्स को अनुमति देता है।",
            "average_hi": "Concurrency में कई काम एक साथ दिखते हैं, parallelism में सच में कई कोर पर चलते हैं। Race condition रोकने के लिए mutex लॉक लगाया जाता है।",
            "weak_hi": "मल्टीटास्किंग के लिए थ्रेड्स होते हैं।"
        }
    },

    # ========================================================
    # 2. PROBLEM SOLVING
    # ========================================================
    {
        "id": "prob_easy_1",
        "role": "Software Developer Intern",
        "skill": "Problem Solving",
        "difficulty": "EASY",
        "question_en": "Suppose you are given an array of integers and asked to find the maximum number. How would you approach solving this problem step-by-step?",
        "question_hi": "मान लीजिए आपको पूर्णांकों (integers) का एक Array दिया गया है और सबसे बड़ी संख्या ढूंढनी है। आप इसे चरण-दर-चरण (step-by-step) कैसे हल करेंगे?",
        "expected_concepts": ["edge cases (empty array)", "initialization", "single pass iteration", "comparison logic", "O(N) time complexity"],
        "ideal_answer_points": [
            "Check for edge cases: handle empty array or single-element array.",
            "Initialize a 'max' variable to the first element (or negative infinity).",
            "Iterate through the array from the second element, comparing each with current max.",
            "Update max if the current element is greater, returning max after one full pass (O(N) time, O(1) space)."
        ],
        "rubric": {
            "excellent": "Mentions empty array validation, initializes max to first element, iterates in a single O(N) pass, explains space complexity O(1).",
            "good": "Gives clear algorithm to loop through array and track max, mentions time complexity.",
            "average": "Explains looping and comparison, but forgets edge cases or suggests sorting first.",
            "poor": "Unclear logic or cannot outline steps."
        },
        "follow_ups": [
            "What if the array has millions of elements streaming in one by one?",
            "Why is sorting the array first (O(N log N)) less optimal than a single pass?"
        ],
        "demo_answers": {
            "strong_en": "First, I would validate edge cases: if the array is empty, return null or raise an error; if it has one element, that element is the maximum. Next, initialize `max` with the first element. Then loop through the remaining elements: if the current element is greater than `max`, update `max`. Finally, return `max`. This runs in O(N) linear time and O(1) constant auxiliary space.",
            "average_en": "I will make a variable called max and set it to the first element. Then I will loop through all elements and if an element is bigger than max, I set max to that element. At the end, return max. Time is O(N).",
            "weak_en": "Sort the array and pick the last number.",
            "strong_hi": "सबसे पहले मैं Edge Case चेक करूँगा: यदि Array खाली है तो error या null लौटाएँगे, यदि एक एलिमेंट है तो वही maximum है। फिर `max` वेरिएबल को पहले एलिमेंट के बराबर सेट करूँगा। इसके बाद बाकी एलिमेंट्स में लूप चलाकर तुलना करूँगा: यदि वर्तमान संख्या `max` से बड़ी है, तो `max` को अपडेट करूँगा। यह O(N) समय और O(1) स्पेस में पूरा होगा।",
            "average_hi": "पहले एलिमेंट को max मानेंगे और पूरे array में लूप चलाकर जो बड़ा मिलेगा उसे max बना देंगे। समय O(N) लगेगा।",
            "weak_hi": "Array को sort करके आखिरी नंबर ले लेंगे।"
        }
    },
    {
        "id": "prob_easy_2",
        "role": "Software Developer Intern",
        "skill": "Problem Solving",
        "difficulty": "EASY",
        "question_en": "How would you check if a given word or phrase is a palindrome (reads the same forwards and backwards)?",
        "question_hi": "आप कैसे जांचेंगे कि कोई शब्द या वाक्य एक Palindrome है (जो आगे और पीछे दोनों तरफ से पढ़ने पर एक जैसा हो)?",
        "expected_concepts": ["two-pointer technique", "string reversal", "case sensitivity / whitespace cleaning", "O(N) time complexity"],
        "ideal_answer_points": [
            "Clean the input by converting to lowercase and stripping non-alphanumeric characters if evaluating a phrase.",
            "Use a two-pointer approach: one pointer at the start, one at the end.",
            "Compare characters while moving pointers toward the center; if any pair differs, return false.",
            "If pointers cross without mismatches, it is a palindrome (O(N) time, O(1) space)."
        ],
        "rubric": {
            "excellent": "Mentions two pointers, handles case-insensitivity and punctuation cleaning, details O(N) time and O(1) extra space.",
            "good": "Explains comparing characters from both ends or reversing the string and comparing.",
            "average": "Suggests reversing string but ignores space complexity or edge cases.",
            "poor": "Cannot explain how palindrome checking works."
        },
        "follow_ups": [
            "Why is the two-pointer approach better than reversing the string into a new variable in terms of memory?",
            "How would you handle Unicode or accented characters?"
        ],
        "demo_answers": {
            "strong_en": "I would use a two-pointer approach. First, normalize the string by converting to lowercase and optionally removing spaces and punctuation. Place pointer `left` at index 0 and `right` at the last index. In a while loop where left < right, compare characters: if they don't match, return false; otherwise, increment left and decrement right. If loop completes, return true. This is O(N) time and O(1) auxiliary space.",
            "average_en": "You can reverse the string and check if the reversed string equals the original string. Or use two pointers from front and back to compare characters.",
            "weak_en": "Check if first letter equals last letter.",
            "strong_hi": "मैं Two-Pointer अप्रोच का इस्तेमाल करूँगा। पहले स्ट्रिंग को lowercase में बदलकर स्पेस हटा देंगे। एक पॉइंटर शुरुआत (left) पर और एक अंत (right) पर रखेंगे। जब तक left < right हो, दोनों अक्षरों की तुलना करेंगे। अगर कोई असमानता मिली तो false, नहीं तो left++ और right-- करेंगे। यह O(N) समय और O(1) अतिरिक्त मेमोरी में हो जाता है।",
            "average_hi": "स्ट्रिंग को उल्टा करके ओरिजिनल स्ट्रिंग से मिला लेंगे अगर दोनों बराबर हैं तो palindrome है।",
            "weak_hi": "पहला और आखिरी अक्षर मिला लेंगे।"
        }
    },
    {
        "id": "prob_med_1",
        "role": "Software Developer Intern",
        "skill": "Problem Solving",
        "difficulty": "MEDIUM",
        "question_en": "Given an array of integers and a target sum, how would you find two numbers that add up to the target? Compare the brute force approach with an optimized solution.",
        "question_hi": "पूर्णांकों (integers) के एक Array और एक Target Sum के साथ, आप ऐसे दो नंबर कैसे ढूँढेंगे जिनका जोड़ target के बराबर हो? Brute force और Optimized समाधान की तुलना कीजिए।",
        "expected_concepts": ["Two Sum problem", "Brute force O(N^2)", "Hash Map / Set lookup O(N)", "Space-Time Tradeoff", "Complement calculation"],
        "ideal_answer_points": [
            "Brute force: nested loops checking every pair (i, j), taking O(N^2) time and O(1) space.",
            "Optimized: use a Hash Map storing value -> index. In a single pass, check if target - current exists in map.",
            "Optimized approach achieves O(N) time with O(N) space complexity."
        ],
        "rubric": {
            "excellent": "Clearly explains both approaches, computes complement `target - num`, explains Hash Map O(1) average lookup, and states exact time/space complexities for both.",
            "good": "Explains brute force O(N^2) and hash map O(N) correctly.",
            "average": "Suggests sorting and two pointers without realizing original indices may be needed or mentions hash map vaguely.",
            "poor": "Fails to provide an algorithm better than random guessing."
        },
        "follow_ups": [
            "What if the array is already sorted? Can we solve it in O(1) space?",
            "What happens if there are duplicate numbers in the array?"
        ],
        "demo_answers": {
            "strong_en": "The brute force approach uses two nested loops to check every possible pair, which takes O(N^2) time and O(1) space. The optimized approach uses a Hash Map for an O(N) time and O(N) space solution. As we iterate through the array, we calculate the complement `target - current_number`. If the complement is already in our map, we have found our pair and return their indices. Otherwise, we store the current number and its index in the map.",
            "average_en": "Brute force checks every combination with two loops taking O(N^2). We can optimize it by putting numbers into a hash table and looking up target minus number in O(1) time, making the whole algorithm O(N).",
            "weak_en": "Add numbers one by one until you reach the target.",
            "strong_hi": "Brute force तरीके में दो नेस्टेड लूप्स लगाकर हर जोड़े की जांच करते हैं, जिसमें O(N^2) समय लगता है। इसका अनुकूलित (optimized) समाधान Hash Map का उपयोग करना है। हम Array में एक ही बार iterate करते हैं और हर नंबर के लिए `complement = target - number` निकालते हैं। अगर वह Hash Map में मौजूद है, तो हमें उत्तर मिल गया। नहीं तो मौजूदा नंबर को Map में डाल देते हैं। यह O(N) समय और O(N) स्पेस लेता है।",
            "average_hi": "Brute force में दो लूप से O(N^2) लगता है। Hash map इस्तेमाल करके हम O(N) समय में target - x ढूँढ सकते हैं।",
            "weak_hi": "सारे नंबर जोड़ कर देख लेंगे।"
        }
    },
    {
        "id": "prob_med_2",
        "role": "Software Developer Intern",
        "skill": "Problem Solving",
        "difficulty": "MEDIUM",
        "question_en": "Imagine a web app is running very slowly when fetching a list of 10,000 items from an API. As a developer, how would you diagnose and solve this problem?",
        "question_hi": "कल्पना कीजिए कि एक वेब ऐप API से 10,000 आइटम्स की लिस्ट लाते समय बहुत धीमा चल रहा है। एक डेवलपर के रूप में, आप इस समस्या की पहचान (diagnose) और समाधान (solve) कैसे करेंगे?",
        "expected_concepts": ["Network/payload bottleneck", "Pagination / Infinite scrolling", "Virtualization / Windowing", "Backend query indexing", "Caching"],
        "ideal_answer_points": [
            "Diagnose using browser DevTools Network tab (TTFB vs download time) and backend profiling.",
            "Backend solutions: implement pagination (limit/offset or cursor-based) so only 20-50 items are sent per request.",
            "Frontend solutions: implement virtualized list rendering (e.g., react-window) so only visible DOM nodes are created.",
            "Add caching (Redis on backend, HTTP cache headers) and database indexing."
        ],
        "rubric": {
            "excellent": "Breaks diagnosis into frontend vs backend vs network, suggests pagination/cursor pagination, virtualized DOM rendering, and caching.",
            "good": "Suggests pagination and checking browser network tab.",
            "average": "Suggests reducing data or making internet faster.",
            "poor": "Cannot explain how to diagnose or solve slow API responses."
        },
        "follow_ups": [
            "What is the difference between offset pagination and cursor-based pagination?",
            "What is DOM virtualization and why does rendering 10,000 DOM nodes freeze the browser?"
        ],
        "demo_answers": {
            "strong_en": "First, I would diagnose where the bottleneck lies using Chrome DevTools Network tab: checking TTFB to see if the database query is slow, or payload transfer time if JSON size is huge. To fix this, on the backend I would implement cursor-based pagination to return only 20-50 items at a time, along with database indexing and caching. On the frontend, I would implement virtualized rendering so only visible items exist in the DOM, preventing browser UI freezes.",
            "average_en": "I would check network tab in dev tools to see why it takes long. Then I would add pagination so the API returns 20 items per page instead of 10,000 all at once, and add caching.",
            "weak_en": "Restart the server and check internet connection.",
            "strong_hi": "सबसे पहले मैं Browser DevTools के Network Tab से समस्या की पहचान करूँगा—क्या TTFB (Backend Database) में देरी है या 10,000 आइटम्स का JSON डाउनलोड होने में। समाधान के लिए: Backend पर Pagination (Cursor-based) लागू करेंगे ताकि एक बार में केवल 20-50 आइटम्स आएँ। Frontend पर Virtualization लागू करेंगे ताकि केवल स्क्रीन पर दिखने वाले DOM नोड्स ही रेंडर हों, जिससे ब्राउज़र हैंग न हो।",
            "average_hi": "Devtools से चेक करेंगे कि क्या धीमा है। फिर 10,000 की जगह Pagination लगाकर 20-20 डेटा भेजेंगे।",
            "weak_hi": "सर्वर रीस्टार्ट कर देंगे।"
        }
    },
    {
        "id": "prob_hard_1",
        "role": "Software Developer Intern",
        "skill": "Problem Solving",
        "difficulty": "HARD",
        "question_en": "How would you design a rate limiter for an API that allows a maximum of 100 requests per minute per user? Explain the algorithm and data structures you would use.",
        "question_hi": "आप किसी API के लिए Rate Limiter कैसे डिज़ाइन करेंगे जो प्रति यूज़र प्रति मिनट अधिकतम 100 अनुरोधों (requests) की अनुमति देता है? अपने एल्गोरिदम और डेटा स्ट्रक्चर्स को समझाइए।",
        "expected_concepts": ["Token Bucket / Leaky Bucket / Sliding Window Log", "Redis atomic operations", "Distributed state", "HTTP 429 Too Many Requests", "Key expiry (TTL)"],
        "ideal_answer_points": [
            "Discuss algorithms: Fixed Window Counter (burst flaw), Sliding Window Counter, or Token Bucket.",
            "Token Bucket: users have a bucket of 100 tokens, refilled at constant rate; request takes 1 token.",
            "Implementation using Redis with user_id key, sorted sets (ZSET) for sliding window timestamps or atomic INCR with EXPIRE.",
            "Return HTTP 429 with `Retry-After` header when limit exceeded."
        ],
        "rubric": {
            "excellent": "Evaluates Token Bucket or Sliding Window algorithm, details Redis storage, handles atomic updates, and specifies HTTP 429 response headers.",
            "good": "Explains Token bucket or window counting with Redis and user keys.",
            "average": "Understands counting requests in a dictionary but misses distributed environment and edge cases.",
            "poor": "Cannot explain how a rate limiter functions."
        },
        "follow_ups": [
            "How does the sliding window log prevent the boundary burst issue of the fixed window algorithm?",
            "What happens if Redis goes down—how should your rate limiter fail (fail-open vs fail-closed)?"
        ],
        "demo_answers": {
            "strong_en": "I would use a Sliding Window Counter algorithm or Token Bucket. In a distributed environment, I'd store state in Redis keyed by `rate_limit:{user_id}`. With a sliding window log using Redis Sorted Sets (ZSET), each request adds current timestamp as member and score. We remove timestamps older than 60 seconds using ZREMRANGEBYSCORE, count remaining elements with ZCARD: if count < 100, allow; otherwise reject with HTTP 429 and `Retry-After` header.",
            "average_en": "I would use Redis with the user's ID as key. We can store request timestamps in a list or sorted set. If there are more than 100 requests in the last 60 seconds, return HTTP 429 status code. Otherwise increment the counter.",
            "weak_en": "Create a counter in a global variable and reset it every minute.",
            "strong_hi": "मैं Token Bucket या Sliding Window Counter एल्गोरिदम का उपयोग करूँगा। Distributed सिस्टम के लिए Redis का इस्तेमाल करेंगे जहाँ Key `ratelimit:{user_id}` होगी। Redis Sorted Set (ZSET) में हर रिक्वेस्ट का टाइमस्टैम्प स्टोर करेंगे। पिछले 60 सेकंड से पुराने टाइमस्टैम्प हटाकर ZCARD से काउंट चेक करेंगे। यदि काउंट 100 से कम है तो रिक्वेस्ट पास होगी, अन्यथा HTTP 429 (Too Many Requests) और `Retry-After` हेडर लौटाएँगे।",
            "average_hi": "Redis में यूज़र आईडी के साथ काउंटर रखेंगे और हर मिनट बाद रिसेट करेंगे। 100 से ज्यादा होने पर 429 एरर देंगे।",
            "weak_hi": "इफ कंडीशन लगा देंगे कि 100 से ज्यादा न हो।"
        }
    },
    {
        "id": "prob_hard_2",
        "role": "Software Developer Intern",
        "skill": "Problem Solving",
        "difficulty": "HARD",
        "question_en": "You are asked to build an autocomplete search feature for millions of product names. How would you structure the data and query system for millisecond response times?",
        "question_hi": "आपको लाखों प्रोडक्ट्स के नामों के लिए एक Autocomplete Search फ़ीचर बनाना है। मिलीसेकंड रिस्पॉन्स टाइम के लिए आप डेटा स्ट्रक्चर और क्वेरी सिस्टम को कैसे डिज़ाइन करेंगे?",
        "expected_concepts": ["Trie / Prefix Tree", "Inverted Index / Elasticsearch", "Caching top prefixes", "Debounce on frontend", "Ranking / Frequency scores"],
        "ideal_answer_points": [
            "Data structure: Trie (Prefix Tree) where each node represents a character and holds top-k frequent completions.",
            "Frontend: implement input debouncing (e.g. 200-300ms) to avoid spamming the backend on every keystroke.",
            "Backend/Storage: Pre-compute top suggestions at Trie nodes or use Elasticsearch / Redis prefix indices.",
            "Caching: Cache common short prefixes (e.g. 'ip', 'iph', 'iphon') in an in-memory cache."
        ],
        "rubric": {
            "excellent": "Proposes Trie with pre-stored top results at nodes, frontend debouncing, caching strategies, and mentions scaling via sharding or search engines like Elasticsearch.",
            "good": "Explains Trie data structure and frontend debouncing with caching.",
            "average": "Suggests SQL LIKE '%query%' which is slow, but recognizes need for caching.",
            "poor": "No structured idea of search or autocomplete data structures."
        },
        "follow_ups": [
            "How does storing top-5 suggestions at each Trie node reduce search complexity from O(depth + subtree) to O(prefix length)?",
            "How would you handle typo-tolerance (fuzzy search) in autocomplete?"
        ],
        "demo_answers": {
            "strong_en": "I would use a Trie (Prefix Tree) data structure. To achieve single-digit millisecond latency, each Trie node should store the top 5-10 most popular product completions precomputed, avoiding expensive subtree traversals at runtime. On the frontend, we debounce keystrokes by 250ms. Common 2-3 letter prefixes are cached in Redis or CDN. For large scale, an Elasticsearch completion suggester backed by finite state transducers (FST) would be ideal.",
            "average_en": "A Trie is the best data structure because it matches by prefix. You can put the product names into a Trie. On the client side, use debounce so it doesn't query on every letter. Cache popular searches in Redis.",
            "weak_en": "Use SQL LIKE query on the database table.",
            "strong_hi": "मैं Trie (Prefix Tree) डेटा स्ट्रक्चर का उपयोग करूँगा। मिलीसेकंड रिस्पॉन्स के लिए, हर Trie नोड पर टॉप 5-10 सबसे लोकप्रिय प्रोडक्ट्स की लिस्ट पहले से स्टोर रखेंगे ताकि रनटाइम पर सबट्री न खंगालना पड़े। Frontend पर 200-300ms का Debounce लगाएँगे। लोकप्रिय छोटे प्रीफ़िक्स को Redis या CDN में कैश करेंगे। बड़े पैमाने पर Elasticsearch FST Suggester भी इस्तेमाल कर सकते हैं।",
            "average_hi": "Trie डेटा स्ट्रक्चर सबसे अच्छा रहेगा प्रीफ़िक्स सर्च के लिए। साथ में Redis कैशिंग और Frontend पर debounce यूज़ करेंगे।",
            "weak_hi": "डेटाबेस में सर्च क्वेरी चला देंगे।"
        }
    },

    # ========================================================
    # 3. DATA STRUCTURES & ALGORITHMS (DSA)
    # ========================================================
    {
        "id": "dsa_easy_1",
        "role": "Software Developer Intern",
        "skill": "Data Structures & Algorithms",
        "difficulty": "EASY",
        "question_en": "What is the difference between an Array and a Linked List? What are their time complexities for accessing and inserting elements?",
        "question_hi": "Array और Linked List में क्या अंतर है? एलिमेंट्स को एक्सेस और इन्सर्ट करने में उनकी Time Complexities क्या होती हैं?",
        "expected_concepts": ["contiguous vs non-contiguous memory", "random access vs sequential traversal", "O(1) access in array", "O(1) insertion at head in linked list", "cache locality"],
        "ideal_answer_points": [
            "Array stores elements in contiguous memory: access is O(1) by index, insertion/deletion in middle is O(N) due to shifting.",
            "Linked List stores nodes with data and pointers in non-contiguous memory: access is O(N) sequential search, insertion at known position/head is O(1).",
            "Arrays have better cache locality; linked lists have extra memory overhead for pointers."
        ],
        "rubric": {
            "excellent": "Accurately details memory layout (contiguous vs pointer-based), compares access (O(1) vs O(N)) and insertion (O(N) vs O(1)), mentions cache locality and pointer overhead.",
            "good": "Correctly states O(1) vs O(N) access and explains basic differences.",
            "average": "Knows both store items, but confuses access or insertion complexities.",
            "poor": "Cannot explain how a linked list differs from an array."
        },
        "follow_ups": [
            "Why do arrays have better CPU cache performance than linked lists?",
            "What is a doubly linked list and what extra capabilities does it provide?"
        ],
        "demo_answers": {
            "strong_en": "An array stores elements in contiguous memory locations, enabling instant O(1) random access via index arithmetic. However, inserting or deleting elements requires shifting, taking O(N) time. In contrast, a Linked List stores nodes scattered in memory connected by pointers. Access requires traversing from head taking O(N) time, but inserting at the head or known pointer is O(1) without shifting. Arrays also offer superior CPU cache locality.",
            "average_en": "Arrays have contiguous memory so you can access elements in O(1) time, but inserting takes O(N) because elements shift. Linked lists use pointers, so access is O(N) but inserting at the beginning is O(1).",
            "weak_en": "Array has fixed size and linked list is a list with links.",
            "strong_hi": "Array एलिमेंट्स को मेमोरी में लगातार (contiguous) जगह पर स्टोर करता है, इसलिए इंडेक्स के जरिए O(1) समय में रैंडम एक्सेस मिलता है। लेकिन बीच में इन्सर्ट करने पर एलिमेंट्स को शिफ्ट करना पड़ता है जो O(N) लेता है। Linked List में नोड्स पॉइंटर्स के जरिए जुड़े होते हैं, इसलिए एक्सेस करने में O(N) लगता है, पर किसी ज्ञात नोड या हेड पर इन्सर्ट करना O(1) में हो जाता है।",
            "average_hi": "Array में इंडेक्स से सीधा O(1) में मिल जाता है, Linked List में आगे से ढूँढना पड़ता है तो O(N) लगता है। Linked list में इन्सर्शन आसान होता है।",
            "weak_hi": "दोनों लिस्ट ही हैं बस नाम अलग है।"
        }
    },
    {
        "id": "dsa_easy_2",
        "role": "Software Developer Intern",
        "skill": "Data Structures & Algorithms",
        "difficulty": "EASY",
        "question_en": "How does Binary Search work, and what prerequisite must be satisfied before you can use it on an array?",
        "question_hi": "Binary Search कैसे काम करता है, और किसी Array पर इसे इस्तेमाल करने से पहले कौन सी शर्त (prerequisite) पूरी होनी चाहिए?",
        "expected_concepts": ["sorted array prerequisite", "divide and conquer", "halving search space", "O(log N) time complexity", "midpoint comparison"],
        "ideal_answer_points": [
            "Prerequisite: the array must be sorted in order.",
            "Mechanism: find midpoint, compare target with midpoint element.",
            "If target equals midpoint, return index; if smaller, search left half; if larger, search right half.",
            "Repeats until target is found or search space is empty, running in O(log N) time."
        ],
        "rubric": {
            "excellent": "Explicitly names sorted order requirement, details midpoint calculation `low + (high - low)/2` to prevent overflow, explains halving search space, gives O(log N) time.",
            "good": "Mentions sorted requirement and explains divide-and-conquer steps with O(log N).",
            "average": "Explains splitting in half but forgets that the array must be sorted.",
            "poor": "Confuses linear search with binary search."
        },
        "follow_ups": [
            "Why is `low + (high - low) / 2` preferred over `(low + high) / 2`?",
            "What is the space complexity of iterative vs recursive binary search?"
        ],
        "demo_answers": {
            "strong_en": "Binary Search requires the array to be sorted beforehand. It works by divide-and-conquer: compare target with the middle element. If they match, return its index. If target is smaller, eliminate the right half and search the left; if larger, search the right. This halves the search space at every step, yielding an efficient O(log N) time complexity, far faster than O(N) linear search.",
            "average_en": "The array must be sorted first. You check the middle element, and if the target is smaller you look in the left half, otherwise the right half. It keeps dividing by two so time is O(log N).",
            "weak_en": "It searches by converting numbers into binary.",
            "strong_hi": "Binary Search की सबसे मुख्य शर्त यह है कि Array का पहले से 'Sorted' होना अनिवार्य है। यह Divide-and-Conquer पर काम करता है: यह बीच वाले एलिमेंट से टारगेट की तुलना करता है। यदि टारगेट छोटा है, तो दाईं ओर का आधा हिस्सा छोड़ कर बाईं ओर खोजते हैं; यदि बड़ा है तो दाईं ओर। हर कदम पर सर्च स्पेस आधा हो जाता है, जिससे टाइम कॉम्प्लेक्सिटी O(log N) होती है।",
            "average_hi": "Array sorted होना चाहिए। बीच का नंबर देखते हैं और हर बार आधा-आधा हिस्सा चेक करते हैं। इसका टाइम O(log N) होता है।",
            "weak_hi": "नंबर्स को 0 और 1 में बदलकर ढूंढते हैं।"
        }
    },
    {
        "id": "dsa_med_1",
        "role": "Software Developer Intern",
        "skill": "Data Structures & Algorithms",
        "difficulty": "MEDIUM",
        "question_en": "Can you explain how a Hash Table handles collisions? Describe at least two collision resolution techniques.",
        "question_hi": "क्या आप समझा सकते हैं कि Hash Table में Collisions को कैसे संभाला जाता है? कम से कम दो Collision Resolution तकनीकों का वर्णन कीजिए।",
        "expected_concepts": ["Hash function", "Collision", "Separate Chaining", "Open Addressing (Linear Probing, Quadratic Probing, Double Hashing)", "Load factor"],
        "ideal_answer_points": [
            "A collision occurs when two distinct keys produce the same hash index.",
            "Technique 1: Separate Chaining (each bucket stores a linked list/tree of colliding entries).",
            "Technique 2: Open Addressing (Linear Probing searches next available slot: index + 1, index + 2, etc.).",
            "Maintaining a low load factor (typically <= 0.7) and resizing ensures average O(1) lookup."
        ],
        "rubric": {
            "excellent": "Explains why collisions happen, compares Separate Chaining and Open Addressing with trade-offs, mentions load factor and rehashing.",
            "good": "Explains chaining and linear probing correctly.",
            "average": "Mentions linked list in buckets but struggles to explain open addressing.",
            "poor": "Does not understand what a hash collision is."
        },
        "follow_ups": [
            "Why did Java 8 change HashMap bucket lists into Red-Black Trees when length exceeds 8?",
            "What is primary clustering in linear probing and how does double hashing solve it?"
        ],
        "demo_answers": {
            "strong_en": "A collision happens when two keys hash to the same bucket index. Two primary resolution techniques are: 1. Separate Chaining: Each bucket holds a linked list or balanced tree of entries that hash to that slot. Lookup scans that bucket. 2. Open Addressing (e.g. Linear Probing): All elements stay inside the table array; if the hashed slot is occupied, it probes the next sequential slot until an empty one is found. Keeping load factor below ~0.75 ensures average O(1) performance.",
            "average_en": "Collisions happen when two keys get the same hash code. Chaining puts a linked list at that array index so multiple items can live there. Linear probing searches for the next empty slot in the array. Average time remains O(1).",
            "weak_en": "Collision is when two things crash. The hash table throws an error.",
            "strong_hi": "Hash Collision तब होती है जब दो अलग-अलग Keys का एक ही Hash इंडेक्स बन जाता है। इसे सुलझाने के दो मुख्य तरीके हैं: 1. Separate Chaining: हर बकेट में एक Linked List या Tree होती है, जहाँ टकराने वाले सभी आइटम्स जुड़ जाते हैं। 2. Open Addressing (Linear Probing): यदि तय स्लॉट भरा हुआ है, तो अगला खाली स्लॉट (index + 1) ढूँढकर वहाँ स्टोर किया जाता है। Load Factor को नियंत्रित रखकर औसत O(1) समय बना रहता है।",
            "average_hi": "Chaining में बकेट के अंदर linked list बना देते हैं। Linear probing में अगला खाली स्लॉट ढूंढ कर रख देते हैं। इससे collision सुलझ जाता है।",
            "weak_hi": "Hash table एरर दे देता है।"
        }
    },
    {
        "id": "dsa_med_2",
        "role": "Software Developer Intern",
        "skill": "Data Structures & Algorithms",
        "difficulty": "MEDIUM",
        "question_en": "What is the difference between Depth-First Search (DFS) and Breadth-First Search (BFS) in a graph? Which data structures do they each use?",
        "question_hi": "Graph में Depth-First Search (DFS) और Breadth-First Search (BFS) में क्या अंतर है? वे दोनों किन डेटा स्ट्रक्चर्स का उपयोग करते हैं?",
        "expected_concepts": ["DFS vs BFS", "Stack (or recursion) for DFS", "Queue (FIFO) for BFS", "Level-order traversal vs deep traversal", "Shortest path in unweighted graph", "Visited set"],
        "ideal_answer_points": [
            "DFS explores as deep as possible along each branch before backtracking; it uses a Stack (or call stack recursion).",
            "BFS explores neighbor nodes level by level; it uses a Queue (FIFO).",
            "BFS is guaranteed to find the shortest path in an unweighted graph, whereas DFS is useful for cycle detection, topological sort, and path existence.",
            "Both use a visited set to avoid infinite loops in cyclic graphs."
        ],
        "rubric": {
            "excellent": "Identifies Stack for DFS and Queue for BFS, explains traversal mechanics, highlights BFS for shortest path in unweighted graphs and DFS for topological sort/backtracking, mentions visited tracking.",
            "good": "Explains DFS goes deep with stack, BFS goes wide with queue.",
            "average": "Confuses which data structure belongs to which algorithm.",
            "poor": "Cannot describe how either graph traversal algorithm works."
        },
        "follow_ups": [
            "Why is BFS better than DFS for finding the shortest path in an unweighted graph?",
            "What is the time complexity of BFS/DFS on an adjacency list representation?"
        ],
        "demo_answers": {
            "strong_en": "DFS explores deeply down a branch before backtracking, using a Stack or recursion. It is ideal for cycle detection, topological sorting, and mazes. BFS explores level-by-level, visiting all immediate neighbors first, using a Queue (FIFO). BFS guarantees finding the shortest path in an unweighted graph. Both have O(V + E) time complexity with an adjacency list and require a visited set to handle cycles.",
            "average_en": "DFS goes deep down nodes and uses a stack or recursive function. BFS goes layer by layer and uses a queue. BFS is great for finding the shortest distance in unweighted graphs.",
            "weak_en": "DFS is for depth and BFS is for breadth. They search trees.",
            "strong_hi": "DFS (Depth-First Search) किसी ब्रांच में गहराई तक जाता है और फिर बैकट्रैक करता है, इसके लिए Stack (या रिकर्शन) का उपयोग होता है। BFS (Breadth-First Search) लेवल-दर-लेवल सभी पड़ोसी नोड्स को पहले देखता है, इसके लिए Queue (FIFO) का उपयोग होता है। अनवेटेड ग्राफ में सबसे छोटा रास्ता (Shortest Path) ढूँढने के लिए BFS सबसे उपयुक्त है। दोनों में O(V+E) समय लगता है।",
            "average_hi": "DFS गहराई में जाता है और Stack इस्तेमाल करता है। BFS लेवल वाइज़ जाता है और Queue इस्तेमाल करता है।",
            "weak_hi": "दोनों ग्राफ में सर्च करने के तरीके हैं।"
        }
    },
    {
        "id": "dsa_hard_1",
        "role": "Software Developer Intern",
        "skill": "Data Structures & Algorithms",
        "difficulty": "HARD",
        "question_en": "How would you implement a Least Recently Used (LRU) Cache with O(1) get and put operations? Which combination of data structures makes this possible?",
        "question_hi": "आप O(1) get और put ऑपरेशन्स के साथ Least Recently Used (LRU) Cache कैसे बनाएंगे? कौन से डेटा स्ट्रक्चर्स का संयोजन इसे संभव बनाता है?",
        "expected_concepts": ["LRU Cache", "Hash Map + Doubly Linked List", "O(1) lookup", "O(1) removal and insertion", "Eviction of tail node", "Moving accessed node to head"],
        "ideal_answer_points": [
            "Combine a Hash Map with a Doubly Linked List.",
            "The Hash Map maps key -> Doubly Linked List node for O(1) lookup.",
            "The Doubly Linked List maintains recency order: most recently used at head, least recently used at tail.",
            "On get(key): locate node in O(1) via map, detach node and move to head in O(1).",
            "On put(key, val): update/insert node at head; if capacity exceeded, evict tail node and remove its key from map in O(1)."
        ],
        "rubric": {
            "excellent": "Names Hash Map + Doubly Linked List, explains why singly linked list cannot do O(1) node deletion, details head/tail pointers and eviction steps.",
            "good": "Explains Hash Map for lookup and Doubly Linked list for ordering in O(1).",
            "average": "Suggests hash map and array, missing that array deletion is O(N).",
            "poor": "Cannot explain how to achieve O(1) for both operations."
        },
        "follow_ups": [
            "Why doesn't a Singly Linked List allow O(1) node deletion even if you have a direct pointer to the node?",
            "How do dummy head and dummy tail sentinel nodes simplify LRU cache implementation?"
        ],
        "demo_answers": {
            "strong_en": "To achieve O(1) for both `get` and `put`, we combine a Hash Map and a Doubly Linked List. The Hash Map stores `key -> Node` pointers for O(1) access. The Doubly Linked List maintains usage order: most recently used at head, least recently used at tail. When `get(key)` is called, we locate the node in O(1) via the map and splice it to the head in O(1). When `put` exceeds capacity, we remove the tail node in O(1) and delete its entry from the hash map.",
            "average_en": "You combine a Hash Map and a Doubly Linked List. Hash map gives O(1) lookup by key. The doubly linked list lets you add and remove nodes in O(1) time. The head is most recently used and the tail is least recently used, which gets evicted when full.",
            "weak_en": "Use a dictionary with timestamps and loop through to find the oldest.",
            "strong_hi": "O(1) get और put के लिए हम Hash Map और Doubly Linked List का संयोजन (combination) इस्तेमाल करते हैं। Hash Map `key -> Node` पॉइंटर स्टोर करता है जिससे O(1) में खोज होती है। Doubly Linked List इस्तेमाल के क्रम को बनाए रखती है: सबसे नया हेड पर और सबसे पुराना टेल पर। किसी नोड को एक्सेस करने पर उसे O(1) में काटकर हेड पर ले आते हैं। कैपेसिटी भरने पर टेल वाले नोड को O(1) में डिलीट कर मैप से हटा देते हैं।",
            "average_hi": "Hash Map और Doubly Linked List मिलाकर बनता है। Hash map से O(1) सर्च और Linked list से O(1) इन्सर्शन/डिलीशन होता है।",
            "weak_hi": "डिक्शनरी में टाइमस्टैम्प रख कर सबसे पुराना डिलीट कर देंगे।"
        }
    },
    {
        "id": "dsa_hard_2",
        "role": "Software Developer Intern",
        "skill": "Data Structures & Algorithms",
        "difficulty": "HARD",
        "question_en": "Explain Dynamic Programming. What are the two essential characteristics a problem must possess to be solved with DP, and what is the difference between Top-Down Memoization and Bottom-Up Tabulation?",
        "question_hi": "Dynamic Programming (DP) को समझाइए। किसी समस्या को DP से हल करने के लिए उसमें कौन सी दो अनिवार्य विशेषताएं होनी चाहिए, और Top-Down Memoization व Bottom-Up Tabulation में क्या अंतर है?",
        "expected_concepts": ["Dynamic Programming", "Optimal Substructure", "Overlapping Subproblems", "Top-Down (Memoization)", "Bottom-Up (Tabulation)", "State transitions / recurrence relation"],
        "ideal_answer_points": [
            "Two essential characteristics: 1. Optimal Substructure (optimal solution to problem contains optimal solutions to subproblems), 2. Overlapping Subproblems (same subproblems are solved repeatedly).",
            "Top-Down (Memoization): uses recursion starting from main problem down to base cases, caching subproblem results in a table/map to avoid recomputation.",
            "Bottom-Up (Tabulation): iterative approach solving smallest base cases first and filling a table up to the desired target.",
            "Tabulation avoids call stack overhead, while memoization only computes subproblems that are actually needed."
        ],
        "rubric": {
            "excellent": "Clearly articulates Optimal Substructure and Overlapping Subproblems, compares Memoization vs Tabulation with trade-offs (stack depth vs unneeded state calculation), provides clear example.",
            "good": "Explains both characteristics and gives difference between recursion+caching and iterative table filling.",
            "average": "Knows DP is caching previous results but struggles with theoretical definitions.",
            "poor": "Confuses DP with divide and conquer or greedy algorithms."
        },
        "follow_ups": [
            "How does Dynamic Programming differ from the Greedy approach?",
            "What is state space reduction (e.g. reducing Fibonacci DP from O(N) space to O(1) space)?"
        ],
        "demo_answers": {
            "strong_en": "Dynamic Programming solves optimization problems by breaking them into subproblems. A problem requires two key properties: 1. Optimal Substructure (the global optimal solution is formed from optimal subproblem solutions) and 2. Overlapping Subproblems (the exact same subproblems recur during computation). Top-Down Memoization is recursive: it starts at the original problem and caches results in a lookup table. Bottom-Up Tabulation is iterative: it builds solutions from base cases upwards, avoiding call stack overhead.",
            "average_en": "Dynamic Programming avoids repeating work by storing subproblem answers. It requires overlapping subproblems and optimal substructure. Top-down uses recursion with a cache (memoization), while bottom-up uses loops to fill an array from base cases (tabulation).",
            "weak_en": "Dynamic programming is programming that changes dynamically.",
            "strong_hi": "Dynamic Programming जटिल समस्याओं को उप-समस्याओं (subproblems) में तोड़कर हल करती है। इसके लिए दो शर्तें जरूरी हैं: 1. Optimal Substructure (पूरी समस्या का हल उसकी उप-समस्याओं के सर्वोत्तम हल से बनता है) और 2. Overlapping Subproblems (वही उप-समस्याएं बार-बार आती हैं)। Top-Down Memoization में रिकर्शन के साथ रिज़ल्ट्स को कैश करते हैं। Bottom-Up Tabulation में लूप्स के जरिए बेस केस से शुरू करके टेबल भरते हैं, जिससे स्टैक ओवरफ्लो का खतरा नहीं रहता।",
            "average_hi": "DP में हम पुराने नतीजों को याद रखते हैं ताकि दोबारा गणना न करनी पड़े। Top-down में रिकर्शन + कैश होता है और Bottom-up में लूप से टेबल बनाते हैं।",
            "weak_hi": "कोड को डायनेमिकली रन करने को DP कहते हैं।"
        }
    },

    # ========================================================
    # 4. TECHNICAL UNDERSTANDING
    # ========================================================
    {
        "id": "tech_easy_1",
        "role": "Software Developer Intern",
        "skill": "Technical Understanding",
        "difficulty": "EASY",
        "question_en": "What is an API, and what is the difference between GET and POST HTTP methods?",
        "question_hi": "API क्या है, और GET व POST HTTP मेथड्स में क्या अंतर है?",
        "expected_concepts": ["API definition", "Client-Server model", "GET for retrieving data / idempotent / URL query params", "POST for creating data / request body / non-idempotent"],
        "ideal_answer_points": [
            "An API (Application Programming Interface) allows two software systems to communicate with standardized requests and responses.",
            "GET is used to retrieve data from the server; parameters are in the URL, requests should be idempotent and cached.",
            "POST is used to send data to the server to create a resource; data is carried in the request body, not cached by default, and non-idempotent."
        ],
        "rubric": {
            "excellent": "Defines API clearly, contrasts GET (data retrieval, query params, idempotency, caching) with POST (resource creation, body payload, non-idempotent).",
            "good": "Explains API and notes GET retrieves data while POST submits/creates data in request body.",
            "average": "Understands GET gets data and POST sends data, but misses details on payload, security, or idempotency.",
            "poor": "Cannot explain API or HTTP methods."
        },
        "follow_ups": [
            "What does idempotency mean in the context of HTTP methods?",
            "Why shouldn't passwords be sent using GET query parameters?"
        ],
        "demo_answers": {
            "strong_en": "An API is an Application Programming Interface that allows different software applications to communicate through defined contracts. In HTTP, GET is used to retrieve data from a server without modifying server state—it is idempotent, and parameters are passed in the URL. POST is used to submit data to create or process a resource—data is sent in the request body, it is non-idempotent, and typically causes state change on the server.",
            "average_en": "An API lets two systems talk to each other. GET is used to fetch data and puts parameters in the URL. POST sends data to the server inside the request body to create something new.",
            "weak_en": "API connects websites. GET gets things and POST posts things.",
            "strong_hi": "API (Application Programming Interface) दो सॉफ्टवेयर प्रणालियों के बीच संवाद का माध्यम है। GET मेथड सर्वर से डेटा प्राप्त करने (fetch) के लिए होता है, इसके पैरामीटर्स URL में दिखते हैं और यह सर्वर डेटा में बदलाव नहीं करता। POST मेथड सर्वर पर नया डेटा भेजने या रिसोर्स बनाने के लिए होता है, इसका डेटा Request Body में सुरक्षित रूप से जाता है।",
            "average_hi": "API दो ऍप्लिकेशन्स को जोड़ती है। GET से डेटा मंगाते हैं और POST से डेटा सर्वर पर भेजते हैं।",
            "weak_hi": "इंटरनेट पर डेटा भेजने का तरीका है।"
        }
    },
    {
        "id": "tech_easy_2",
        "role": "Software Developer Intern",
        "skill": "Technical Understanding",
        "difficulty": "EASY",
        "question_en": "What is Version Control, and why do software engineering teams use Git?",
        "question_hi": "Version Control क्या है, और सॉफ्टवेयर इंजीनियरिंग टीमें Git का उपयोग क्यों करती हैं?",
        "expected_concepts": ["Version Control System", "Tracking changes and history", "Branching and merging", "Collaboration without overwriting", "Rollback / revert capability"],
        "ideal_answer_points": [
            "Version control tracks changes to source code over time, maintaining a complete history of modifications.",
            "Git is a distributed version control system that lets multiple developers collaborate concurrently on different branches.",
            "It allows safe experimentation, merging code reviews, and reverting bugs to earlier commits."
        ],
        "rubric": {
            "excellent": "Explains distributed version control, commit history, branching workflows, conflict resolution, and rollback capabilities.",
            "good": "Explains tracking changes and collaboration using branches in Git.",
            "average": "Says Git is GitHub or just saves code backups.",
            "poor": "Cannot explain version control."
        },
        "follow_ups": [
            "What is the difference between Git and GitHub?",
            "What is a merge conflict and how do you resolve one?"
        ],
        "demo_answers": {
            "strong_en": "Version Control is a system that records changes to files over time so you can recall specific versions later. Teams use Git, a distributed version control system, because it enables seamless collaboration: developers work on independent branches without overwriting each other's work, track commit histories with blame and diffs, and easily roll back faulty changes while merging code through Pull Requests.",
            "average_en": "Version control keeps track of all code changes over time. Teams use Git so multiple people can work on the same codebase using branches without deleting each other's work.",
            "weak_en": "Git is GitHub where you store code online.",
            "strong_hi": "Version Control एक ऐसा सिस्टम है जो समय के साथ कोड में हुए सभी बदलावों का इतिहास (history) रखता है। टीमें Git का उपयोग इसलिए करती हैं क्योंकि यह एक Distributed VCS है जो कई डेवलपर्स को अलग-अलग Branches पर एक साथ बिना एक-दूसरे के कोड को मिटाए काम करने देता है। इससे कोड रिव्यु, बग आने पर पुराना कोड वापस लाना (rollback) आसान हो जाता है।",
            "average_hi": "Git कोड का बैकअप और हिस्ट्री रखता है ताकि टीम के लोग मिलकर काम कर सकें और पुराना कोड देख सकें।",
            "weak_hi": "Git ऑनलाइन कोड अपलोड करने के लिए होता है।"
        }
    },
    {
        "id": "tech_med_1",
        "role": "Software Developer Intern",
        "skill": "Technical Understanding",
        "difficulty": "MEDIUM",
        "question_en": "What is the difference between SQL (relational) and NoSQL (non-relational) databases? When would you choose one over the other?",
        "question_hi": "SQL (रिलेशनल) और NoSQL (नॉन-रिलेशनल) डेटाबेस में क्या अंतर है? आप एक के मुकाबले दूसरे को कब चुनेंगे?",
        "expected_concepts": ["Structured schema vs flexible schema", "ACID compliance vs BASE/eventual consistency", "Horizontal vs vertical scaling", "Relational joins vs document/key-value lookups", "Use cases"],
        "ideal_answer_points": [
            "SQL databases (PostgreSQL, MySQL) have structured tabular schemas with relations, foreign keys, and strict ACID guarantees.",
            "NoSQL databases (MongoDB, Redis, Cassandra) have flexible dynamic schemas (documents, key-value, column-family) designed for horizontal scaling.",
            "Choose SQL for structured data, complex joins, and transactional consistency (e.g. banking, e-commerce orders).",
            "Choose NoSQL for rapidly evolving unstructured data, high write throughput, and distributed horizontal scalability (e.g. real-time analytics, social feeds)."
        ],
        "rubric": {
            "excellent": "Clear comparison of schema rigidity vs flexibility, ACID transactions vs eventual consistency, vertical vs horizontal scaling, with grounded practical use cases.",
            "good": "Explains tables vs documents and gives valid reasons to choose each.",
            "average": "Knows SQL has tables and NoSQL does not, but cannot explain scaling or ACID properties.",
            "poor": "Cannot explain databases."
        },
        "follow_ups": [
            "What do the four letters in ACID stand for?",
            "Can a SQL database scale horizontally (e.g., sharding or CockroachDB)?"
        ],
        "demo_answers": {
            "strong_en": "SQL databases are relational with predefined schemas, structured tables, foreign keys, and strict ACID compliance, making them ideal for transactional integrity like banking and e-commerce orders. They scale primarily vertically. NoSQL databases offer schema-less or flexible data models (documents, key-value, graphs) and scale horizontally across distributed clusters. You choose SQL when relationships and consistency are paramount, and NoSQL for high-velocity unstructured data and rapid horizontal scale.",
            "average_en": "SQL has tables with rows and columns, fixed schema, and supports joins. NoSQL stores JSON-like documents with flexible schemas. SQL is best when data is structured and needs transactions, while NoSQL is good for fast scaling and changing schemas.",
            "weak_en": "SQL is old and NoSQL is modern without SQL queries.",
            "strong_hi": "SQL डेटाबेस रिलेशनल होते हैं, जिनमें फिक्स्ड स्कीमा, टेबल्स, और सख्त ACID प्रॉपर्टीज होती हैं—यह बैंकिंग और जटिल रिलेशंस वाले सिस्टम के लिए सबसे अच्छे हैं। NoSQL डेटाबेस (जैसे MongoDB) फ्लेक्सिबल स्कीमा (JSON डॉक्यूमेंट्स) का उपयोग करते हैं और आसानी से Horizontally scale हो जाते हैं। जब डेटा का ढांचा तय हो और ट्रांजैक्शन्स ज़रूरी हों तो SQL चुनते हैं; जब डेटा अनस्ट्रक्चर्ड हो और हाई-स्पीड राइट्स चाहिए हों तो NoSQL चुनते हैं।",
            "average_hi": "SQL में टेबल्स और फिक्स्ड स्कीमा होता है, NoSQL में JSON डॉक्यूमेंट्स होते हैं। SQL ट्रांज़ैक्शन के लिए और NoSQL बड़े डेटा को स्केल करने के लिए सही है।",
            "weak_hi": "SQL में क्वेरी लिखनी पड़ती है NoSQL में नहीं।"
        }
    },
    {
        "id": "tech_med_2",
        "role": "Software Developer Intern",
        "skill": "Technical Understanding",
        "difficulty": "MEDIUM",
        "question_en": "What happens under the hood when a user types a URL (like https://example.com) into a browser and presses Enter?",
        "question_hi": "जब कोई यूज़र ब्राउज़र में URL (जैसे https://example.com) टाइप करके Enter दबाता है, तो बैकग्राउंड में क्या-क्या होता है?",
        "expected_concepts": ["DNS resolution", "TCP three-way handshake", "TLS/SSL handshake for HTTPS", "HTTP request and response", "Browser rendering (DOM, CSSOM, Render tree)"],
        "ideal_answer_points": [
            "DNS lookup: Browser checks local cache, then queries DNS resolvers to translate hostname into an IP address.",
            "Connection establishment: TCP 3-way handshake (SYN, SYN-ACK, ACK) and TLS handshake for HTTPS encryption.",
            "HTTP request: Browser sends GET request with headers to the server.",
            "Server processes request and returns HTTP status code and HTML response.",
            "Browser rendering: Parses HTML into DOM, CSS into CSSOM, builds Render Tree, layout, and paints pixels."
        ],
        "rubric": {
            "excellent": "Covers DNS lookup stages, TCP handshake, TLS encryption negotiation, HTTP request/response cycle, and browser DOM/CSSOM parsing and painting.",
            "good": "Mentions DNS, IP connection, HTTP request, and rendering the page.",
            "average": "Knows it talks to a server and gets a webpage, but misses network layers.",
            "poor": "Vague or incorrect explanation of web architecture."
        },
        "follow_ups": [
            "How does TLS certificate validation ensure you are connecting to the legitimate server?",
            "What is the difference between parsing HTML and executing JavaScript scripts in the critical rendering path?"
        ],
        "demo_answers": {
            "strong_en": "First, the browser resolves the domain to an IP address via DNS cache or recursive DNS queries. Next, it establishes a TCP connection via the 3-way handshake (SYN, SYN-ACK, ACK), followed by the TLS handshake to establish HTTPS encryption. The browser sends an HTTP GET request; the server processes it and returns HTML. Finally, the browser parses the HTML into a DOM tree, CSS into CSSOM, combines them into a Render Tree, performs layout calculations, and paints the pixels on screen.",
            "average_en": "The browser checks DNS to find the server's IP address. Then it makes a TCP and SSL connection to the server. The browser sends an HTTP GET request, the server sends back HTML and CSS, and the browser displays the page.",
            "weak_en": "The browser sends a signal over the internet to the website and opens it.",
            "strong_hi": "सबसे पहले DNS रिज़ॉल्यूशन होता है जहाँ डोमेन का IP एड्रेस ढूंढा जाता है। इसके बाद सर्वर के साथ TCP 3-way handshake और HTTPS के लिए TLS Handshake होता है। फिर ब्राउज़र HTTP GET रिक्वेस्ट भेजता है। सर्वर HTML/CSS रिस्पॉन्स वापस करता है। अंत में ब्राउज़र HTML से DOM और CSS से CSSOM बनाकर Render Tree तैयार करता है और स्क्रीन पर पेज पेंट करता है।",
            "average_hi": "DNS से IP मिलता है, फिर सर्वर से कनेक्शन बनाकर HTTP रिक्वेस्ट जाती है। सर्वर से HTML मिलता है और ब्राउज़र उसे स्क्रीन पर दिखा देता है।",
            "weak_hi": "इंटरनेट से वेबसाइट खुल जाती है।"
        }
    },
    {
        "id": "tech_hard_1",
        "role": "Software Developer Intern",
        "skill": "Technical Understanding",
        "difficulty": "HARD",
        "question_en": "What is the difference between Monolithic and Microservices architecture? What challenges arise in distributed systems regarding data consistency and network failures?",
        "question_hi": "Monolithic और Microservices आर्किटेक्चर में क्या अंतर है? Distributed Systems में डेटा कंसिस्टेंसी और नेटवर्क फेलियर्स को लेकर क्या चुनौतियाँ आती हैं?",
        "expected_concepts": ["Monolith vs Microservices", "Loose coupling / independent deployment", "CAP theorem", "Network latency / partition tolerance", "Eventual consistency / Saga pattern", "Distributed tracing"],
        "ideal_answer_points": [
            "Monolith packages all business logic and database access in a single unified codebase/deployment unit.",
            "Microservices decomposes functionality into independent, loosely coupled services communicating via APIs/message brokers.",
            "Challenges: network latency, partial failures, distributed transactions (CAP theorem), debugging across service boundaries.",
            "Solutions: Saga pattern for distributed transactions, circuit breakers (Resilience4j), event-driven messaging (Kafka), distributed tracing."
        ],
        "rubric": {
            "excellent": "Contrasts architectural trade-offs, discusses CAP theorem, distributed transactions (two-phase commit vs Sagas), circuit breakers, and observability.",
            "good": "Explains single app vs multiple services and discusses network failures and consistency.",
            "average": "States monolith is one app and microservices is many apps, without architectural depth.",
            "poor": "Fails to explain system architecture."
        },
        "follow_ups": [
            "What is the Saga pattern and how does compensation logic work?",
            "Why is the Circuit Breaker pattern crucial in microservices?"
        ],
        "demo_answers": {
            "strong_en": "A monolith deploys the entire application and shared database as a single unit, which is simple to develop and debug initially but becomes a bottleneck as teams scale. Microservices separates the system into independent services bounded by business domains, each with its own database, enabling independent scaling and deployments. However, microservices introduce distributed system challenges: network partitions, cascading failures, and complex data consistency governed by the CAP theorem. To solve this, teams use the Saga pattern with compensating transactions, circuit breakers, and event-driven architecture.",
            "average_en": "A monolith is one big codebase where everything runs together. Microservices breaks the application into smaller independent services that talk over HTTP or message queues. The challenge with microservices is that network calls can fail and keeping data consistent across multiple databases is hard.",
            "weak_en": "Monolith is old code and microservices is modern cloud code.",
            "strong_hi": "Monolith में पूरा ऍप्लिकेशन और डेटाबेस एक ही यूनिट के रूप में डिप्लॉय होता है, जो शुरुआत में आसान होता है। Microservices में बिज़नेस फ़ंक्शन्स को अलग-अलग स्वतंत्र सेवाओं में बाँट दिया जाता है, जिनका अपना डेटाबेस होता है। इसमें चुनौतियाँ यह हैं कि नेटवर्क कॉल्स कभी भी फेल हो सकती हैं और अलग-अलग डेटाबेसों में कंसिस्टेंसी बनाए रखना कठिन होता है। इसके लिए Saga पैटर्न, Circuit Breaker और Kafka जैसे मैसेज ब्रोकर्स का सहारा लिया जाता है।",
            "average_hi": "Monolith एक बड़ा प्रोजेक्ट होता है, Microservices में छोटे-छोटे सर्विस अलग चलते हैं। इसमें नेटवर्क एरर और कई डेटाबेस में डेटा मिलाने की दिक्कत आती है।",
            "weak_hi": "मोनोलिथ छोटा होता है और माइक्रोसर्विस बड़ा होता है।"
        }
    },
    {
        "id": "tech_hard_2",
        "role": "Software Developer Intern",
        "skill": "Technical Understanding",
        "difficulty": "HARD",
        "question_en": "Explain how authentication and authorization work using JSON Web Tokens (JWT) and OAuth 2.0. What are the security risks like token theft and how are they mitigated?",
        "question_hi": "JSON Web Tokens (JWT) और OAuth 2.0 का उपयोग करके Authentication और Authorization कैसे काम करते हैं? टोकन चोरी (token theft) जैसे सुरक्षा जोखिम क्या हैं और इनसे कैसे बचा जाता है?",
        "expected_concepts": ["Authentication vs Authorization", "JWT structure (Header, Payload, Signature)", "Stateless authentication", "OAuth 2.0 flow (Access token, Refresh token)", "XSS and CSRF risks", "HttpOnly Secure cookies"],
        "ideal_answer_points": [
            "Authentication verifies who you are; Authorization determines what you have permission to do.",
            "JWT consists of Header, Payload, and cryptographic Signature, allowing stateless server verification without database sessions.",
            "OAuth 2.0 is an authorization framework using client IDs, redirect URIs, and scopes to issue short-lived access tokens and refresh tokens.",
            "Security risks: XSS can steal tokens from localStorage (mitigated by storing in HttpOnly, Secure, SameSite cookies). Token leakage is mitigated by short expiration times and refresh token rotation."
        ],
        "rubric": {
            "excellent": "Clearly distinguishes AuthN vs AuthZ, breaks down JWT 3-part structure, explains OAuth token flow, details storage vulnerabilities (localStorage vs HttpOnly cookies) and token rotation.",
            "good": "Explains JWT structure, headers/payload/signature, and mentions access token expiry.",
            "average": "Knows JWT is a token for login, but confused about authorization vs authentication.",
            "poor": "Cannot explain tokens or security."
        },
        "follow_ups": [
            "Why is storing JWTs in localStorage vulnerable to Cross-Site Scripting (XSS)?",
            "How does refresh token rotation help detect token theft?"
        ],
        "demo_answers": {
            "strong_en": "Authentication verifies identity, while Authorization determines permissions. A JWT contains Header, Payload, and a Signature verified with a secret or public key, allowing stateless verification without server session state. In OAuth 2.0, an authorization server issues short-lived access tokens and longer-lived refresh tokens. The main risk is token theft via XSS if stored in localStorage. The best mitigation is storing tokens in HttpOnly, Secure, SameSite cookies, keeping access token lifespans short (15 mins), and implementing refresh token rotation with family revocation on reuse.",
            "average_en": "Authentication is who you are and authorization is what permissions you have. JWT has three parts: header, payload, and signature. OAuth 2 lets users authorize apps without sharing passwords. To prevent token theft, store tokens in HttpOnly cookies instead of localStorage and use short-lived tokens with refresh tokens.",
            "weak_en": "JWT is an encrypted password that users keep in their browser.",
            "strong_hi": "Authentication यूज़र की पहचान सत्यापित करता है, जबकि Authorization यह तय करता है कि उसे क्या अधिकार हैं। JWT में तीन भाग होते हैं: Header, Payload और Signature, जिससे सर्वर बिना सेशन स्टोर किए टोकन की प्रामाणिकता जांच सकता है। OAuth 2.0 में एक्सेस टोकन और रिफ्रेश टोकन जारी होते हैं। टोकन चोरी (XSS) से बचने के लिए टोकन को localStorage की जगह HttpOnly, Secure कुकीज़ में रखना चाहिए और एक्सेस टोकन की एक्सपायरी छोटी रखनी चाहिए।",
            "average_hi": "JWT में तीन हिस्से होते हैं और यह लॉगिन के काम आता है। टोकन चोरी रोकने के लिए HttpOnly कुकीज़ और रिफ्रेश टोकन का यूज़ करते हैं।",
            "weak_hi": "पासवर्ड की जगह टोकन यूज़ करते हैं।"
        }
    },

    # ========================================================
    # 5. COMMUNICATION
    # ========================================================
    {
        "id": "comm_easy_1",
        "role": "Software Developer Intern",
        "skill": "Communication",
        "difficulty": "EASY",
        "question_en": "How would you explain a technical bug to a non-technical stakeholder or client so they understand its impact without getting lost in technical jargon?",
        "question_hi": "आप किसी गैर-तकनीकी स्टेकहोल्डर या क्लाइंट को कोई टेक्निकल बग कैसे समझाएंगे ताकि वे बिना तकनीकी शब्दों में उलझे इसके प्रभाव को समझ सकें?",
        "expected_concepts": ["user impact first", "real-world analogy", "avoiding jargon", "clear timeline and next steps", "listening to concerns"],
        "ideal_answer_points": [
            "Focus immediately on the business and user impact rather than internal code errors.",
            "Use clear, relatable real-world analogies rather than acronyms or stack traces.",
            "Provide transparent status: what happened, what we are doing to fix it, and estimated resolution time.",
            "Keep communication proactive and offer a temporary workaround if available."
        ],
        "rubric": {
            "excellent": "Prioritizes business/user impact, uses an accessible analogy, outlines a structured update (Impact -> Action -> Timeline), avoids technical jargon, demonstrates empathy.",
            "good": "Explains the problem in simple terms focusing on what the user sees and giving a fix timeline.",
            "average": "Recognizes jargon should be avoided but still uses semi-technical terms.",
            "poor": "Uses heavy jargon and dismisses stakeholder concerns."
        },
        "follow_ups": [
            "What if the stakeholder is angry about the delay—how do you handle the conversation?",
            "Can you give an example of an analogy you've used before?"
        ],
        "demo_answers": {
            "strong_en": "I would structure my explanation around three things: User Impact, Action Plan, and Timeline. I avoid jargon like 'database deadlocks' and instead say: 'Right now, customers cannot complete their checkout payments because our payment pipeline is stalled. Our team has identified the cause, applied a patch, and we expect payments to be fully restored within 45 minutes.' This respects their time, gives clarity, and reassures them with concrete actions.",
            "average_en": "I would explain what the user experiences instead of the code error. I'd avoid big tech words and give them an analogy, then tell them when it will be fixed and what we are doing right now.",
            "weak_en": "Tell them the server had a null pointer exception.",
            "strong_hi": "मैं तकनीकी शब्दों के बजाय बिजनेस और यूज़र पर पड़ने वाले असर पर ध्यान दूंगा। उदाहरण के लिए 'डेटाबेस डेडलॉक' कहने के बजाय मैं कहूँगा: 'इस समय ग्राहक चेकआउट पेज पर पेमेंट नहीं कर पा रहे हैं। हमारी टीम ने समस्या की पहचान कर ली है और अगले 45 मिनट में इसे ठीक कर दिया जाएगा।' मैं उन्हें स्पष्ट टाइमलाइन और समाधान की जानकारी दूँगा ताकि उन्हें भरोसा रहे।",
            "average_hi": "मैं आसान शब्दों में बताऊँगा कि यूज़र को क्या दिक्कत आ रही है और हम कब तक इसे ठीक कर देंगे।",
            "weak_hi": "उन्हें बोल देंगे कि सर्वर क्रैश हो गया है।"
        }
    },
    {
        "id": "comm_easy_2",
        "role": "Software Developer Intern",
        "skill": "Communication",
        "difficulty": "EASY",
        "question_en": "When asking a senior engineer for help after being stuck on a task, how do you formulate your question to respect their time?",
        "question_hi": "किसी काम में अटक जाने के बाद सीनियर इंजीनियर से मदद मांगते समय, आप अपने सवाल को कैसे तैयार करेंगे ताकि उनके समय का सम्मान हो सके?",
        "expected_concepts": ["showing prior effort", "clear problem statement", "sharing what was already tried", "minimal reproducible context", "specific question"],
        "ideal_answer_points": [
            "Summarize the goal: what you are trying to achieve.",
            "Describe what actually happened: expected vs actual behavior with error logs.",
            "Detail what you have already tried and researched (documentation, debugging steps).",
            "Ask a specific, targeted question rather than a vague 'it doesn't work'."
        ],
        "rubric": {
            "excellent": "Follows the 15-minute / structured rule: State Goal -> Show Error -> Detail What Was Tried -> Targeted Question, showing self-reliance and respect for time.",
            "good": "Explains the issue, what they tried, and asks a specific question.",
            "average": "Says they will explain the error and ask for help, but doesn't mention showing their own prior attempts.",
            "poor": "Expects the senior to solve it immediately without providing context."
        },
        "follow_ups": [
            "How long do you typically struggle on a problem before asking for help?",
            "What documentation do you provide when asking the question (e.g., error logs, reproducible steps)?"
        ],
        "demo_answers": {
            "strong_en": "I follow a four-part structure: 1. Goal: What I am attempting to accomplish. 2. Observed issue: The specific error message and behavior. 3. What I've tried: The 2-3 approaches or documentation I researched. 4. Targeted question: 'I suspect the issue is in the authentication middleware token parsing—could you point me in the right direction?' This shows I investigated independently and saves them from repeating steps I already did.",
            "average_en": "I would explain what I'm trying to do, what error I am getting, and list everything I already tried so they know what didn't work. Then I ask a specific question so they can answer quickly.",
            "weak_en": "Send a screenshot of the error and ask them to fix it.",
            "strong_hi": "मैं चार चरणों में अपनी बात रखूँगा: 1. लक्ष्य: मैं क्या करना चाह रहा हूँ। 2. समस्या: क्या एरर आ रही है। 3. मैंने क्या प्रयास किए: मैंने कौन से समाधान और दस्तावेज़ देखे। 4. सटीक सवाल: 'मुझे लगता है कि टोकन वेरिफिकेशन में दिक्कत है, क्या आप मुझे सही दिशा बता सकते हैं?' इससे उनका समय बचेगा और उन्हें पता रहेगा कि मैंने खुद भी रिसर्च की है।",
            "average_hi": "पहले बताऊँगा कि क्या एरर है और मैंने क्या-क्या ट्राय किया है, फिर उनसे पूछूँगा कि आगे क्या करना चाहिए।",
            "weak_hi": "स्क्रीनशॉट भेज कर बोलूँगा कि कोड नहीं चल रहा।"
        }
    },
    {
        "id": "comm_med_1",
        "role": "Software Developer Intern",
        "skill": "Communication",
        "difficulty": "MEDIUM",
        "question_en": "During a Code Review, a teammate leaves critical feedback suggesting you rewrite a major part of your PR. How do you respond and collaborate professionally?",
        "question_hi": "Code Review के दौरान, एक साथी डेवलपर आपकी PR के एक बड़े हिस्से को दोबारा लिखने का सुझाव देता है। आप पेशेवर तरीके से कैसे प्रतिक्रिया देंगे और सहयोग करेंगे?",
        "expected_concepts": ["separating ego from code", "assuming positive intent", "seeking clarification / rationale", "proposing a call if async is slow", "focusing on code quality"],
        "ideal_answer_points": [
            "Separate personal feelings from the code; assume positive intent aimed at code quality and maintainability.",
            "Acknowledge the feedback constructively and seek clarification on the architectural reasoning.",
            "If the trade-offs are nuanced, schedule a quick 5-10 minute sync to discuss approaches rather than long comment threads.",
            "Reach consensus based on team standards, testing, and performance benefits."
        ],
        "rubric": {
            "excellent": "Demonstrates emotional maturity, curiosity to learn the underlying rationale, proposes quick sync if comments drag on, evaluates technical trade-offs collaboratively.",
            "good": "Remains calm, thanks the reviewer, asks for reasons, and collaborates on the best fix.",
            "average": "Says they will just change the code without understanding why or defending unnecessarily.",
            "poor": "Reacts defensively or takes the critique personally."
        },
        "follow_ups": [
            "What if you genuinely believe your original approach is better—how do you present your counter-argument?",
            "How do you write constructive code review comments when reviewing others' work?"
        ],
        "demo_answers": {
            "strong_en": "I separate my identity from my code and assume positive intent. First, I thank the teammate for their thorough review. I read their suggestion carefully to understand the architectural benefits. If their points are valid, I happily adopt them. If I have reservations or want to discuss trade-offs, I politely share my rationale with data or suggest a quick 10-minute sync to avoid a lengthy comment chain, aligning on the best solution for the team.",
            "average_en": "I wouldn't take it personally. I would thank them and ask them to explain why the rewrite is better. If it makes sense I will rewrite it, and if I disagree we can discuss the pros and cons on a quick call.",
            "weak_en": "Accept everything they say and redo it, or close the PR.",
            "strong_hi": "मैं कोड और खुद को अलग रखता हूँ और सकारात्मक सोच के साथ देखता हूँ कि यह सुझाव प्रोजेक्ट की गुणवत्ता के लिए है। मैं उन्हें विस्तृत रिव्यु के लिए धन्यवाद दूँगा। यदि उनका सुझाव आर्किटेक्चर को बेहतर बनाता है तो मैं उसे खुशी से लागू करूँगा। यदि मुझे कोई शंका है, तो मैं लंबी कमेंट चैट के बजाय 10 मिनट की कॉल पर बात करने का सुझाव दूँगा ताकि टीम के हित में सही निर्णय लिया जा सके।",
            "average_hi": "मैं इसे व्यक्तिगत नहीं लूँगा। उनसे पूछूँगा कि ऐसा क्यों करना बेहतर रहेगा, और अगर सही लगा तो कोड बदल दूँगा।",
            "weak_hi": "जैसा उन्होंने बोला वैसा कर देंगे बिना पूछे।"
        }
    },
    {
        "id": "comm_med_2",
        "role": "Software Developer Intern",
        "skill": "Communication",
        "difficulty": "MEDIUM",
        "question_en": "How do you communicate a deadline risk to your engineering manager when you realize a feature will not be completed on time?",
        "question_hi": "जब आपको एहसास होता है कि कोई फ़ीचर तय समय पर पूरा नहीं हो पाएगा, तो आप अपने इंजीनियरिंग मैनेजर को डेडलाइन के जोखिम के बारे में कैसे सूचित करेंगे?",
        "expected_concepts": ["early notification", "transparency over hiding", "root cause explanation", "actionable options (scope cut vs time extension)", "impact analysis"],
        "ideal_answer_points": [
            "Notify the manager as early as possible—never wait until the deadline day.",
            "Explain the root cause clearly (unexpected complexity, external dependency, unforeseen edge cases).",
            "Present concrete options: e.g. Option A (ship core MVP on time by cutting non-essential scope), Option B (extend deadline by 2 days).",
            "Recommend the best option and ask for guidance."
        ],
        "rubric": {
            "excellent": "Proactive early notification, clear root cause breakdown, provides concrete trade-off options (descoping vs extension), presents recommended path, demonstrates accountability.",
            "good": "Communicates early, explains the delay reason, and suggests a new completion date or reduced scope.",
            "average": "Says they will apologize and work overtime without discussing trade-offs.",
            "poor": "Waits until the deadline has passed to inform the manager."
        },
        "follow_ups": [
            "Why is descoping a feature often preferable to pushing back a release date?",
            "How do you prevent deadline estimation inaccuracies in future sprints?"
        ],
        "demo_answers": {
            "strong_en": "I communicate proactively as soon as I spot the risk, never waiting until deadline day. I schedule a brief chat with my manager stating: 'We ran into unexpected complexity with payment webhook edge cases. At current velocity, we will miss Friday's release by two days.' I then offer solutions: 'Option 1 is descoping the retry dashboard and shipping core payments on Friday. Option 2 is keeping full scope and shipping on Tuesday.' I provide my recommendation and seek their strategic input.",
            "average_en": "I would tell my manager right away when I know there's a delay, not at the last minute. I'll explain what caused the roadblock and offer options like cutting smaller features or extending the deadline by a day or two.",
            "weak_en": "Work all night without telling anyone and hope it finishes.",
            "strong_hi": "मैं डेडलाइन के दिन का इंतजार किए बिना जोखिम का पता चलते ही तुरंत मैनेजर को सूचित करूँगा। मैं समस्या की वजह साफ़ बताऊँगा और साथ में विकल्प रखूँगा: 'विकल्प 1: गैर-ज़रूरी फ़ीचर्स को हटाकर मुख्य MVP समय पर रिलीज़ करना। विकल्प 2: पूरी कार्यक्षमता के साथ 2 दिन का अतिरिक्त समय लेना।' मैं अपनी सिफारिश के साथ मैनेजर से मार्गदर्शन माँगूँगा।",
            "average_hi": "जैसे ही पता चले कि लेट होगा, तुरंत मैनेजर को बताएँगे और कारण समझाकर नया टाइम देंगे या कुछ फ़ीचर बाद के लिए छोड़ेंगे।",
            "weak_hi": "रात भर काम करेंगे और चुप रहेंगे।"
        }
    },
    {
        "id": "comm_hard_1",
        "role": "Software Developer Intern",
        "skill": "Communication",
        "difficulty": "HARD",
        "question_en": "How would you lead an Architecture Decision Record (ADR) discussion when your team is deeply divided between two conflicting technical approaches (e.g. REST vs GraphQL)?",
        "question_hi": "जब आपकी टीम दो परस्पर विरोधी तकनीकी दृष्टिकोणों (जैसे REST बनाम GraphQL) के बीच बँटी हो, तो आप Architecture Decision Record (ADR) चर्चा का नेतृत्व कैसे करेंगे?",
        "expected_concepts": ["objective evaluation framework", "decision matrix / trade-offs", "aligning on business requirements", "documenting ADR", "disagree and commit"],
        "ideal_answer_points": [
            "Ground the debate in project requirements, client needs, team expertise, and maintenance costs rather than personal preference.",
            "Create a structured comparison matrix evaluating latency, caching, payload size, tooling, and developer velocity.",
            "Facilitate a timeboxed discussion where both sides present use cases and trade-offs.",
            "Document the consensus in an ADR (Context, Decision, Consequences), and encourage the team to 'disagree and commit'."
        ],
        "rubric": {
            "excellent": "Establishes objective criteria matrix, frames discussion around business/technical constraints, uses ADR structure (Context, Decision, Consequences), drives 'disagree and commit'.",
            "good": "Lists pros and cons of both, facilitates structured discussion, and writes down the decision in an ADR.",
            "average": "Suggests voting without technical trade-off matrix.",
            "poor": "Picks one side arbitrarily and ignores the other team members."
        },
        "follow_ups": [
            "What do you do if a teammate refuses to commit to the chosen decision?",
            "How do you test assumptions with a quick Spike or Proof of Concept (POC) before finalizing an ADR?"
        ],
        "demo_answers": {
            "strong_en": "I de-escalate personal preferences by anchoring the conversation in objective business requirements and technical constraints. I prepare a structured decision matrix comparing REST and GraphQL on caching, payload over-fetching, team learning curve, and timeline. I run a time-boxed ADR session where each side shares their trade-offs. If necessary, we run a 2-day proof of concept. Once decided, I document the ADR with Context, Decision, and Consequences, ensuring the team aligns under 'disagree and commit'.",
            "average_en": "I would make a comparison table listing pros, cons, costs, and risks of both REST and GraphQL based on our project needs. We'd have a meeting to discuss facts instead of opinions, write down an Architecture Decision Record, and agree to support the final choice as a unified team.",
            "weak_en": "Take a vote and majority wins.",
            "strong_hi": "मैं व्यक्तिगत पसंद के बजाय प्रोजेक्ट की वास्तविक ज़रूरतों और सीमाओं पर चर्चा को केंद्रित करूँगा। मैं एक Decision Matrix बनाऊँगा जिसमें Caching, Latency, टीम की दक्षता और समयसीमा के आधार पर दोनों की तुलना होगी। हम समयबद्ध ADR मीटिंग करेंगे। ज़रूरत पड़ने पर 2 दिन का छोटा POC (Proof of Concept) करेंगे। अंत में ADR डॉक्यूमेंट तैयार करेंगे जिसमें Context, Decision और Consequences दर्ज होंगे, और 'Disagree and Commit' सिद्धांत के साथ आगे बढ़ेंगे।",
            "average_hi": "दोनों तकनीकों के फायदे-नुकसान की लिस्ट बनाकर टीम के साथ मीटिंग करेंगे। प्रोजेक्ट की ज़रूरत देखकर ADR लिखेंगे और फैसला लेंगे।",
            "weak_hi": "वोटिंग करा लेंगे जिसके ज्यादा वोट वो जीत गया।"
        }
    },
    {
        "id": "comm_hard_2",
        "role": "Software Developer Intern",
        "skill": "Communication",
        "difficulty": "HARD",
        "question_en": "Following a major production outage that impacted thousands of users, how would you write and lead a blameless post-mortem retrospective with the team?",
        "question_hi": "हजारों यूज़र्स को प्रभावित करने वाले एक बड़े प्रोडक्शन आउटेज के बाद, आप टीम के साथ Blameless Post-Mortem (दोषमुक्त समीक्षा) कैसे लिखेंगे और उसका नेतृत्व कैसे करेंगे?",
        "expected_concepts": ["blameless culture", "timeline of events", "root cause analysis (5 Whys)", "actionable prevention items with owners", "systemic failure over human blame"],
        "ideal_answer_points": [
            "Establish a blameless mindset: assume people made the best decisions with the information they had; blame the process, tooling, or safety guards, not individuals.",
            "Build an accurate chronological timeline of the incident: detection, communication, mitigation, and resolution.",
            "Conduct root cause analysis using methods like the '5 Whys' to uncover systemic deficiencies.",
            "Generate SMART preventative action items (automated tests, canary deploys, alerts) with assigned owners and deadlines."
        ],
        "rubric": {
            "excellent": "Articulates blameless philosophy, builds precise incident timeline, uses 5 Whys to identify systemic/safeguard gaps, assigns actionable preventative tasks with owners, publishes learning report.",
            "good": "Focuses on timeline, finding root cause without blaming anyone, and setting up fixes so it never happens again.",
            "average": "Talks about finding the bug and fixing it, but lacks depth on systemic prevention or psychological safety.",
            "poor": "Focuses on finding who made the mistake and punishing them."
        },
        "follow_ups": [
            "Why is psychological safety essential for incident reporting and system reliability?",
            "What is the difference between immediate mitigation and long-term remediation?"
        ],
        "demo_answers": {
            "strong_en": "A blameless post-mortem focuses on systemic vulnerabilities rather than human error. I start by establishing psychological safety: the system allowed a single mistake to cause an outage, meaning our safety nets failed. I lead the team through a detailed timeline: T0 detection, alerts fired, mitigation taken, and final recovery. We use the '5 Whys' to drill down to root causes like missing canary tests or inadequate database connection pool limits. Finally, we assign concrete action items with owners and deadlines to prevent recurrence.",
            "average_en": "I would make sure no one is blamed because people don't cause outages intentionally—processes and safeguards fail. We document the exact timeline of what happened, find the root cause using the 5 Whys, and create action items like adding tests and alerts with owners so it cannot happen again.",
            "weak_en": "Find out who pushed the broken code and ask them to fix it and be more careful.",
            "strong_hi": "Blameless Post-Mortem का मूल सिद्धांत यह है कि गलती इंसान की नहीं बल्कि सिस्टम और सुरक्षा घेरे (safety nets) की नाकामी है। मैं एक सटीक टाइमलाइन बनाऊँगा: आउटेज कब शुरू हुआ, कब पता चला, और कैसे रिकवर हुआ। '5 Whys' तकनीक से हम जड़ तक पहुँचेंगे कि ऑटोमेटेड टेस्ट्स या अलर्ट्स ने इसे पहले क्यों नहीं पकड़ा। अंत में हम ठोस एक्शन आइटम्स तय करेंगे (जैसे कैनरी डिप्लॉयमेंट, बेहतर मॉनिटरिंग) और ज़िम्मेदार डेवलपर्स को समयसीमा के साथ सौंपेंगे।",
            "average_hi": "बिना किसी पर दोष लगाए पूरी टाइमलाइन लिखेंगे, 5 Whys से असली वजह समझेंगे, और सिस्टम में नए टेस्ट या अलर्ट्स लगाने के टास्क तय करेंगे।",
            "weak_hi": "जिसने गलत कोड पुश किया उसे समझाएंगे।"
        }
    }
]

def get_questions_by_role(role="Software Developer Intern"):
    return [q for q in QUESTION_BANK if q.get("role") == role]

def get_questions_by_skill_and_difficulty(skill, difficulty, role="Software Developer Intern"):
    return [
        q for q in QUESTION_BANK
        if q.get("role") == role and q.get("skill") == skill and q.get("difficulty") == difficulty
    ]

DYNAMIC_QUESTIONS_REGISTRY = {}

def register_dynamic_question(q_obj):
    """Registers a dynamically generated interview question into the in-memory registry."""
    if q_obj and "id" in q_obj:
        DYNAMIC_QUESTIONS_REGISTRY[q_obj["id"]] = q_obj

def get_question_by_id(question_id):
    for q in QUESTION_BANK:
        if q.get("id") == question_id:
            return q
    if question_id in DYNAMIC_QUESTIONS_REGISTRY:
        return DYNAMIC_QUESTIONS_REGISTRY[question_id]
    return None
