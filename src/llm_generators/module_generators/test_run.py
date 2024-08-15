import asyncio
from time import time

from .question_html_generator import question_html_generator
from .server_js_generator import server_js_generator
from .server_py_generator import server_py_generator
from .question_solution_html_generator import question_solution_generator


async def main():
    start_time = time()
    question = "A ball is traveling at a constant speed of 5 m/s along a straight path. The time of travel is 5 minutes. Calculate the total distance."
    print("Generating HTML content for the question...")
    question_html = await question_html_generator.arun(question)
    print("HTML content generated successfully.\n")

    print("Starting asynchronous tasks for server.js, server.py, and solution.html generation...")
    server_js, server_py, solution_html = await asyncio.gather(
        server_js_generator.arun(question_html),
        server_py_generator.arun(question_html),
        question_solution_generator.arun(question_html)
    )

    print("\nAll tasks completed successfully.")
    print("\nGenerated Content:\n")
    print("==== server.js ====")
    print(server_js)
    print("\n==== server.py ====")
    print(server_py)
    print("\n==== solution.html ====")
    print(solution_html)

    print(f"\n Total time {time()-start_time}")

if __name__ == "__main__":
    asyncio.run(main())