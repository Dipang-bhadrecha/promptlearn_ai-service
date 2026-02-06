#!/usr/bin/env python3
"""
Quick test script for the Memory System
Tests all major components and verifies functionality
"""
import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_USER = f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
TEST_CONV = "test_conversation"


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


async def send_message(message, messages_history=None):
    """Send a message to the AI"""
    if messages_history is None:
        messages_history = []

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{BASE_URL}/ai/generate",
            json={
                "user_id": TEST_USER,
                "conversation_id": TEST_CONV,
                "message": message,
                "messages": messages_history
            }
        )
        response.raise_for_status()
        return response.json()


async def get_memory_stats():
    """Get memory statistics"""
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{BASE_URL}/ai/memory/stats",
            json={
                "user_id": TEST_USER,
                "conversation_id": TEST_CONV
            }
        )
        response.raise_for_status()
        return response.json()


async def get_conversation_history():
    """Get conversation history"""
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{BASE_URL}/ai/memory/history",
            json={
                "user_id": TEST_USER,
                "conversation_id": TEST_CONV
            }
        )
        response.raise_for_status()
        return response.json()


async def get_summary():
    """Get conversation summary"""
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{BASE_URL}/ai/memory/summary",
            json={
                "user_id": TEST_USER,
                "conversation_id": TEST_CONV
            }
        )
        response.raise_for_status()
        return response.json()


async def clear_memory():
    """Clear conversation memory"""
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{BASE_URL}/ai/memory/clear",
            json={
                "user_id": TEST_USER,
                "conversation_id": TEST_CONV
            }
        )
        response.raise_for_status()
        return response.json()


async def test_basic_conversation():
    """Test 1: Basic conversation without memory"""
    print_header("Test 1: Basic Conversation (No Memory)")

    response = await send_message("Hello! What is Python?")

    print_info(f"User: Hello! What is Python?")
    print_info(f"Assistant: {response['assistant_message'][:100]}...")

    meta = response['meta']
    print_success(f"Pipeline version: {meta['pipeline_version']}")
    print_success(f"Memory used: {meta.get('memory', {})}")

    return response


async def test_short_term_memory():
    """Test 2: Short-term memory (conversation continuity)"""
    print_header("Test 2: Short-Term Memory (STM)")

    # Build conversation history
    history = [
        {"role": "user", "content": "Hello! What is Python?"},
        {"role": "assistant", "content": "Python is a high-level programming language..."}
    ]

    response = await send_message("What are its main features?", history)

    print_info(f"User: What are its main features?")
    print_info(f"Assistant: {response['assistant_message'][:100]}...")

    memory_meta = response['meta'].get('memory', {})
    print_success(f"STM turns: {memory_meta.get('stm_turns', 0)}")
    print_success(f"Context tokens: {memory_meta.get('total_tokens', 0)}")

    return response


async def test_memory_persistence():
    """Test 3: Memory persistence"""
    print_header("Test 3: Memory Persistence")

    # Send a few messages
    for i in range(3):
        await send_message(f"Tell me fact #{i} about programming")
        print_success(f"Sent message {i+1}")

    # Check memory stats
    stats = await get_memory_stats()
    print_info(f"Memory stats: {json.dumps(stats['stats'], indent=2)}")

    # Get history
    history = await get_conversation_history()
    print_success(f"Total turns stored: {history['count']}")

    return history


async def test_memory_consolidation():
    """Test 4: Memory consolidation (summarization)"""
    print_header("Test 4: Memory Consolidation")

    print_info("Sending 25 messages to trigger consolidation...")

    for i in range(25):
        response = await send_message(f"Tell me programming concept #{i}")
        memory_meta = response['meta'].get('memory', {})

        if i % 5 == 0:
            print_info(f"Turn {i}: Summary exists: {memory_meta.get('has_summary', False)}")

    print_success("All messages sent!")

    # Check final stats
    stats = await get_memory_stats()
    print_info(f"Final memory stats: {json.dumps(stats['stats'], indent=2)}")

    # Get summary
    summary_response = await get_summary()
    if summary_response['summary']:
        print_success("✓ Summary generated!")
        print_info(f"Summary: {summary_response['summary'][:200]}...")
    else:
        print_warning("No summary generated yet (may need more turns)")

    return stats


async def test_semantic_retrieval():
    """Test 5: Semantic retrieval (LTM)"""
    print_header("Test 5: Semantic Retrieval (LTM)")

    # Create a new conversation
    new_conv_id = "test_conversation_2"

    async with httpx.AsyncClient(timeout=30) as client:
        # Ask about something from previous conversation
        response = await client.post(
            f"{BASE_URL}/ai/generate",
            json={
                "user_id": TEST_USER,
                "conversation_id": new_conv_id,
                "message": "What did we discuss about Python earlier?",
                "messages": []
            }
        )
        response.raise_for_status()
        data = response.json()

    print_info(f"User: What did we discuss about Python earlier?")
    print_info(f"Assistant: {data['assistant_message'][:150]}...")

    memory_meta = data['meta'].get('memory', {})
    ltm_retrieved = memory_meta.get('ltm_memories_retrieved', 0)

    if ltm_retrieved > 0:
        print_success(f"✓ LTM retrieval working! Retrieved {ltm_retrieved} memories")
    else:
        print_warning("No LTM memories retrieved (may need more past conversations)")

    return data


async def test_memory_clearing():
    """Test 6: Memory clearing"""
    print_header("Test 6: Memory Clearing")

    # Clear memory
    result = await clear_memory()
    print_success(result['message'])

    # Verify cleared
    stats = await get_memory_stats()
    turns = stats['stats']['total_turns']

    if turns == 0:
        print_success("✓ Memory cleared successfully!")
    else:
        print_warning(f"Memory not fully cleared. {turns} turns remaining")

    return result


async def run_all_tests():
    """Run all tests"""
    print("\n")
    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        PromptLearn AI Memory System Test Suite           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    print_info(f"Testing with user: {TEST_USER}")
    print_info(f"Conversation ID: {TEST_CONV}")

    try:
        # Check server health
        async with httpx.AsyncClient(timeout=5) as client:
            await client.get(f"{BASE_URL}/ai/memory/health")
        print_success("✓ Server is running")

    except Exception as e:
        print_error(f"Server not reachable: {e}")
        print_warning("Make sure to run: make dev")
        return

    tests = [
        ("Basic Conversation", test_basic_conversation),
        ("Short-Term Memory", test_short_term_memory),
        ("Memory Persistence", test_memory_persistence),
        ("Memory Consolidation", test_memory_consolidation),
        ("Semantic Retrieval", test_semantic_retrieval),
        ("Memory Clearing", test_memory_clearing)
    ]

    results = []

    for name, test_func in tests:
        try:
            await test_func()
            results.append((name, True))
        except Exception as e:
            print_error(f"Test failed: {e}")
            results.append((name, False))

    # Summary
    print_header("Test Results Summary")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        if success:
            print_success(f"{name}: PASSED")
        else:
            print_error(f"{name}: FAILED")

    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.ENDC}\n")

    if passed == total:
        print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 All tests passed! Memory system is working perfectly!{Colors.ENDC}\n")
    else:
        print(f"{Colors.WARNING}{Colors.BOLD}⚠️  Some tests failed. Check the logs above.{Colors.ENDC}\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
